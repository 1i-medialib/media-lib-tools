import logging

logger = logging.getLogger(__name__)

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