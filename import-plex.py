#!/usr/bin/env python3

import psycopg2
import psycopg2.extras
import argparse
import logging
from pathlib import Path
from music.song import Song
from utilities.exceptions import FileTypeIgnore, UnhandledFileType

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


def process_file(dbh,file_path):
    if not Path(file_path).name.startswith('.'):
        logger.debug('Processing File: {}'.format(file_path))
        try:
            s = Song(ytmusic=None,dbh=dbh,file_name=file_path)
            s.save()
        except FileTypeIgnore as e:
            logger.debug('Not processing image file: {}'.format(e))
        except UnhandledFileType as e:
            logger.error('Can\'t handle file: {}'.format(e))
            raise
        except Exception as e:
            if s:
                s.print_attributes()
                raise

def read_dir(dbh,dir_path):
    global file_count
    global dir_count
    logger.info('Reading directory {}'.format(dir_path))
    if dir_path.endswith('@eaDir'):
        logger.debug('not')
        return
    p = Path(dir_path)
    for entry in p.iterdir():
        if entry.is_file():
            file_count += 1
            process_file(dbh,'{}/{}'.format(dir_path, entry.name))
        elif entry.is_dir():
            # directory
            dir_count += 1
            read_dir(dbh,'{}/{}'.format(dir_path, entry.name))
        else:
            logger.error('Don\'t know how to handle entry: {}'.format(entry.name))


def main():
    parser = argparse.ArgumentParser(
        description='import songs from plex.')

    parser.add_argument('--verbose', '-v',
                        help='verbose logging', action='store_true')
    parser.add_argument('--path', '-p', help='library path')

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
        'host': '192.168.50.5',
        'database': 'medialib',
        'port': 35432
    }

    pgc = connect_to_pg(pg_config)

    read_dir(pgc,args.path)

    logger.warning('Read {} Directories and {} Files'.format(dir_count, file_count))
    logger.warning('Finished...')

if __name__ == '__main__':
    main()
