from utilities.logging import Logging
import psycopg2
import psycopg2.extras

class Artist:
    "Music Artist class"

    def __init__(self, utilities, ytmusic, dbh, info=None):
        self.u = utilities  # Utilities Object
        self.ytm = ytmusic  # youtube Music API object
        self.dbh = dbh     # database handle
        self.id = None      # pk from database


        self.name = None
        self.rating = 0
        self.yt_id = None
        if info:
            if 'name' in info:
                self.name = info['name']
            if 'rating' in info:
                self.rating = info['rating']

    def print_attributes(self):
        self.u.debug('Artist:')
        self.u.debug('  ID    : {}'.format(self.id))
        self.u.debug('  Name  : {}'.format(self.name))
        self.u.debug('  Rating: {}'.format(self.rating))

    def load_artist_from_youtube(self,youtube_artist):
        if 'id' in youtube_artist:
            self.yt_id = youtube_artist['id']
        if 'name' in youtube_artist:
            self.name = youtube_artist['name']
        self.query_artist()
        self.save()
        self.print_attributes()

    def query_artist_by_id(self):
        # query artist from db
        if not self.id:
            self.u.log('No id is defined to query artist by')
            return

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    medialib.artist s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement, (self.id,))
        if c_query.rowcount == 0:
            self.u.log('No artist found for id: {}'.format(self.id))
            return
        sdata = c_query.fetchone()
        self.name = sdata['name']
        self.rating = sdata['rating']
        self.yt_id = sdata['youtube_id']

    def query_artist(self):
        # query artist from db
        if self.id:
            # we have an id. Query by it
            self.query_artist_by_id()
            return

        # query by title, artist, album

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    medialib.artist s
            WHERE   s.name = %s
        """

        c_query.execute(query_statement,
                        (self.name,))
        if c_query.rowcount == 0:
            self.u.log('No artist found for name: {}'.format(self.name))
            return

        if c_query.rowcount != 1:
            self.u.log('Found multiple artists!')
            return

        sdata = c_query.fetchone()
        self.id = sdata['id']
        self.name = sdata['name']
        self.yt_id = sdata['youtube_id']

    def update_db(self):
        pass

    def insert_db(self):

        try:
            c_stmt = self.dbh.cursor()
            insert_stmt = """ 
            insert into medialib.artist
                ( name, rating, youtube_id )
                values
                ( %s, %s, %s )
                RETURNING id
            """
            c_stmt.execute(
                insert_stmt,
                (self.name, self.rating, self.yt_id )
            )
            self.id = c_stmt.fetchone()[0]
            self.u.debug('Inserted artist: {} as id: {}'.format(
                self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            self.u.log('Error inserting artist: {}'.format(error))
            self.print_attributes()
            raise

        finally:
            c_stmt.close()

    def save(self):
        # save artist to database
        # query first to see if it exists:
        self.query_artist()

        if self.id:
            self.update_db()
        else:
            self.insert_db()
        self.dbh.commit()
