#!/usr/bin/env python3

import argparse
import base64
import datetime
import json
import logging
import os
import requests
import hashlib
from pathlib import Path
from utilities.exceptions import PictureNotFound,FileTypeIgnore,UnhandledFileType

file_count = 1
dir_count = 1
directory_recursion_level = 0
max_dirs = 100

logger = logging.getLogger(__name__)

def get_file_checksum(file_path):
    with open(file_path, 'rb', buffering=0) as f:
        sha1_unhashed = hashlib.file_digest(f, 'sha1').digest()
    sha1_hashed = base64.b64encode(sha1_unhashed).decode("utf-8")
    logger.debug('FilePath: {}, Shat1: {}, Hashed: {}'.format(file_path, sha1_hashed, sha1_hashed))
    return sha1_hashed

def retrieve_photo_from_immich(file):
    url = 'https://photos.fargue.net/api/search/metadata'
    headers = {'user-agent': 'my-app/0.0.1',
               'x-api-key': 'DrkRC29lilNsFrhSgcMvmbSiHXtT6G4Kp8IDOn9OdHQ',
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Connection': 'keep-alive'
               }
    #payload = {'originalFileName': file['file_name'] }
    payload = {'checksum': file['checksum'] }
    img = None
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        if not 'assets' in r.json():
            logger.error(f'Response for Filename: {file['file_name']} is invalid. No assets value.')
            logger.error(json.dumps(r.data, indent=4))
            raise ValueError

        jd = r.json()
        a= jd['assets']
        logger.debug(f'Response->assets: {a}')
        if a['count'] == 0:
            raise PictureNotFound(file)
        elif a['count'] != 1:
            raise ValueError
            logger.debug(f'Found {a['count']} matches for file name: {file['file_name']}')
            logger.debug('file info - Checksum: {}, mtime: {}'
                        .format(file['checksum'],datetime.datetime.fromtimestamp(file['ctime'])))
            found = False
            for immich_obj in a['items']:
                logger.debug('Immich info - Checksum: {}, mtime: {}'
                            .format(immich_obj['checksum'],immich_obj['fileModifiedAt']))
                if file['checksum'] == immich_obj['checksum']:
                    logger.debug('Match')
                    found = True
                    img = immich_obj
                    break
            if not found:
                raise PictureNotFound(file)
        else:
            # found one, return it.
            img = a['items'][0]
    except (requests.exceptions.JSONDecodeError) as e:
        logger.error(e)
        raise e
    return img

def process_file(file_path):
    if not Path(file_path).name.startswith('.'):
        logger.debug('Processing File: {}'.format(file_path))
        try:
            fname=os.path.basename(file_path)
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
            file_extension = (os.path.splitext(fname)[1][1:]).lower()
            fchecksum = get_file_checksum(file_path)

            logger.debug('File Stats:')
            logger.debug(f'  Extention: {file_extension}')
            logger.debug(f'  Checksum: {fchecksum}')
            logger.debug(f'  Mode: {mode}')
            logger.debug(f'  Size: {size}')
            logger.debug('  Mtime: %s' % datetime.datetime.fromtimestamp(mtime))
            logger.debug('  Ctime: %s' % datetime.datetime.fromtimestamp(ctime))
            file_info = {
                'file_path': file_path,
                'file_name': fname,
                'checksum': fchecksum,
                'mode': mode,
                'size': size,
                'mtime': mtime,
                'ctime': ctime
            }
            if file_extension in ['db']:
                raise FileTypeIgnore(file_extension)
            if file_extension not in ['jpg','mov']:
                raise UnhandledFileType(file_extension)
            obj = retrieve_photo_from_immich(file_info)
        except FileTypeIgnore as e:
            logger.debug('Not processing ignored file type: {}'.format(e))
        except UnhandledFileType as e:
            logger.error('Can\'t handle file: {}'.format(e))
        except PictureNotFound as e:
            logger.info(str(e))
        except Exception as e:
            logger.error('Error with file: {}, - {}'.format(file_path,e))
            raise

def read_dir(dir_path):
    global file_count
    global dir_count
    global directory_recursion_level

    directory_recursion_level += 1
    if directory_recursion_level <= 2:
        logger.info('Reading directory {}'.format(dir_path))
    else:
        logger.debug('Reading directory {}'.format(dir_path))
    if dir_path.endswith('@eaDir'):
        logger.debug('not')
        return
    p = Path(dir_path)
    for entry in p.iterdir():
        if entry.is_file():
            file_count += 1
            process_file('{}/{}'.format(dir_path, entry.name))
        elif entry.is_dir():
            # directory
            dir_count += 1
            read_dir('{}/{}'.format(dir_path, entry.name))
        else:
            logger.error('Don\'t know how to handle entry: {}'.format(entry.name))
    directory_recursion_level -= 1
    if directory_recursion_level == 1 and dir_count >= max_dirs:
        logger.info(f'recursion is {directory_recursion_level}, dir_count {dir_count}, max {max_dirs}')
        raise StopIteration


def main():
    parser = argparse.ArgumentParser(
        description='import songs from filesystem library.')

    parser.add_argument('--verbose', '-v',
                        help='verbose logging', action='store_true')
    parser.add_argument('--path', '-p', help='library path',required=True)

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

    read_dir(args.path)

    logger.warning('Read {} Directories and {} Files'.format(dir_count, file_count))
    logger.warning('Finished...')

if __name__ == '__main__':
    main()
