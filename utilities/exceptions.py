import logging

logger = logging.getLogger(__name__)

class FatalError(Exception):
    "Fatal Error, stop processing, cleanup, exit"
    def __init__(self,msg="A Fatal Error has occurred"):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'FatalError: {self.msg}'

class AlbumNotFound(Exception):
    "MediaLib Album Search Not Found"

    def __init__(self,artist_name,album_name,msg="MediaLib Album Search Not Found"):
        self.artist_name = artist_name
        self.album_name = album_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'Arist: {self.artist_name}, Album: {self.album_name} -> {self.msg}'

class ArtistNotFound(Exception):
    "MediaLib Artist Name Search Not Found"

    def __init__(self,artist_name,msg="MediaLib Artist Name Search Not Found"):
        self.name = artist_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.artist_name} -> {self.msg}'

class MultipleArtistsFound(Exception):
    "MediaLib Artist Name Search Yielded More Than One Result"

    def __init__(self,artist_name,msg="MediaLib Artist Name Search Yielded More Than One Result"):
        self.name = artist_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.artist_name} -> {self.msg}'

class AlbumNotFound(Exception):
    "MediaLib Album Name Search Not Found"

    def __init__(self,artist_name,album_name,msg="MediaLib Album Name Search Not Found"):
        self.artist_name = artist_name
        self.album_name = album_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'Arist: {self.artist_name}, Album: {self.album_name} -> {self.msg}'

class SongNotFound(Exception):
    "MediaLib Song Name Search Not Found"

    def __init__(self,artist_name,album_name,song_name, msg="MediaLib Song Name Search Not Found"):
        self.artist_name = artist_name
        self.album_name = album_name
        self.song_name = song_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'Arist: {self.artist_name}, Album: {self.album_name}, Song: {self.song_name} -> {self.msg}'

class UnhandledFileType(Exception):
    "MediaLib Unsupported File Type Exception class"

    def __init__(self,file_type,msg="Unsupported File Type"):
        self.file_type = file_type
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.file_type} -> {self.msg}'

class FileTypeIgnore(Exception):
    "MediaLib Image File Type Exception class"

    def __init__(self,file_type,msg="Image File Type"):
        self.file_type = file_type
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.file_type} -> {self.msg}'

class InvalidFileExtension(Exception):
    "Unhandled Extension"
    def __init__(self,file_extension,file_name,msg="Unsupported File Extension"):
        self.file_extension = file_extension
        self.file_name = file_name
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.file_name}({self.file_extension}) -> {self.msg}'

class PictureNotFound(Exception):
    "Picture Not Found in Immich"
    def __init__(self,file,msg="Picture not found in Immich"):
        self.file_name = file['file_name']
        self.checksum = file['checksum']
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.file_name}({self.checksum}) -> {self.msg}'
