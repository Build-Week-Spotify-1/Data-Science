
import pandas as pd
import numpy as np
import spotipy
from joblib import load
from flask import Flask, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials

def create_app():
    app = Flask(__name__)
    client_credentials_manager = SpotifyClientCredentials(client_id='69d7960353114a25ad479492dd0346eb', client_secret='6190f3b487b448d6b0d8340c01baf3ab')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    nn = load('static/spotify2.joblib')
    id_map = np.array(pd.read_csv('static/IDS2.csv')).reshape(1,-1)[0]
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
        '''This route returns details about the specified song'''
        title = request.args.get('title')
        artist = request.args.get('artist')

        song = sp.search(f'{title} {artist}', type='track', limit=1)
        info = {'title': song['tracks']['items'][0]['name'],
                'artist': song['tracks']['items'][0]['artists'][0]['name'],
                'album': song['tracks']['items'][0]['album']['name']
                }
        return jsonify(info)

    @app.route('/suggestions', methods=['GET'])
    def suggest():

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
            x[0][2] = x[0][2]/11
            x[0][3] = x[0][3]/58.882
            x[0][10] = x[0][10]/249.983
            ids = nn.kneighbors(x)[1][0]
            ids = [id_map[id] for id in ids]
            s = sp.tracks(ids)
            s = [s['tracks'][ind] for ind in range(len(s['tracks']))]
            s = [{'title': t['name'],
                  'artist': t['artists'][0]['name'],
                  'album': t['album']['name'],
                  'image': t['album']['images'][1]['url']}for t in s]
            af = sp.audio_features(ids)
            af = [{feat:af[ind][feat]/(song_features[feat]+.0001) for feat in features} for ind in range(len(af))]
            suggestions = {'tracks':[{'info':s[ind], 'features':af[ind]} for ind in range(len(af))]}
            return jsonify(suggestions)
    return app