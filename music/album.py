from music.artist import Artist
import logging
import psycopg2
import psycopg2.extras
from utilities.navidrome import Navidrome
from utilities.exceptions import FatalError, AlbumNotFound

logger = logging.getLogger(__name__)

class Album:
    "Music Album class"

    def __init__(self, ytmusic, dbh, name=None, artist_id=None, release_date=None,
                 release_year=None, number_of_disks=0, track_count=0, rating=0):
        self.ytm = ytmusic  # youtube Music API object
        self.dbh = dbh      # database handle
        self.id = None      # pk from database

        self.name = name
        self.artist_id = artist_id
        self.release_date = release_date
        self.release_year = release_year
        self.number_of_disks = number_of_disks
        self.track_count = track_count
        self.otf_rating = round(rating,0)
        self.rating = rating
        self.yt_id = None
        self.navidrome_id = None

    def print_attributes(self):
        logger.warning('Album:')
        logger.warning('  Name       : {}'.format(self.name))
        logger.warning('  ID         : {}'.format(self.id))
        logger.warning('  Artist Id  : {}'.format(self.artist_id))
        logger.warning('  Rating     : {}'.format(self.rating))
        logger.warning('  Track Count: {}'.format(self.track_count))
        logger.warning('  YouTube ID : {}'.format(self.yt_id))

    def load_album_from_youtube(self, youtube_album):
        #ulogger.pprintd(youtube_album)
        if 'id' in youtube_album:
            self.yt_id = youtube_album['id']
        if 'name' in youtube_album:
            self.name = youtube_album['name']
        if 'release_date' in youtube_album:
            self.release_date = youtube_album['release_date']
        if 'release_year' in youtube_album:
            self.release_date = youtube_album['release_year']
        if 'number_of_disks' in youtube_album:
            self.number_of_disks = youtube_album['number_of_disks']
        if 'rating' in youtube_album:
            self.rating = youtube_album['rating']
        self.query_album()
        self.save()
        # only print if debug level
        if logging.root.level == logging.DEBUG:
            self.print_attributes()

    def query_album_by_id(self):
        # query album from db
        if not self.id:
            logger.warning('No id is defined to query album by')
            return
        logger.debug(f'Querying album by id: {self.id}')

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    album s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement,(self.id,))
        if c_query.rowcount == 0:
            logger.debug('No album found for id: {}'.format(self.id))
            return
        sdata = c_query.fetchone()
        self.name = sdata['name']
        self.artist_id = sdata['artist_id']
        self.release_date = sdata['release_date']
        self.release_year = sdata['release_year']
        self.number_of_disks = sdata['number_of_disks']
        self.track_count = sdata['track_count']
        self.rating = sdata['rating']
        self.yt_id = sdata['youtube_id']
        if sdata['navidrome_id']:
            self.navidrome_id = sdata['navidrome_id']
        else:
            n = Navidrome()  
            logger.debug(f'Querying navidrome for album name: {self.name}')
            ao = Artist()
            ao.query_artist_by_id(self.artist_id)
            try:
                self.navidrome_id = n.search_album(ao,self)
                logger.debug(f'Got navidrome album_id: {self.navidrome_id}')
            except AlbumNotFound as e:
                logger.info(f'Could not find album name: {self.name} for artist: {ao.name} in Navidrome. continuing....')
                self.navidrome_id = None


    def query_album(self):
        # query album from db
        if self.id:
            # we have an id. Query by it
            self.query_album_by_id()
            return

        # query by name, artist_id
        logger.debug(f'Querying album by name: {self.name} and artist_id: {self.artist_id}')

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    album s
            WHERE   s.name = %s
            AND     s.artist_id = %s
        """

        c_query.execute(query_statement,
                        (self.name,self.artist_id))
        if c_query.rowcount == 0:
            logger.debug('No album found for name: {}, artist id: {}'.format(self.name,self.artist_id))
            return

        if c_query.rowcount != 1:
            logger.warning('Found multiple albums!')
            return

        sdata = c_query.fetchone()
        self.id = sdata['id']
        self.name = sdata['name']
        self.artist_id = sdata['artist_id']
        self.release_date = sdata['release_date']
        self.release_year = sdata['release_year']
        self.number_of_disks = sdata['number_of_disks']
        self.track_count = sdata['track_count']
        self.rating = sdata['rating']
        self.yt_id = sdata['youtube_id']
        if sdata['navidrome_id']:
            self.navidrome_id = sdata['navidrome_id']
        else:
            n = Navidrome()  
            logger.debug(f'Querying navidrome for album name: {self.name}')
            ao = Artist(self.ytm,self.dbh)
            ao.id = self.artist_id
            ao.query_artist_by_id()
            try:
                self.navidrome_id = n.search_album(ao,self)
            except AlbumNotFound as e:
                self.navidrome_id = None
           
            logger.debug(f'Got navidrome album_id: {self.navidrome_id}')

    def update_db(self):
        logger.debug('Updating album name {}, album id: {}'.format(self.name,self.id))
        logger.debug(f'Navidrome_id: {self.navidrome_id}')

        try:
            c_stmt = self.dbh.cursor()
            update_stmt = """ 
            update album
                set name = %s,
                    artist_id = %s,
                    release_date = %s,
                    release_year = %s,
                    number_of_disks = %s,
                    track_count = %s,
                    rating = %s,
                    youtube_id = %s,
                    navidrome_id = %s
                where id = %s
            """
            c_stmt.execute(
                update_stmt,
                (self.name, self.artist_id, self.release_date, self.release_year, self.number_of_disks,
                 self.track_count, self.rating, self.yt_id, self.navidrome_id, self.id)
            )
            logger.debug('Updated album: {}, id: {}'.format(self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            logger.error('Error updating album: {}'.format(error))
            self.print_attributes()
            raise

        finally:
            c_stmt.close()

    def insert_db(self):
        logger.debug('Inserting album name {}, artist id: {}'.format(self.name,self.artist_id))
        try:
            c_stmt = self.dbh.cursor()
            insert_stmt = """ 
            insert into album
                ( name, artist_id, release_date, release_year, number_of_disks,
                  track_count, rating, youtube_id, navidrome_id )
                values
                ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
                RETURNING id
            """
            c_stmt.execute(
                insert_stmt,
                (self.name, self.artist_id, self.release_date, self.release_year, self.number_of_disks,
                 self.track_count, self.rating, self.yt_id, self.navidrome_id)
            )
            self.id = c_stmt.fetchone()[0]
            logger.debug('Inserted album: {} as id: {}'.format(
                self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            logger.error('Error inserting album: {}'.format(error))
            self.print_attributes()
            raise

        finally:
            c_stmt.close()

    def save(self):
        # save album to database
        # query first to see if it exists:
        self.query_album()

        if self.id:
            self.update_db()
        else:
            self.insert_db()
        self.dbh.commit()
