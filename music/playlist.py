from Utilities import Utilities
from music.song import Song


class Playlist:
    "Music Playlist class"

    def __init__(self, utilities, ytmusic, dbh, info=None):
        self.u = utilities  # Utilities Object
        self.ytm = ytmusic  # youtube Music API object
        self.dbh = dbh     # database handle
        self.id = None      # pk from database

        self.name = None
        self.rating = 0
        self.description = None
        self.track_count = 0
        self.songs = []
        self.yt_id = None
        if info:
            if 'name' in info:
                self.name = info['name']
            if 'description' in info:
                self.description = info['description']
            if 'trackCount' in info:
                self.track_count = int(info['trackCount'])
            if 'songs' in info:
                self.songs = info['songs']
            if 'rating' in info:
                self.rating = int(info['rating'])

    def print_attributes(self):
        self.u.log('Playlist:')
        self.u.log('  Name       : {}'.format(self.name))
        self.u.log('  Rating     : {}'.format(self.rating))
        self.u.log('  Track Count: {}'.format(self.track_count))

    def get_songs_from_youtube_playlist_id(self):
        if not self.yt_id:
            self.u.log('No yt id set')
            return
        
        pl = self.ytm.get_playlist(self.yt_id, limit=(self.track_count + 1))
        for track in pl['tracks']:
            s = Song(self.u,self.ytm,self.dbh)
            s.load_song_from_youtube(track)
            self.songs.append(s)


    def load_playlist_from_youtube(self, youtube_playlist):
        # self.u.pprintd(youtube_playlist)

        if 'id' in youtube_playlist:
            self.yt_id = youtube_playlist['id']
        elif 'playlistId' in youtube_playlist:
            self.yt_id = youtube_playlist['playlistId']
        if 'title' in youtube_playlist:
            self.name = youtube_playlist['title']
        if 'description' in youtube_playlist:
            self.description = youtube_playlist['description']
        if 'trackCount' in youtube_playlist:
            self.track_count = int(youtube_playlist['trackCount'])
        elif 'count' in youtube_playlist:
            self.track_count = int(youtube_playlist['count'])
        if 'tracks' in youtube_playlist:
            self.songs = youtube_playlist['tracks']
        else:
            # get songs from pl
            self.get_songs_from_youtube_playlist_id()
        self.print_attributes()

    def save(self):
        # save items in the playlist to db
        self.u.debug('Saving playlist: {}'.format(self.name))
        # iterate songs and save
        for song in self.songs:
            self.u.debug('Saving song: {}'.format(song.title))
            song.save()
