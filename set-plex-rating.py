import sqlite3
import logging
from utilities.exceptions import InvalidFileExtension, FatalError

logger = logging.getLogger(__name__)
#local_music_path = r"E:\media\music"
local_music_path = r"E:\media\music"
#dbFileName=r"Z:\appdata\plexmediaserver\app\Library\Application Support\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.test.db"
#dbFileName=r'Z:\appdata\plexmediaserver\app\Library\Application Support\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.db'
dbFileName='/srv/appdata/plexmediaserver/app/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
#dbFileName=r'/srv/appdata/plexmediaserver/app/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.test.db'


class Track:
    'Common base class for all tracks'

    trackCount = 0

    def __init__(self, mediaItemId):
        self.rating = 0
        self.mediaItemId = mediaItemId
        self.dbConn = self.dbConnect()
        self.populateTrackFromDb()
        self.readTagData()

        if self.jerry_plexRating is None:
            logger.info ("no plex rating, setting to 1")
            self.rating = 1
        else:
            logger.info (f'rating is: {self.rating}')

        if self.jerry_metaDataItemsId is None:
            # if they have no row in metadata_item_settings, insert one
            logger.info('inserting jerry')
            self.insertMetaDataItemsSettings(1)

        logger.info('updating jerry')
        self.updateMetaDataItemSettingsRating(self.jerry_metaDataItemsId)

        if self.general_metaDataItemsId is None:
            # if they have no row in metadata_item_settings, insert one
            logger.info('inserting general')
            self.insertMetaDataItemsSettings(3788213)
        logger.info('updating general')
        self.updateMetaDataItemSettingsRating(self.general_metaDataItemsId)

        Track.trackCount += 1
        self.dbConn.commit()
        self.dbConn.close()
        logger.info('db commit and close')

    def getLocalPath(self,libPath,fileName):
#        logger.debug(f'got db track path: {fileName}. replacing with {local_music_path}')
#        newfile = fileName.replace(libPath,local_music_path)
#        logger.debug(f'Local track path is {newfile}')
#        return newfile
        return fileName

    def displayCount(self):
        logger.info ("Total tracks %d" % Track.trackCount)

    def displayTrack(self):
        logger.info (f'Track Id: {self.mediaItemId}, Rating: {self.rating}, MetaDataItemsId: {self.jerry_metaDataItemsId}, filename: {self.fileName}')

    def dbConnect(self):
        import sqlite3

        conn = sqlite3.connect(dbFileName)
        return conn

    def insertMetaDataItemsSettings(self,account_id):
        logger.info (f'inserting row account_id: {account_id}, for guid: {self.metaDataGuid}')
        i1 = '''\
            INSERT INTO metadata_item_settings
                ( account_id, guid, rating )
                VALUES
                ( ?, ?, ? )\
            '''

        c = self.dbConn.cursor()
        c.execute(i1, (account_id,self.metaDataGuid,self.rating))

    def updateMetaDataItemSettingsRating(self,metadataitems_id):
        logger.debug (f'Updating id: {metadataitems_id} rating to: {self.rating}')
        i1 = "UPDATE metadata_item_settings set rating = ? where id = ?"
        c = self.dbConn.cursor()
        c.execute(i1, (self.rating, metadataitems_id))

    def readTagData(self):
        import os
        from mutagen.mp3 import MutagenError

        file_extension = os.path.splitext(self.fileName)[1][1:]
        logger.info(f'File Extension of {self.fileName} is: {file_extension}')

        try:
            if file_extension == 'ogg':
                self.handleOGG()
            elif file_extension == 'flac':
                self.handleFlac()
            elif file_extension == 'mp3':
                self.handleMP3()
            elif file_extension == 'wma':
                logger.info ("Can't handle wma....yet")
                self.rating = 0
            elif file_extension == 'm4a':
                logger.info ("Can't handle m4a....yet")
                self.rating = 0
            else:
                logger.info (f'Invalid file type: {file_extension} on file {self.fileName}')
                raise InvalidFileExtension(file_extension,self.fileName)
            logger.info (f'Setting Plex Rating to: {self.rating}')
            if self.rating < 0 or self.rating > 10:
                logger.info (f'Invalid rating: {self.rating}')
                raise SystemExit
        except MutagenError as e:
            #logger.error(str(e))
            raise FatalError('Error in Mutagen')

    def handleMP3(self):
        from mutagen.mp3 import MP3

        f = MP3(self.fileName)
        self.rating = 0
        for frame in f.tags.getall("TXXX"):
            if frame.HashKey == 'TXXX:FMPS_Rating':
                if frame == '0.1':
                    self.rating = 1
                elif frame == '0.2':
                    self.rating = 2
                elif frame == '0.3':
                    self.rating = 3
                elif frame == '0.4':
                    self.rating = 4
                elif frame == '0.5':
                    self.rating = 5
                elif frame == '0.6':
                    self.rating = 6
                elif frame == '0.7':
                    self.rating = 7
                elif frame == '0.8':
                    self.rating = 8
                elif frame == '0.9':
                    self.rating = 9
                elif frame == '1':
                    self.rating = 10
                return
#        logger.info f.pprint()

    def handleFlac(self):
        from mutagen.flac import FLAC
        f = FLAC(self.fileName)
        for tag in f.tags:
            if tag[0].upper() == 'FMPS_RATING':
                frame = tag[1]
                logger.info (f'flac rating is: {frame}')
                self.rating = float(frame) * 10
                return

    def handleOGG(self):
        from mutagen.oggvorbis import OggVorbis
        f = OggVorbis(self.fileName)
        for tag in f.tags:   # pylint: disable=not-an-iterable
            if tag[0].upper() == 'FMPS_RATING':
                frame = tag[1]
                logger.info (f'ogg rating is: {frame}')
                self.rating = float(frame) * 10
                return

    def populateTrackFromDb(self):
        q1 = '''\
            SELECT mi.id, mi.library_section_id, mi.section_location_id, mi.metadata_item_id,
                ls.name,
                sl.root_path,
                mp.file,
                mdi.id, mdi.guid,
                mis_jerryarn.id, mis_jerryarn.account_id, mis_jerryarn.rating,
                mis_general.id, mis_general.account_id, mis_general.rating
            FROM media_items mi
            JOIN library_sections ls on mi.library_section_id = ls.id
            JOIN section_locations sl on mi.section_location_id = sl.id
            JOIN media_parts mp on mi.id = mp.media_item_id
            join metadata_items mdi on mi.metadata_item_id = mdi.id
            LEFT OUTER JOIN metadata_item_settings mis_jerryarn on mdi.guid = mis_jerryarn.guid and mis_jerryarn.account_id = 1
            LEFT OUTER JOIN metadata_item_settings mis_general on mdi.guid = mis_general.guid and mis_general.account_id = 3788213
            WHERE mi.id = ?\
            '''
        c = self.dbConn.cursor()
        c.execute(q1, (self.mediaItemId,))
        r = c.fetchone()
#        logger.info r
        self.librarySectionId = r[1]
        self.sectionLocationId = r[2]
        self.metadataItemId = r[3]
        self.librarySectionName = r[4]
        self.rootPath = r[5]
        self.localPath = r[5]
        self.fileName = self.getLocalPath(self.localPath,r[6])
        self.metaDataId = r[7]
        self.metaDataGuid = r[8]
        self.jerry_metaDataItemsId = r[9]
        self.jerry_accountId = r[10]
        self.jerry_plexRating = r[11]
        self.general_metaDataItemsId = r[12]
        self.general_accountId = r[13]
        self.general_plexRating = r[14]
# End Class Track

#t = Track(201734)

def main():

    log_level = logging.INFO
    log_format = '%(asctime)s (%(levelname)s) [%(module)s::%(funcName)s::%(lineno)d] %(message)s'
    logging.basicConfig(level=log_level,format=log_format)

    logger.info('Here we go')
    logger.debug('Running in verbose mode')

    logger.info('using database file: {}'.format(dbFileName))
    conn = sqlite3.connect(dbFileName)
    q1 = '''\
        SELECT mi.id
        FROM media_items mi
        WHERE mi.library_section_id = 4
        ORDER BY mi.id desc
        '''
    arr = []
    c = conn.cursor()
    for row in c.execute(q1):
        #logger.info(row)
        arr.append(row[0])
    c.close()

    t_count = 0

    for plexid in arr:
        t_count += 1
        try:
            t = Track(plexid)
            t.displayTrack()
        except InvalidFileExtension as e:
            logger.info(str(e))
            logger.info("continuing....")
        except FileNotFoundError as e:
            logger.error(str(e))
            return
        #if t_count > 300:
        #    break

    t.displayCount()
    logger.info ("Done....")
    return

if __name__ == "__main__":
    main()