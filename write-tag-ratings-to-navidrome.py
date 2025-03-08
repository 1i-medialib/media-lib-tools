#!/usr/bin/env python3

import psycopg2
import psycopg2.extras
import argparse
import logging
from music.song import Song
from music.artist import Artist
from music.album import Album
from utilities.exceptions import FatalError, MultipleArtistsFound, ArtistsNotFound, AlbumNotFound, SongNotFound
from utilities.navidrome import Navidrome

file_count = 1
dir_count = 1

logger = logging.getLogger(__name__)

def connect_to_pg(cfg):
    try:
        cnx = psycopg2.connect(**cfg)
    except (Exception, psycopg2.Error) as err:
        logger.error('Error while connecting to Postgresql: {}'.format(err))
        raise
    else:
        logger.debug('Connected to postgresql datdabase')
    return cnx

def process_songs(dbh,navidrome,artist,album):
    song_cursor = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        logger.debug(f"Fetching songs from artist_id: {artist.id}, album_id: {album.id}")
        logger.debug('artist_id is type: {}'.format(type(artist.id)))
        song_cursor.execute(
            """
            SELECT  id FROM SONG 
            WHERE   album_id = %s
            AND     artist_id = %s
            ORDER 
            BY      disk_number ASC,
                    track_number ASC
            """,
            ((album.id),artist.id,))
        rows = song_cursor.fetchall()
        for row in rows:
            try:
                logger.info(row)
                song = Song(ytmusic=None,dbh=dbh)
                song.id = row['id']
                song.query_song_by_id()
                #song.print_attributes()
                if not song.navidrome_id:
                    navidrome.update_song(artist,album,song)
            except SongNotFound as e:
                continue
    finally:
        song_cursor.close()

def process_albums(dbh,navidrome,artist):
    album_cursor = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        album_cursor.execute('SELECT id FROM ALBUM WHERE artist_id = %s ORDER BY name ASC',(artist.id,))
        rows = album_cursor.fetchall()
        for row in rows:
            try:
                logger.info(row)
                album = Album(ytmusic=None,dbh=dbh)
                album.id = row['id']
                album.query_album_by_id()
                #album.print_attributes()
                if not album.navidrome_id:
                    navidrome.update_album(artist,album)

                process_songs(dbh,navidrome,artist,album)
            except AlbumNotFound as e:
                continue

    finally:
        album_cursor.close()

def process_artists(dbh,navidrome):
    artist_cursor = dbh.cursor(cursor_factory=psycopg2.extras.DictCursor)
    artist_cursor.execute(
        '''
        DECLARE cursor 
        CURSOR FOR 
        SELECT  id
        FROM    ARTIST
        WHERE   ID != 0
        AND     id in (604)
        ORDER BY name ASC
        ''')

    while True:
        artist_cursor.execute('FETCH 100 FROM cursor')
        rows = artist_cursor.fetchall()
        if not rows:
            break
        for row in rows:
            try:
                logger.info(row)
                artist = Artist(ytmusic=None,dbh=dbh)
                artist.id = row['id']
                artist.query_artist_by_id()
                #artist.print_attributes()
                if not artist.navidrome_id:
                    navidrome.update_artist(artist)

                process_albums(dbh,navidrome,artist)
            except ArtistsNotFound as e:
                continue

    artist_cursor.close()

def main():
    parser = argparse.ArgumentParser(
        description='Write Ratings from file tags to Navidrome.')

    parser.add_argument('--verbose', '-v',
                        help='verbose logging', action='store_true')

    args = parser.parse_args()

    # set up logging
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    log_format = '%(asctime)s (%(levelname)s) [%(module)s::%(funcName)s::%(lineno)d] %(message)s'
    logging.basicConfig(level=log_level,format=log_format)
    logger.info('Here we go')
    logger.debug('Running in verbose mode')

    pg_config = {
        'user': 'medialib_app',
        'password': 'apppass',
        'host': '192.168.50.5',
        'database': 'medialib',
        'port': 35432
    }

    pgc = connect_to_pg(pg_config)
    navidrome = Navidrome()

    process_artists(pgc,navidrome)
    pgc.close()
    logger.warning('Finished...')

if __name__ == '__main__':
    main()
