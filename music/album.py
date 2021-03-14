from Utilities import Utilities
from music.artist import Artist
import psycopg2
import psycopg2.extras

class Album:
    "Music Album class"

    def __init__(self, utilities, ytmusic, dbh, name=None, artist_id=None, release_date=None,
                 release_year=None, number_of_disks=0, track_count=0, rating=0):
        self.u = utilities  # Utilities Object
        self.ytm = ytmusic  # youtube Music API object
        self.dbh = dbh      # database handle
        self.id = None      # pk from database

        self.name = name
        self.artist_id = artist_id
        self.release_date = release_date
        self.release_year = release_year
        self.number_of_disks = number_of_disks
        self.track_count = track_count
        self.rating = rating
        self.yt_id = None

    def print_attributes(self):
        self.u.debug('Album:')
        self.u.debug('  Name       : {}'.format(self.name))
        self.u.debug('  ID         : {}'.format(self.id))
        self.u.debug('  Artist Id  : {}'.format(self.artist_id))
        self.u.debug('  Rating     : {}'.format(self.rating))
        self.u.debug('  Track Count: {}'.format(self.track_count))
        self.u.debug('  YouTube ID : {}'.format(self.yt_id))

    def load_album_from_youtube(self, youtube_album):
        #uself.u.pprintd(youtube_album)
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
        self.print_attributes()

    def query_album_by_id(self):
        # query album from db
        if not self.id:
            self.u.log('No id is defined to query album by')
            return

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    medialib.album s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement, (self.id,))
        if c_query.rowcount == 0:
            self.u.log('No album found for id: {}'.format(self.id))
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

    def query_album(self):
        # query album from db
        if self.id:
            # we have an id. Query by it
            self.query_album_by_id()
            return

        # query by tiname, artist_id

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    medialib.album s
            WHERE   s.name = %s
            AND     s.artist_id = %s
        """

        c_query.execute(query_statement,
                        (self.name,self.artist_id))
        if c_query.rowcount == 0:
            self.u.log('No album found for name: {}'.format(self.name))
            return

        if c_query.rowcount != 1:
            self.u.log('Found multiple albums!')
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

    def update_db(self):

        try:
            c_stmt = self.dbh.cursor()
            update_stmt = """ 
            update medialib.album
                set name = %s,
                    artist_id = %s,
                    release_date = %s,
                    release_year = %s,
                    number_of_disks = %s,
                    track_count = %s,
                    rating = %s,
                    youtube_id = %s
                where id = %s
            """
            c_stmt.execute(
                update_stmt,
                (self.name, self.artist_id, self.release_date, self.release_year, self.number_of_disks,
                 self.track_count, self.rating, self.yt_id, self.id)
            )
            self.u.debug('Updated album: {}, id: {}'.format(self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            self.u.log('Error updating album: {}'.format(error))
            self.print_attributes()
            raise

        finally:
            c_stmt.close()

    def insert_db(self):

        try:
            c_stmt = self.dbh.cursor()
            insert_stmt = """ 
            insert into medialib.album
                ( name, artist_id, release_date, release_year, number_of_disks,
                  track_count, rating, youtube_id )
                values
                ( %s, %s, %s, %s, %s, %s, %s, %s )
                RETURNING id
            """
            c_stmt.execute(
                insert_stmt,
                (self.name, self.artist_id, self.release_date, self.release_year, self.number_of_disks,
                 self.track_count, self.rating, self.yt_id)
            )
            self.id = c_stmt.fetchone()[0]
            self.u.debug('Inserted album: {} as id: {}'.format(
                self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            self.u.log('Error inserting album: {}'.format(error))
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
