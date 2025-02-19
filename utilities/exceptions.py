import logging

logger = logging.getLogger(__name__)

class FatalError(Exception):
    "Fatal Error, stop processing, cleanup, exit"
    def __init__(self,msg="A Fatal Error has occurred"):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'FatalError: {self.msg}'

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
    def __init__(self,file_extension,file_namemsg="Unsupported File Extension"):
        self.file_extension = file_extension
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return f'{self.file_name}({self.file_extension}) -> {self.msg}'
