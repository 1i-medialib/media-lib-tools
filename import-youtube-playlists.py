#!/usr/bin/env python3

from ytmusicapi import YTMusic
import psycopg2
import psycopg2.extras
import argparse
import logging
from music.artist import Artist
from music.playlist import Playlist
from utilities.exceptions import FileTypeIgnore, UnhandledFileType

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

def get_playlist(ytm, dbh, playlist_name):
    # return array of match Playlist objects    
    logger.info('Searching for playlist: {}'.format(playlist_name))
    playlist_info=[]
    playlists = ytm.get_library_playlists()
    for l_playlist in playlists:
        if playlist_name:
            l_name = l_playlist['title'].lower()
            if playlist_name.lower() in l_name:
                p = Playlist(ytm, dbh)
                p.load_playlist_from_youtube(l_playlist)
                playlist_info.append(p)
        else:
            p = Playlist(ytm, dbh)
            p.load_playlist_from_youtube(l_playlist)
            playlist_info.append(p)
    return playlist_info

def main():
    parser = argparse.ArgumentParser(description='import songs from youtube music playlists.')

    parser.add_argument('--verbose','-v', help='verbose logging', action='store_true')
    parser.add_argument('--playlist','-p',help='playlist name')

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
        'password': 'medialib',
        'host': 'localhost',
        'database': 'medialib',
        'port': 35432
    }

    ytmusic = YTMusic('headers_auth.json')
    pgc = connect_to_pg(u,pg_config)

    get_playlist(u,ytmusic,pgc,args.playlist)
    logger.warning('Finished...')

if __name__ == '__main__':
    main()
