from Utilities import Utilities
from music.artist import Artist
from music.album import Album
import psycopg2
import psycopg2.extras



class Song:
    "Music Song class"

    def __init__(self, utilities, ytmusic, dbh, info=None):
        
        self.u = utilities  # Utilities Object
        self.ytm = ytmusic  # youtube Music API object
        self.dbh = dbh      # database handle
        self.id = None      # pk from database
        self.title = None   # song title
        self.rating = 0     # rating is 0-10
        self.comment = None
        self.release_date = None
        self.release_year = None
        self.arranger = None
        self.bpm = None
        self.track_number = 0
        self.disk_number = 0
        self.score = None
        self.yt_id = None   # id or videoId from youtube music
        self.album = None   # Album object
        self.artists = []   # Array of Artist Objects
        self.yt_like_status = None  # INDIFFERENT, LIKE or DISLIKE
        self.filename = 'NA'
        self.duration = None
        self.media_type_id = 1
        if info:
            if 'dbh' in info:
                self.dbh = info['dbh']
            if 'title' in info:
                self.title = info['title']
            if 'comment' in info:
                self.comment = info['comment']
            if 'release_date' in info:
                self.release_date = info['release_date']
            if 'release_year' in info:
                self.release_date = info['release_year']
            if 'track_number' in info:
                self.track_number = info['track_number']
            if 'rating' in info:
                self.rating = info['rating']

    def print_attributes(self):
        self.u.log('Song:')
        self.u.log('  Title          : {}'.format(self.title))
        for a in self.artists:
            self.u.log('  Artist         : {}'.format(a.name))
            self.u.log('  Artist id      : {}'.format(a.id))
        if self.album:
            self.u.log('  Album Name     : {}'.format(self.album.name))
        self.u.log('  Rating         : {}'.format(self.rating))
        self.u.log('  Release Date   : {}'.format(self.release_date))
        self.u.log('  Duration       : {}'.format(self.duration))
        self.u.log('  YouTube Id     : {}'.format(self.yt_id))
        self.u.log('  YTM Like Status: {}'.format(self.yt_like_status))

    def load_song_from_youtube(self, youtube_song):
        # self.u.pprintd(youtube_song)
        __artist_id = None
        if 'id' in youtube_song:
            self.yt_id = youtube_song['id']
        elif 'videoId' in youtube_song:
            self.yt_id = youtube_song['videoId']
        if 'title' in youtube_song:
            self.title = youtube_song['title']
        if 'artists' in youtube_song:
            for artist in youtube_song['artists']:
                a = Artist(self.u,self.ytm,self.dbh)
                a.load_artist_from_youtube(artist)
                self.artists.append(a)
                if not __artist_id:
                    __artist_id = a.id
        else:
            self.u.log('No artist for song: {}'.format(self.title))
        if 'album' in youtube_song and youtube_song['album']:
            al = Album(self.u,self.ytm,self.dbh,artist_id=artist_id)
            al.load_album_from_youtube(youtube_song['album'])
            al.artist_id = __artist_id
            self.album = al
        else:
            self.u.log('No album for song: {}'.format(self.title))
        if 'rating' in youtube_song:
            self.rating = youtube_song['rating']
        if 'likeStatus' in youtube_song:
            self.yt_like_status = youtube_song['likeStatus']
        if 'duration' in youtube_song:
            self.duration = youtube_song['duration']
        self.query_song()
        self.save()
        self.print_attributes()

    def query_song_by_id(self):
        # query song from db
        if not self.id:
            self.u.log('No id is defined to query song by')
            return
        
        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement="""
            SELECT *
            FROM    medialib.song s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement,(self.id,))
        if c_query.rowcount == 0:
            self.u.log('No song found for id: {}'.format(self.id))
            return
        sdata = c_query.fetchone()
        self.title = sdata['title']
        self.comment = sdata['comment']
        self.release_year = sdata['year']
        self.release_date = sdata['release_date']
        self.track_number = sdata['track_number']
        self.arranger = sdata['arranger']
        self.bpm = sdata['bpm']
        self.rating = sdata['rating']
        self.duration = sdata['duration']
        self.disk_number = sdata['disk_number']
        self.score = sdata['score']
        self.yt_id = sdata['youtube_id']
        self.filename = sdata['filename']
        self.artist_id = sdata['artist_id']
        self.album_id = sdata['album_id']
        self.media_type_id = sdata['media_type_id']

    def query_song(self):
        # query song from db
        if self.id:
            # we have an id. Query by it
            self.query_song_by_id()
            return

        # query by title, artist, album

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    medialib.song s
            WHERE   s.title = %s
            AND     s.artist_id = %s
            AND     s.album_id = %s
        """

        __artist_id = self.artists[0].id
        if self.album and self.album.id:
            __album_id = self.album.id
        else:
            __album_id = 0
        c_query.execute(query_statement, (self.title,__artist_id,__album_id,))
        if c_query.rowcount == 0:
            self.u.log('No song found for id: {}'.format(self.id))
            return
        
        if c_query.rowcount != 1:
            self.u.log('Found multiple songs!')
            return

        sdata = c_query.fetchone()
        self.id = sdata['id']
        self.title = sdata['title']
        self.comment = sdata['comment']
        self.release_year = sdata['year']
        self.release_date = sdata['release_date']
        self.track_number = sdata['track_number']
        self.arranger = sdata['arranger']
        self.bpm = sdata['bpm']
        self.rating = sdata['rating']
        self.duration = sdata['duration']
        self.disk_number = sdata['disk_number']
        self.score = sdata['score']
        self.yt_id = sdata['youtube_id']
        self.filename = sdata['filename']
        self.artist_id = sdata['artist_id']
        self.album_id = sdata['album_id']
        self.media_type_id = sdata['media_type_id']

    def update_db(self):

        __artist_id = None
        for a in self.artists:
            # only support one artist per song right now, we'll store the first one
            if not __artist_id:
                __artist_id = a.id
        if self.album:
            self.album.artist_id = __artist_id
        self.artist_id = __artist_id

        try:
            c_stmt = self.dbh.cursor()
            if self.duration:
                if type(self.duration == 'int'):
                    __duration = self.duration
                else:
                    __duration = self.u.duration_to_seconds(self.duration)
            else:
                __duration = None
            if self.album and self.album.id:
                __album_id = self.album.id
            else:
                __album_id = 0

            update_stmt = """ 
            update medialib.song
                set title = %s,
                    comment = %s,
                    year = %s,
                    release_date = %s,
                    track_number = %s,
                    arranger = %s,
                    bpm = %s,
                    rating = %s,
                    duration = %s,
                    disk_number = %s,
                    score = %s,
                    youtube_id = %s,
                    filename = %s,
                    artist_id = %s,
                    album_id = %s,
                    media_type_id = %s
                where id = %s
            """
            c_stmt.execute(
                update_stmt,
                (self.title, self.comment, self.release_year, self.release_date, self.track_number,
                 self.arranger, self.bpm, self.rating, __duration, self.disk_number, self.score,
                 self.yt_id, self.filename, __artist_id, __album_id, self.media_type_id, self.id
                 )
            )
            self.u.debug('Updated song: {}, id: {}'.format(
                self.title, self.id))
        except (Exception, psycopg2.Error) as error:
            self.u.log('Error updating song: {}'.format(error))
            self.print_attributes()
            raise

        finally:
            c_stmt.close()

    def insert_db(self):

        artist_id = None
        for a in self.artists:
            # only support one artist per song right now, we'll store the first one
            if not artist_id:
                artist_id = a.id
        if self.album:
            self.album.artist_id = artist_id
        self.artist_id = artist_id

        try:
            c_stmt = self.dbh.cursor()
            if self.duration:
                __duration = self.u.duration_to_seconds(self.duration)
            else:
                __duration = None
            if self.album and self.album.id:
                __album_id = self.album.id
            else:
                __album_id = 0


            insert_stmt=""" 
            insert into medialib.song
                ( title, comment, year, release_date, track_number,
                arranger, bpm, rating, duration, disk_number, score,
                youtube_id, filename, artist_id, album_id, media_type_id )
                values
                ( %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s )
                RETURNING id
            """
            c_stmt.execute(
                insert_stmt,
                ( self.title, self.comment, self.release_year, self.release_date, self.track_number,
                self.arranger, self.bpm, self.rating, __duration, self.disk_number, self.score,
                self.yt_id, self.filename, artist_id, __album_id, self.media_type_id
                )
            )
            self.id = c_stmt.fetchone()[0]
            self.u.debug('Inserted song: {} as id: {}'.format(self.title,self.id))
        except (Exception, psycopg2.Error) as error:
            self.u.log('Error inserting song: {}'.format(error))
            self.print_attributes()
            raise 

        finally:
            c_stmt.close()

    def save(self):
        # save song to database
        # query first to see if it exists:
        self.query_song()

        if self.id:
            self.update_db()
        else:
            self.insert_db()
        self.dbh.commit()
