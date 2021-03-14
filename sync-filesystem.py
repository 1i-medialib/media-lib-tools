#!/usr/bin/env python3

from ytmusicapi import YTMusic
import psycopg2
import psycopg2.extras
import argparse
from Utilities import Utilities
from music.artist import Artist
from music.playlist import Playlist


def connect_to_pg(u, cfg):
    try:
        cnx = psycopg2.connect(**cfg)
    except (Exception, psycopg2.Error) as err:
        u.log('Error while connecting to Postgresql: {}'.format(err))
        raise
    else:
        u.debug('Connected to postgresql datdabase')
    return cnx


def get_playlist(u, ytm, dbh, playlist_name):
    # return array of match Playlist objects    
    u.log('Searching for playlist: {}'.format(playlist_name))
    playlist_info=[]
    playlists = ytm.get_library_playlists()
    for l_playlist in playlists:
        if playlist_name:
            l_name = l_playlist['title'].lower()
            if playlist_name.lower() in l_name:
                p = Playlist(u, ytm, dbh)
                p.load_playlist_from_youtube(l_playlist)
                playlist_info.append(p)
        else:
            p = Playlist(u, ytm, dbh)
            p.load_playlist_from_youtube(l_playlist)
            playlist_info.append(p)
    return playlist_info

def main():
    parser = argparse.ArgumentParser(description='import songs from youtube music playlists.')

    parser.add_argument('--verbose','-v', help='verbose logging', action='store_true')
    parser.add_argument('--playlist','-p',help='playlist name')

    args = parser.parse_args()

    u = Utilities(args.verbose)
    u.log('Here we go')
    u.debug('Running in verbose mode')
    
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
    u.log('Finished...')


main()
