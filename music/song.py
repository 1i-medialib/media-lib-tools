from utilities.gen import Gen
from music.artist import Artist
from music.album import Album
import psycopg2
import psycopg2.extras
import os
import logging
from mediafile import MediaFile
import mutagen
from mutagen.id3 import ID3, POPM, TXXX, TCON
from utilities.exceptions import FileTypeIgnore, UnhandledFileType

logger = logging.getLogger(__name__)

class Song:
    "Music Song class"

    def __init__(self, ytmusic, dbh,
            file_name=None,
            play_count=0,
            release_date=None,
            release_year=None,
            rating=0,
            track_number=None,
            plex_id=None
            ):
        
        self.gen = Gen()
        self.ytm = ytmusic              # youtube Music API object
        self.dbh = dbh                  # database handle
        self.id = None                  # pk from database
        self.album = None               # Album object
        self.album_artist = None
        self.album_artist_sort = None
        self.arranger = None
        self.art = None
        self.artists = []               # Array of Artist Objects
        self.artist_sort = None
        self.bit_rate = None
        self.bpm = None
        self.channels = None
        self.clementinerating = None
        self.comment = None
        self.comp = None
        self.composer = None
        self.country = None
        self.disk_number = 0
        self.disk_total = 0
        self.format = None
        self.duration = None
        self.genre = None
        self.genres = []
        self.grouping = None
        self.images = None
        self.label = None
        if file_name:
            self.filename = file_name      # file name and path for song
        else:
            self.filename = None
        self.lyrics = None
        self.media_type_id = 1
        self.play_count = play_count
        self.plex_id = plex_id
        self.rating = rating
        self.release_date = release_date
        self.release_year = release_year
        self.score = 0
        self.title = None
        self.track_number = None

        self.yt_id = None   # id or videoId from youtube music
        self.yt_like_status = None  # INDIFFERENT, LIKE or DISLIKE
        if self.filename:
            logger.debug('working with file: {}'.format(self.filename))
            self.file_extension = (os.path.splitext(self.filename)[1][1:]).lower()
            # TODO: store media_type_id from ext
            logger.debug('File Extension of {} is {}'.format(self.filename, self.file_extension))
            # still need to use mutagen to get some fields
            if self.file_extension == 'ogg':
                self.handle_ogg()
            elif self.file_extension == 'flac':
                self.handle_flac()
            elif self.file_extension == 'm4a' or self.file_extension == 'mp4':
                self.handle_mp4()
            elif self.file_extension == 'wav':
                self.handle_wav()
            elif self.file_extension == 'mp3':
                self.read_tag_data()
            elif self.file_extension == 'png':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'nfo':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'jpg':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'db':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'm3u':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'log':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'txt':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'sfv':
                raise FileTypeIgnore(self.file_extension)
            elif self.file_extension == 'cue':
                raise FileTypeIgnore(self.file_extension)
            else:
                logger.warning('unsupported file type: {}'.format(self.file_extension))
                raise UnhandledFileType(self.file_extension)

        # only print if debug level
        if logging.root.level == logging.DEBUG:
            self.print_attributes()



    def print_attributes(self):
        logger.warning('Song:')
        logger.warning('  Title               : {}'.format(self.title))
        logger.warning('  File Name           : {}'.format(self.filename))
        for a in self.artists:
            logger.warning('  Artist              : {}'.format(a.name))
            logger.warning('  Artist id           : {}'.format(a.id))
        if self.album:
            logger.warning('  Album Name          : {}'.format(self.album.name))
            logger.warning('  Album id            : {}'.format(self.album.id))
        logger.warning('  Rating              : {}'.format(self.rating))
        logger.warning('  Release Date        : {}'.format(self.release_date))
        logger.warning('  Duration            : {}, type {}'.format(self.duration,type(self.duration).__name__))
        logger.warning('  YouTube Id          : {}'.format(self.yt_id))
        logger.warning('  YTM Like Status     : {}'.format(self.yt_like_status))
        logger.warning('  Score/Popularimeter : {}'.format(self.score))
        logger.warning('  Comment             : {}'.format(self.comment))
        if self.play_count:
            logger.warning('  Play Count          : {}'.format(self.play_count))

    def read_tag_data(self):
        f = MediaFile(self.filename)
        self.id3 = ID3(self.filename)

        if f.albumartist:
            self.album_artist = f.albumartist
        if f.albumartist_sort:
            self.album_artist_sort = f.albumartist_sort
        if f.arranger:
            self.arranger = f.arranger
        self.art = f.art
        if f.artist:
            a = Artist(self.ytm,self.dbh,name=f.artist)
            a.query_artist()
            if not a.id:
                a.insert_db()
            self.artists.append(a)
        self.artist_sort = f.artist_sort

        if f.album:
            al = Album(ytmusic=self.ytm,
                       dbh=self.dbh,
                       name=f.album,
                       artist_id=self.artists[0].id)
            al.query_album()
            if not al.id:
                logger.debug('couldn\'t find an album')
                al.insert_db()
            else:
                logger.debug('found an album: {}'.format(al.id))
            self.album = al

        self.bitrate = f.bitrate
        self.bpm = f.bpm
        self.channels = f.channels
        self.comment = f.comments
        self.comp = f.comp
        self.composer = f.composer
        self.country = f.country
        self.release_date = f.date
        self.disk_number = f.disc
        self.disc_total = f.disctotal
        self.format = f.format
        self.genre = f.genre
        self.genres = f.genres
        self.grouping = f.grouping
        self.images = f.images
        self.label = f.label
        self.language = f.language
        self.duration = f.length
        self.lyricist = f.lyricist
        self.lyrics = f.lyrics
        self.samplerate = f.samplerate
        self.title = f.title
        self.track_number = f.track
        self.tracktotal = f.tracktotal
        self.release_year = f.year
        #self. = f.

        self.popularimeter = self.id3.getall('POPM')
        if self.popularimeter:
            logger.debug('popularimeter is type: {}'.format(type(self.popularimeter)))
            logger.debug('popularimeter is: {}'.format(self.popularimeter))
            if hasattr(self.popularimeter[0],'count'):
                pcount = self.popularimeter[0].count
            else:
                pcount = 0
            logger.debug('popularimeter- email: {}, rating: {}, count: {}'.
                  format(
                      self.popularimeter[0].email,
                      self.popularimeter[0].rating,
                      pcount
                  )
                  )
        __as = self.id3.getall('TXXX:FMPS_Rating_Amarok_Score')
        if __as:
            self.amarokscore = (__as[0].text)[0]
            logger.debug('amarokscore is {}'.format(self.amarokscore))

        __pc = self.id3.getall('TXXX:FMPS_PlayCount')
        if __pc:
            self.play_count = (__pc[0].text)[0]
            logger.debug('play_count is {}'.format(self.play_count))

        __rt = self.id3.getall('TXXX:FMPS_Rating')
        if __rt:
            self.clementinerating = (__rt[0].text)[0]
            logger.debug('clementinerating is {}'.format(
                self.clementinerating))

        if not self.rating:
            self.set_master_rating()

    def get_tag_value(self, data, key):
        logger.debug('looking for key {} in data: {}'.format(key,data))
        value = data.get(key)
        if not value:
            return None
        if type(value).__name__ == 'list':
            logger.debug('Need to convert value to string from list')
            __estr = " "
            rval = __estr.join(value)
        else:
            rval = value

        logger.debug(f'Tag key: {key}, value: {rval}')
        return rval

    def handle_flac(self):
        from mutagen.flac import FLAC
        __audio = FLAC(self.filename)

        logger.debug('Flac Tags:')
        logger.debug(__audio.tags)
        self.bit_rate = __audio.info.bitrate
        self.duration = __audio.info.length
        self.title = self.get_tag_value(__audio.tags, 'TITLE')

        __artist = self.get_tag_value(__audio.tags, 'ARTIST')
        logger.debug('flac artist is {}, type: {}'.format(
            __artist, type(__artist)))
        if __artist:
            a = Artist(self.ytm, self.dbh, name=__artist)
            a.query_artist()
            if not a.id:
                a.insert_db()
            self.artists.append(a)

        __album = self.get_tag_value(__audio.tags, 'ALBUM')
        if __album:
            al = Album(ytmusic=self.ytm,
                       dbh=self.dbh,
                       name=__album,
                       artist_id=self.artists[0].id)
            al.query_album()
            if not al.id:
                logger.debug('couldn\'t find an album')
                al.insert_db()
            else:
                logger.debug('found an album: {}'.format(al.id))
            self.album = al

        self.album_artist = self.get_tag_value(__audio.tags, 'ALBUMARTIST')
        # if ORIGINALDATE has value use it, otherwise use DATE
        __date = self.get_tag_value(__audio.tags, 'ORIGINALDATE')
        if not __date or __date == '0000':
            __date = self.get_tag_value(__audio.tags, 'DATE')
        if __date:
            self.release_date = self.gen.convert_date(__date)
        self.track_number = self.get_tag_value(__audio.tags, 'TRACK')
        self.genre = self.get_tag_value(__audio.tags, 'GENRE')
        self.comments = self.get_tag_value(__audio.tags, 'COMMENT')
        self.lyrics = self.get_tag_value(__audio.tags, 'LYRICS')
        self.rating = self.get_tag_value(__audio.tags, 'FMPS_RATING')
        logger.debug('Rating: {}, type: {}'.format(self.rating,type(self.rating)))
        if self.rating == '':
            self.rating = 0
        elif self.rating is None:
            self.rating = 0
        elif( type(self.rating) == "list" ):
            self.rating = float(self.rating[0]) * 10
        else:
            self.rating = float(self.rating) * 10

    def handle_mp4(self):
        try:
            mf = mutagen.File(self.filename)
        except Exception:
            return
        if mf is None:
            return

        #logger.debug('mp4 Tags:')
        #logger.debug(mf)

        self.bit_rate = mf.info.bitrate
        self.duration = mf.info.length

        # get title
        if '©nam' in mf:
            self.title = mf['©nam'][0]
        if '©ART' in mf:
            __artist = mf['©ART'][0]
            if __artist:
                a = Artist(self.ytm, self.dbh, name=__artist)
                a.query_artist()
                if not a.id:
                    a.insert_db()
                self.artists.append(a)
        if 'tmpo' in mf:
            self.bpm = mf['tmpo'][0]
        if '©alb' in mf:
            __album = mf['©alb'][0]
            if __album:
                al = Album(ytmusic=self.ytm,
                           dbh=self.dbh,
                           name=__album,
                           artist_id=self.artists[0].id)
                al.query_album()
                if not al.id:
                    al.insert_db
                self.album = al
        if 'aART' in mf:
            self.album_artist = mf['aART']
        if '©day' in mf:
            self.release_date = self.gen.convert_date(mf['©day'][0])
        if '©cmt' in mf:
            self.comment = mf['©cmt']
        if '©gen' in mf:
            self.genre = mf['©gen']
        if '©lyr' in mf:
            self.lyrics = mf['©lyr']
        if '©wrt' in mf:
            self.composer = mf['©wrt']
        if '----:com.apple.iTunes:FMPS_Playcount' in mf:
            self.play_count = int(mf['----:com.apple.iTunes:FMPS_Playcount'][0])
        if '----:com.apple.iTunes:FMPS_Rating' in mf:
            self.rating = int(float(mf['----:com.apple.iTunes:FMPS_Rating'][0]) * 10)
        if '----:com.apple.iTunes:FMPS_Rating_Amarok_Score' in mf:
            self.score = int(
                float(mf['----:com.apple.iTunes:FMPS_Rating_Amarok_Score'][0])*100)

    def handle_wav(self):
        "used mutagen.wave. Docs: https://mutagen.readthedocs.io/en/latest/api/wave.html"
        """
        Sample tags:
            'TALB': Album
            'TPE1': Lead Artist/Performer/Soloist/Group
            'TPE2': Band/Orchestra/Accompaniment
            'TCON': Genre, Example: text=['Blues Rock;Southern Rock']),
            'TIT2': Title? Example: text=['Get On With Your Life']),
            'TRCK': Track Number text=['5/8']),
            'TPUB': Publisher text=['Epic']),
            'POPM:MusicBee': POPM(email='MusicBee', rating=40),
            'TPOS': Part of set. Example: text=['1/1']
            'TMED': Medium text=['CD']),
            'TDRC': Recording Time text=['1991-07-02']),
            'TDOR': Original Release Time text=['1991'])
        """
        from mutagen.wave import WAVE
        logger.debug('reading wav file: {}'.format(self.filename))
        __audio = WAVE(self.filename)

        for t in __audio.tags:
            if 'APIC' in t:
                continue
            logger.debug('Tag: {}, value: {}'.format(t,__audio.tags[t]))

        __artist = self.get_tag_value(__audio.tags, 'TPE1').text[0]
        if not __artist:
            __artist = self.get_tag_value(__audio.tags, 'TPE2').text[0]

        logger.debug('wav artist is {}, type: {}'.format(__artist, type(__artist)))
        if __artist:
            a = Artist(self.ytm, self.dbh, name=__artist)
            a.query_artist()
            if not a.id:
                a.insert_db()
            self.artists.append(a)

        __album = self.get_tag_value(__audio.tags, 'TALB').text[0]
        if __album:
            al = Album( ytmusic=self.ytm,
                        dbh=self.dbh,
                        name=__album,
                        artist_id=self.artists[0].id)
            al.query_album()
            if not al.id:
                al.insert_db
            self.album = al

        self.album_artist = self.get_tag_value(__audio.tags, 'TPE1').text[0]
        self.title = self.get_tag_value(__audio.tags, 'TIT2').text[0]
        __date = str(self.get_tag_value(__audio.tags, 'TDRC').text[0])
        if __date:
            logger.debug('date: {}, type: {}'.format(__date,type(__date)))
            if len(__date) == 4:
                self.release_year = __date
            else:
                self.release_date = __date
        __track_number = self.get_tag_value(__audio.tags, 'TRCK').text[0]
        if '/' in __track_number:
            # value is x/y (track x of y). We only want x
            self.track_number = __track_number.split('/')[0]
        self.genre = self.get_tag_value(__audio.tags, 'TCON').text[0]
        self.comments = self.get_tag_value(__audio.tags, 'COMM')
        self.lyrics = self.get_tag_value(__audio.tags, 'USLT')
        __mb_rating = self.get_tag_value(__audio.tags, 'POPM:MusicBee')
        if __mb_rating:
            logger.debug('rating: {}'.format(__mb_rating.rating))
            self.rating = __mb_rating.rating
        else:
            self.rating = self.get_tag_value(__audio.tags, 'POPM')
            if self.rating == '':
                self.rating = 0
            else:
                self.rating = int(float(self.rating[0]) * 10)

    def handle_ogg(self):
        from mutagen.oggvorbis import OggVorbis
        logger.debug('reading ogg file: {}'.format(self.filename))
        __audio = OggVorbis(self.filename)

        logger.debug(__audio.tags)
        self.bit_rate = __audio.info.bitrate
        self.duration = __audio.info.length
        self.title = self.get_tag_value(__audio.tags, 'TITLE')

        __artist = self.get_tag_value(__audio.tags, 'ARTIST')
        logger.error('ogg artist is {}, type: {}'.format(__artist, type(__artist)))
        if __artist:
            a = Artist(self.ytm, self.dbh, name=__artist)
            a.query_artist()
            if not a.id:
                a.insert_db()
            self.artists.append(a)


        __album = self.get_tag_value(__audio.tags, 'ALBUM')
        if __album:
            al = Album( ytmusic=self.ytm,
                        dbh=self.dbh,
                        name=__album,
                        artist_id=self.artists[0].id)
            al.query_album()
            if not al.id:
                al.insert_db
            self.album = al

        self.album_artist = self.get_tag_value(__audio.tags, 'ALBUMARTIST')

        __date = self.get_tag_value(__audio.tags, 'DATE')
        if __date:
            if len(__date) == 4:
                self.release_year = __date
            else:
                self.release_date = __date
        self.track_number = self.get_tag_value(__audio.tags, 'TRACK')
        self.genre = self.get_tag_value(__audio.tags, 'GENRE')
        self.comments = self.get_tag_value(__audio.tags, 'COMMENT')
        self.lyrics = self.get_tag_value(__audio.tags, 'LYRICS')
        self.rating = self.get_tag_value(__audio.tags, 'FMPS_RATING')
        if self.rating == '':
            self.rating = 0
        else:
            self.rating = int(float(self.rating[0]) * 10)


    def set_master_rating(self):
        # if clementinerating: (value * 10)
        # elsif popularimeter: value/51
        # else 0
        if self.clementinerating:
            self.rating = int(float(self.clementinerating) * 10)
        elif self.popularimeter and self.popularimeter[0].rating:
            # TODO: create a map
            # 255 - 5 stars
            # 242 - 4.5
            # 196 - 4
            # 186 = 3.5
            # 128 - 3
            # 118 - 2.5
            # 64 = 2 
            # 54 - 1.5
            # 1 - 1
            # 13 - .0
            # 0 - 0
            if self.popularimeter[0].rating == 0:
                self.rating = 0
            elif self.popularimeter[0].rating == 13:
                self.rating = .5
            elif self.popularimeter[0].rating == 1:
                self.rating = 1
            elif self.popularimeter[0].rating == 54:
                self.rating = 1.5
            elif self.popularimeter[0].rating == 64:
                self.rating = 2
            elif self.popularimeter[0].rating == 118:
                self.rating = 2.5
            elif self.popularimeter[0].rating == 128:
                self.rating = 3
            elif self.popularimeter[0].rating == 186:
                self.rating = 3.5
            elif self.popularimeter[0].rating == 196:
                self.rating = 4
            elif self.popularimeter[0].rating == 242:
                self.rating = 4.5
            elif self.popularimeter[0].rating == 255:
                self.rating = 5
            elif self.popularimeter[0].rating > 10:
                logger.error('Rating is > 10')
                raise ValueError
            else:
                self.rating = self.popularimeter[0].rating
        else:
            self.rating = 0

        logger.debug('Set master rating: {}'.format(self.rating))

    def load_song_from_youtube(self, youtube_song):
        # logger.pprintd(youtube_song)
        __artist_id = None
        if 'id' in youtube_song:
            self.yt_id = youtube_song['id']
        elif 'videoId' in youtube_song:
            self.yt_id = youtube_song['videoId']
        if 'title' in youtube_song:
            self.title = youtube_song['title']
        if 'artists' in youtube_song:
            for artist in youtube_song['artists']:
                a = Artist(self.ytm,self.dbh)
                a.load_artist_from_youtube(artist)
                self.artists.append(a)
                if not __artist_id:
                    __artist_id = a.id
        else:
            logger.debug('No artist for song: {}'.format(self.title))
        if 'album' in youtube_song and youtube_song['album']:
            al = Album(self.ytm,self.dbh,artist_id=__artist_id)
            al.load_album_from_youtube(youtube_song['album'])
            al.artist_id = __artist_id
            self.album = al
        else:
            logger.debug('No album for song: {}'.format(self.title))
        if 'rating' in youtube_song:
            self.rating = youtube_song['rating']
        if 'likeStatus' in youtube_song:
            self.yt_like_status = youtube_song['likeStatus']
        if 'duration' in youtube_song:
            self.duration = youtube_song['duration']
        self.query_song()
        self.save()
        # only print if debug level
        if logging.root.level == logging.DEBUG:
            self.print_attributes()

    def query_song_by_id(self):
        # query song from db
        if not self.id:
            logger.debug('No id is defined to query song by')
            return
        
        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement="""
            SELECT *
            FROM    song s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement,(self.id,))
        if c_query.rowcount == 0:
            logger.debug('No song found for id: {}'.format(self.id))
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
        if not self.filename:
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
            FROM    song s
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
            logger.debug('No song found for id: {}'.format(self.id))
            return
        
        if c_query.rowcount != 1:
            logger.warn('Found multiple songs!')
            self.print_attributes()
            return

        sdata = c_query.fetchone()
        self.id = sdata['id']
        self.title = sdata['title']
        if not self.comment:
            self.comment = sdata['comment']
        if not self.release_year:
            self.release_year = sdata['year']
        if not self.release_date:
            self.release_date = sdata['release_date']
        if not self.track_number:
            self.track_number = sdata['track_number']
        if not self.arranger:
            self.arranger = sdata['arranger']
        if not self.bpm:
            self.bpm = sdata['bpm']
        if not self.rating:
            self.rating = sdata['rating']
        if not self.duration:
            self.duration = sdata['duration']
        if not self.disk_number:
            self.disk_number = sdata['disk_number']
        if not self.score:
            self.score = sdata['score']
        self.yt_id = sdata['youtube_id']
        if not self.filename:
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
                __duration = self.gen.duration_to_seconds(self.duration)
            else:
                logger.debug('Song has no duration')
                __duration = None
            if self.album and self.album.id:
                __album_id = self.album.id
            else:
                __album_id = 0

            logger.debug('Album Id is {}'.format(__album_id))

            update_stmt = """ 
            update song
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
            logger.debug('Updated song: {}, id: {}'.format(
                self.title, self.id))
        except (Exception, psycopg2.Error) as error:
            logger.error('Error updating song: {}'.format(error))
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
                __duration = self.gen.duration_to_seconds(self.duration)
            else:
                __duration = None
            if self.album and self.album.id:
                __album_id = self.album.id
            else:
                __album_id = 0

            insert_stmt=""" 
            insert into song
                ( title, comment, year, release_date, track_number,
                arranger, bpm, rating, duration, disk_number, score, youtube_like_status,
                youtube_id, filename, artist_id, album_id, media_type_id )
                values
                ( %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s )
                RETURNING id
            """
            c_stmt.execute(
                insert_stmt,
                ( self.title, self.comment, self.release_year, self.release_date, self.track_number,
                  self.arranger, self.bpm, self.rating, __duration, self.disk_number, self.score, self.yt_like_status,
                self.yt_id, self.filename, artist_id, __album_id, self.media_type_id
                )
            )
            self.id = c_stmt.fetchone()[0]
            logger.debug('Inserted song: {} as id: {}'.format(self.title,self.id))
        except (Exception, psycopg2.Error) as error:
            logger.error('Error inserting song: {}'.format(error))
            self.print_attributes()
            raise 

        finally:
            c_stmt.close()

    def save(self):
        # save song to database
        # query first to see if it exists:
        self.query_song()

        if self.id:
            logger.debug('Updating song')
            self.update_db()
        else:
            logger.debug('Inserting song')
            self.insert_db()
        self.dbh.commit()
