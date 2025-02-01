#!/usr/bin/env python3

import psycopg2
import psycopg2.extras
import argparse
from pathlib import Path
from utilities.logging import Logging
from music.song import Song

file_count = 1
dir_count = 1



def connect_to_pg(u, cfg):
    try:
        cnx = psycopg2.connect(**cfg)
    except (Exception, psycopg2.Error) as err:
        u.log('Error while connecting to Postgresql: {}'.format(err))
        raise
    else:
        u.debug('Connected to postgresql datdabase')
    return cnx


def process_file(l,dbh,file_path):
    if not Path(file_path).name.startswith('.'):
        print('Processing File: {}'.format(file_path))
        try:
            s = Song(log=l,ytmusic=None,dbh=dbh,file_name=file_path)
            s.save()
        except TypeError:
            l.log('not processing file')

def read_dir(u,dbh,dir_path):
    global file_count
    global dir_count
    print('Reading directory {}'.format(dir_path))
    p = Path(dir_path)
    for entry in p.iterdir():
        if entry.is_file():
            file_count += 1
            process_file(u,dbh,'{}/{}'.format(dir_path, entry.name))
        elif entry.is_dir():
            # directory
            dir_count += 1
            read_dir(u,dbh,'{}/{}'.format(dir_path, entry.name))
        else:
            error('Don\'t know how to handle entry: {}'.format(entry.name))


def main():
    parser = argparse.ArgumentParser(
        description='import songs from filesystem library.')

    parser.add_argument('--verbose', '-v',
                        help='verbose logging', action='store_true')
    parser.add_argument('--path', '-p', help='library path')

    args = parser.parse_args()

    u = Logging(args.verbose)
    u.log('Here we go')
    u.debug('Running in verbose mode')

    pg_config = {
        'user': 'medialib_app',
        'password': 'medialib',
        'host': 'localhost',
        'database': 'medialib',
        'port': 35432
    }

    pgc = connect_to_pg(u, pg_config)

    read_dir(u,pgc,args.path)

    u.log('Read {} Directories and {} Files'.format(dir_count, file_count))
    u.log('Finished...')


main()
