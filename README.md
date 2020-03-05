# Spotify Song Suggester
This project is part of the LambdaSchool Build week March 2020

# Project Objective
The Song Suggester has two functionalities on the DataScience side:

* Given a song chosen by the user the API will return the 6 most similar songs from a database of over 300.000 songs.
* Given a song chosen by the user the API will return the least similar song. (DS-part ready for deployment)

# Methods Used 

* knn

# Python 3.7 Libraries 

* Pandas
* Joblib
* flask
* Numpy
* sklearn

# Setup

* The trained model is under static
* The train data aswell

# Notebook: Knn_and_least_similar_song

*  Points 1 - 3 document the steps that were taken to create the training data of the model
*  Points 4 -8 demonstrate the training of the knn-model and testing it by using the spotipy-api to generate input.
*  Point 9 shows the least similar song search using Numpy. 
*  Point 10 holds the code to get a 30 second demo of a song via the spotipy api. 
*  Point 11 contains a short discussion why we chose Knn and did not opt for a neural net.

# API

The DS api for this project has 3 endpoints 

* [spotify-suggestor.herokuapp.com/song?title=&artist=] (returns information about the song)
* [spotify-suggestor.herokuapp.com/suggestions?title=&artist=] (returns 6 most similar songs, along with data for graphing)
* [spotify-suggestor.herokuapp.com/least?title=&artist=] (returns least similar song)

Url Parameters: title (song title) artist (artist)

Results will be returned as long as one of the parameters is entered, and is a valid artist name/song title

User input is sent to the spotify api in order to retrieve correct song info and audio features
