# Spotify-to-Youtube
#### Video Demo: https://youtu.be/KATznR-uDkU
#### Description:

The Spotify to YouTube Playlist Converter is a web application that allows users to convert their Spotify playlists into YouTube playlists easily. Users can login their Spotify account, choose a playlist and the app will generate a corresponding YouTube playlist.

#### Table of Contents
- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Files Description](#files-description)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

#### Features

- Convert Spotify playlists to YouTube playlists
- User-friendly interface
- Error handling for invalid URLs

#### Installation (while in development mode):
1. Clone the repository:
```bash
git clone https://github.com/FelipeFirmida/Spotify-to-Youtube.git
```
2. Navigate to the project directory:
```bash
cd Spotify-to-Youtube
```
3. Install dependencies:
```bash
npm install
```
4. Set up environment variables (this is the hardest part):

You will need to create an app on Spotify Developers page and on Google Cloud API and Services. After creating the APP you will need to set an authorization (on both APIs) for the redirect URLs, so the APIs can trust its your website.

I will link two video guides I used for this part to clarify it.

[Spotify API video](https://www.youtube.com/watch?v=WAmEZBEeNmg)

[Youtube DATA API Video](https://www.youtube.com/watch?v=QY8dhl1EQfI&t=36s)

Create a `.env` file in the root directory and add the following:
```bash
SPOTIFY_CLIENT_ID = your_spotify_client_id
SPOTIFY_CLIENT_SECRET = your_spotify_client_secret
FLASK_S_KEY = your_flask_secret_key
YT_API_KEY = your_youtube_api_key
YT_CLIENT_ID = your_youtube_client_id
YT_CLIENT_SKEY = your_youtube_client_secret_key
```
5. Start the development server:
```bash
npm start
```

6. Or you can also create a clientinfo.py file and import the os.environ library and include the information below:

import os
os.environ['SPOTIFY_CLIENT_ID'] = your_spotify_client_id
os.environ['SPOTIFY_CLIENT_SECRET'] = your_spotify_client_secret
os.environ['FLASK_S_KEY'] = your_flask_secret_key
os.environ['YT_API_KEY'] = your_youtube_api_key
os.environ['YT_CLIENT_ID'] = your_youtube_client_id
os.environ['YT_CLIENT_SKEY'] = your_youtube_client_secret_key

7. After creating the file you should add the line in the app.py file:
```python
import clientinfo # File containing all the info necessary to login the web APP to the Spotify and youtube APIs
```

This will link the file with the sensitive information without leaking them to the public.


#### Usage
1. Open the app in your browser.
2. Click the "Log in to Spotify Button"
3. Log in your Spotify Account and Click Accept.
4. Log in your YouTube Account and Click Continue.
5. Choose the playlist you want to convert from the dropdown menu.
6. Click the "Convert Playlist" button.
7. Wait for the conversion to happen (it may take a couple of minutes - still way faster than doing it manually).
8. After the success page has loaded, go to your YouTube Playlist page and the new Playlist should be there. :)

#### Technologies Used
1. Python
2. Flask
3. Spotify API
4. Spotipy
5. YouTube Data API
6. Google OAUTH 
7. Javascript
8. Bootstrap
9. HTML
10. CSS

#### Files Description

1. app.py

App.py is where all the magic happens. It was made using Python, Flask Framework, Spotipy library, Google.OAuth library. 
I managed the Spotify and YouTube OAuth using the Flask Session and the Spotipy Cache Handler.

2. clientinfo

Holds all the clients key, api keys and secret keys needed to run the app. This file contains sensitive information so its not presented in the github repository.

3. client_secrets.json

Holds all the client secrets needed to use the YouTube Data API.This file contains sensitive information so its not presented in the github repository.

## static/ directory

1. All .png files
All .png files used in the web app and web site were generated using Canva AI (except for the youtube and spotify logos/icons).

2. styles.css
The css file containing all the styles used in all the .html files.

3. script.js
The JavaScript file that was created to show the loading screen when the user clicks the convert playlist button.

## templates/ directory

1. index.html - the home page of the web app.

2. layout.html - the file that contains the basic layout for all the other html files. They were linked using Jinja. I also used bootstrap in the layout to make it easier to build a navbar and a footbar.

3. getPlaylists.html - the page where the user select in a dropdown menu the playlist wanted to be converted.

4. success.html - the page that shows that the playlist was successfuly converted and added to the Youtube playlist.

5. failure.html - the page that shows that something went wrong while converting the playlist.

## flask_session/ directory

Contains all the files related to session infos.


#### Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.

2. Create a new branch:
    ```bash
    git checkout -b feature-branch
    ```
3. Make your changes.

4. Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
5. Push to the branch:
    ```bash
    git push origin feature-branch
    ```
6. Open a pull request.

#### License
This project is licensed under the MIT License.

#### Acknowledgements
- Thanks to [Spotify](https://www.spotify.com/br-en/premium/) for the Spotify API.
- Thanks to [YouTube](https://www.youtube.com/) for the YouTube API.
- Special Thanks to [Harvard's CS50](https://cs50.harvard.edu/) for the course materials and guidance.