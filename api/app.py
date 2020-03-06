
import pandas as pd
import numpy as np
import spotipy
from joblib import load
from flask import Flask, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials

def create_app():
    '''
    Create the app, load the model and lookup table, and initiate the spotify client
    '''
    app = Flask(__name__)
    client_credentials_manager = SpotifyClientCredentials(client_id='69d7960353114a25ad479492dd0346eb', client_secret='6190f3b487b448d6b0d8340c01baf3ab')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    nn = load('static/spotify2.joblib')
    id_map = np.array(pd.read_csv('static/IDS2.csv')).reshape(1,-1)[0]
    data = pd.read_csv('static/train.csv').values
    features = ['danceability',
                'energy',
                'key',
                'loudness',
                'mode',
                'speechiness',
                'acousticness',
                'instrumentalness',
                'liveness',
                'valence',
                'tempo']
    @app.route('/', methods=['GET'])
    def index():
        return 'Hi'

    @app.route('/song', methods=['GET'])
    def song_info():
        '''
        This route formats user input, uses it to find the song in the 
        spotify api, then returns information about it as a json object
        '''
        title = request.args.get('title')
        artist = request.args.get('artist')

        song = sp.search(f'{title} {artist}', type='track', limit=1)
        info = {'id': song['tracks']['items'][0]['id'],
                'title': song['tracks']['items'][0]['name'],
                'artist': song['tracks']['items'][0]['artists'][0]['name'],
                'album': song['tracks']['items'][0]['album']['name']
                }
        return jsonify(info)

    @app.route('/suggestions', methods=['GET'])
    def suggest():
        '''
        This endpoint take a user inputted song/artist, retrieves the audio features for 
        the input song from the spotify api, preprocesses the data input, and retrieves the
        predictions from our nearest neighbors model.
        '''
        # Use the input to retrieve the song id from spotify
        title = request.args.get('title')
        artist = request.args.get('artist')
        song = sp.search(f'{title} {artist}', type='track', limit=1)
        try:
            song_id = song['tracks']['items'][0]['id']
        except:
            # Return error message if the song is not on spotify
            return("Sorry, we couldn't find the song you're looking for.")
        else:
            # Query the input song's audio features 
            song_features = sp.audio_features(song_id)[0]
            x = np.array([song_features[feature] for feature in features]).reshape(1,-1)
            # Preprocess the input data
            x[0][2] = x[0][2]/11
            x[0][3] = x[0][3]/58.882
            x[0][10] = x[0][10]/249.983
            # Get the predictions from the model
            ids = nn.kneighbors(x)[1][0]
            # Map predictions to their spotify id
            ids = [id_map[id] for id in ids]
            # Retrieve the song information and audio features, return them as a json object
            s = sp.tracks(ids)
            s = [s['tracks'][ind] for ind in range(len(s['tracks']))]
            s = [{'title': t['name'],
                  'artist': t['artists'][0]['name'],
                  'album': t['album']['name'],
                  'image': t['album']['images'][1]['url']}for t in s]
            af = sp.audio_features(ids)
            af = [{feat:af[ind][feat]/(song_features[feat]+.0001) for feat in features} for ind in range(len(af))]
            suggestions = {'song': song, 'tracks':[{'info':s[ind], 'features':af[ind]} for ind in range(len(af))]}
            return jsonify(suggestions)

    @app.route('/least', methods=['GET'])
    def least():
        '''
        This endpoint takes user input, and processes it in order
        to return the least similar song from out model
        '''
        # Retrieve the song features
        title = request.args.get('title')
        artist = request.args.get('artist')
        song = sp.search(f'{title} {artist}', type='track', limit=1)
        try:
            song_id = song['tracks']['items'][0]['id']
        except:
            return("Sorry, we couldn't find the song you're looking for.")
        else:
            song_features = sp.audio_features(song_id)[0]
            x = np.array([song_features[feature] for feature in features]).reshape(1,-1)
            # Preprocess the input
            x[0][2] = x[0][2]/11
            x[0][3] = x[0][3]/58.882
            x[0][10] = x[0][10]/249.983
            
            # calculate the distances between input song and training data
            def distancify(row_of_data):
                return np.linalg.norm(x - row_of_data)

            distances = np.apply_along_axis(distancify, axis=1, arr=data)

            index_least_similar_song = np.where(distances == np.amax(distances))[0][0]

            id_least = id_map[index_least_similar_song]
            #return the information of the least similar song
            s = sp.track(id_least)
            s = {'title': s['name'],
                 'artist': s['artists'][0]['name'],
                 'album': s['album']['name'],
                 'image': s['album']['images'][1]['url']}
            return jsonify(s)
    return app