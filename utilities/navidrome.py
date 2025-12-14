import logging
import requests
import hashlib
import secrets
import urllib
import http
from utilities.exceptions import FatalError, MultipleArtistsFound, AlbumNotFound, ArtistNotFound, SongNotFound

logger = logging.getLogger(__name__)
http.client.HTTPConnection.debuglevel = 0

class Navidrome:
    "Navidrome things class"

    URL = 'https://music.fargue.net'
    USER = 'jarnold'
    PASSWORD = 'got2fish'
    VERSION = '1.12.0'
    CLIENT = "MediaLib"


    def __init__(self,
                 verbose=False,
                 username=USER,
                 password=PASSWORD,
                 version=VERSION,
                 client=CLIENT):
        self.verbose = verbose
        self.username = username
        self.password = password
        self.version = version
        self.client = client
        self.rating = None
        self.otf_rating = None
        self.artist_id = None
        self.album_id = None
        self.song_id = None

    def send_request(self,action,action_params):
        http.client.HTTPConnection.debuglevel = 0
        salt = secrets.token_hex(8).encode('utf-8')
        hashed_password = hashlib.md5(self.password.encode('utf-8') + salt).hexdigest()
        #logger.info(f'salt: {salt}, user: {self.username}, pass: {self.password}')
        #logger.info(f'hashed pass: {hashed_password}')
        url = f'{self.URL}/rest/{action}'
        payload = {
            'u': self.username,
            't': hashed_password,
            's': salt,
            'v': self.version,
            'c': self.client,
            'f': 'json'
        }
        if action_params:
            for key,value in action_params.items():
                payload[key] = value
        #logger.info('sending payload: {}'.format(payload))
        r = requests.post(url, params=urllib.parse.urlencode(payload))
        r.raise_for_status()
        #logger.info(f'request Url is: {r.url}')
        #logger.info(r.json())
        return r.json()

    def search_artist(self,artist):
        payload = {
            'query': artist.name,
            'albumCount': 0,
            'songCount' : 0
        }
        jsonresp = self.send_request('search2',payload)
        if 'artist' not in jsonresp['subsonic-response']['searchResult2']:
            logger.fatal(f'No Artist not found with name: {artist.name}')
            raise ArtistNotFound(artist.name)
        resp = jsonresp['subsonic-response']['searchResult2']['artist']
        if len(resp) == 1:
            logger.debug(f'Search for artist name: {artist.name} returned one result. That was easy!')
            result = resp[0]
        elif len(resp) == 0:
            logger.fatal(f'Artist not found with name: {artist.name}')
            raise ArtistNotFound(artist.name)
        else:
            logger.debug('Found {} artists with containing name: {}'.
                        format(len(resp),artist.name))
            sfound = False
            for a in resp:
                logger.debug(f'Artist: {a['name']}')
                if a['name'] == artist.name:
                    result = a
                    sfound = True
                    break
            if not sfound:
                logger.fatal(f'Artist with name: {artist.name} not found.')
                raise ArtistNotFound(artist.name)

        result = jsonresp['subsonic-response']['searchResult2']['artist'][0]
        #logger.info(result)
        self.artist_id = result['id']
        return result['id']

    def search_album(self,artist,album):
        payload = {
            'query': album.name,
            'artistCount': 0,
            'albumCount' : 1000,
            'songCount' : 0
        }
        jsonresp = self.send_request('search2',payload)
        if 'album' not in jsonresp['subsonic-response']['searchResult2']:
            logger.fatal(f'No Album not found with name: {album.name}')
            raise AlbumNotFound(artist.name,album.name)

        resp = jsonresp['subsonic-response']['searchResult2']['album']
        #logger.info(resp)
        if len(resp) == 1:
            logger.debug(f'Search for album name: {album.name} returned one result. That was easy')
            result = resp[0]
        elif len(resp) == 0:
            logger.fatal(f'Album with name: {album.name} not found.')
            raise AlbumNotFound(artist.name,album.name)
        else:
            logger.debug('Found {} albums with name: {}'.
                        format(len(resp),album.name))
            sfound = False
            for a in resp:
                logger.debug(f'Artist: {a['artist']}, Album: {a['name']}')
                if a['artist'] == artist.name and a['name'] == album.name:
                    result = a
                    sfound = True
                    break
            if not sfound:
                logger.fatal(f'Album with name: {album.name}, Artist name: {artist.name} not found.')
                raise AlbumNotFound(artist.name,album.name)
        self.album_id = result['id']
        return result['id']

    def search_song(self,artist,album,song):
        payload = {
            'query': song.title,
            'artistCount': 0,
            'albumCount' : 0,
            'songCount': 1000
        }
        jsonresp = self.send_request('search2',payload)
        if 'song' not in jsonresp['subsonic-response']['searchResult2']:
            logger.fatal(f'Song with name: {song.title} not found.')
            raise SongNotFound(artist.name,album.name,song.title)

        resp = jsonresp['subsonic-response']['searchResult2']['song']
        #logger.info(resp)
        if len(resp) == 1:
            logger.debug(f'Search for song name: {song.title} returned one result. That was easy')
            result = resp[0]
        elif len(resp) == 0:
            logger.fatal(f'Song with name: {song.title} not found.')
            raise SongNotFound(artist.name,album.name,song.title)
        else:
            logger.debug('Found {} songs with name: {}'.
                        format(len(resp),song.title))
            sfound = False
            for a in resp:
                logger.debug(f'Artist: {a['artist']}, Album: {a['album']}, Song: {a['title']}')
                if a['artist'] == artist.name and a['album'] == album.name and a['title'] == song.title:
                    result = a
                    sfound = True
                    break
            if not sfound:
                logger.fatal(f'Song with name: {song.title} not found.')
                raise SongNotFound(artist.name,album.name,song.title)

        self.song_id = result['id']
        return result['id']

    def update_artist(self,artist):
        if artist.otf_rating:
            rating = artist.otf_rating
        elif artist.rating:
            rating = round(artist.rating/2)
        else:
            rating = 0
        logger.info(f'Artist: {artist.name} has rating of: {rating}')
        if not artist.navidrome_id:
            logger.debug(f'Need to get navidrome_id for artist name: {artist.name}')
            self.artist_id = self.search_artist(artist)
        else:
            logger.debug(f'Artist Name: {artist.name} has navidrome_id: {artist.navidrome_id}')
            self.artist_id = artist.navidrome_id
        payload = {
            'id': self.artist_id,
            'rating': rating
        }
        jsonresp = self.send_request('setRating',payload)

    def update_album(self,artist,album):
        if album.otf_rating:
            rating = album.otf_rating
        else:
            rating = round(album.rating/2)

        if rating is None:
            logger.info(f'Artist: {artist.name}, Album: {album.name} has no rating')
            return
        logger.info(f'Artist: {artist.name}, Album: {album.name} has rating of: {rating}')

        if not album.navidrome_id:
            logger.debug(f'Need to get navidrome_id for artist name: {artist.name}, album name: {album.name}')
            self.album_id = self.search_album(artist,album)
        else:
            logger.debug(f'Artist Name: {artist.name}, album name: {album.name} has navidrome_id: {album.navidrome_id}')
            self.album_id = artist.navidrome_id
        payload = {
            'id': self.album_id,
            'rating': rating
        }
        jsonresp = self.send_request('setRating',payload)

    def update_song(self,artist,album,song):
        if song.otf_rating:
            rating = song.otf_rating
        else:
            rating = round(song.rating/2)

        if rating is None:
            logger.info(f'Artist: {artist.name}, Album: {album.name}, Song: {song.title} has no rating')
            return
        logger.info(f'Artist: {artist.name}, Album: {album.name}, Song: {song.title} has rating of: {rating}')

        if not song.navidrome_id:
            logger.debug(f'Need to get navidrome_id for artist name: {artist.name}, album name: {album.name}, song name: {song.title}')
            self.song_id = self.search_song(artist,album,song)
        else:
            logger.debug(f'Artist Name: {artist.name}, album name: {album.name}, song name: {song.title} has navidrome_id: {song.navidrome_id}')
            self.song_id = artist.song_id
        payload = {
            'id': self.song_id,
            'rating': rating
        }
        jsonresp = self.send_request('setRating',payload)
