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
4. Set up environment variables:
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

#### Usage
1. Open the app in your browser.
2. Click the "Log in to Spotify Button"
3. Log in your Spotify Account and Click Accept.
4. Log in your YouTube Account and Click Continue.
5. Choose the playlist you want to convert from the dropdown menu.
6. Click the "Convert Playlist" button.
7. Wait for the conversion to happen (it may take a couple of minutes).
8. After the success page has loaded, go to your YouTube Playlist page and the your new Playlist should be there. :)

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

App.py is where all the magic happens. It was made using Python, Flask Framework,

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