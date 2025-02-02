import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

class Artist:
    "Music Artist class"

    def __init__(self, ytmusic, dbh, name=None, rating=0):
        self.ytm = ytmusic   # youtube Music API object
        self.dbh = dbh     # database handle
        self.id = None      # pk from database

        self.name = name
        self.rating = rating
        self.yt_id = None

    def print_attributes(self):
        logger.warning('Artist:')
        logger.warning('  ID    : {}'.format(self.id))
        logger.warning('  Name  : {}'.format(self.name))
        logger.warning('  Rating: {}'.format(self.rating))

    def load_artist_from_youtube(self,youtube_artist):
        if 'id' in youtube_artist:
            self.yt_id = youtube_artist['id']
        if 'name' in youtube_artist:
            self.name = youtube_artist['name']
        self.query_artist()
        self.save()
        # only print if debug level
        if logging.root.level == logging.DEBUG:
            self.print_attributes()

    def query_artist_by_id(self):
        # query artist from db
        if not self.id:
            logger.warning('No id is defined to query artist by')
            return

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    artist s
            WHERE   s.id = %s
        """
        c_query.execute(query_statement, (self.id,))
        if c_query.rowcount == 0:
            logger.warning('No artist found for id: {}'.format(self.id))
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
        logger.debug('Querying artist with name: {}, type: {}'.format(
                self.name, type(self.name)))

        c_query = self.dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query_statement = """
            SELECT *
            FROM    artist s
            WHERE   s.name = %s
        """

        c_query.execute(query_statement,
                        (self.name,))
        if c_query.rowcount == 0:
            logger.debug('No artist found for name: {}, type: {}'.format(self.name, type(self.name)))
            return

        if c_query.rowcount != 1:
            logger.warning('Found multiple artists!')
            return

        sdata = c_query.fetchone()
        self.id = sdata['id']
        self.name = sdata['name']
        self.yt_id = sdata['youtube_id']
        logger.debug('Artist: {}, has id: {}'.format(self.name,self.id))

    def update_db(self):
        pass

    def insert_db(self):

        try:
            c_stmt = self.dbh.cursor()
            insert_stmt = """ 
            insert into artist
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
            logger.debug('Inserted artist: {} as id: {}'.format(
                self.name, self.id))
        except (Exception, psycopg2.Error) as error:
            logger.error('Error inserting artist: {}'.format(error))
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
