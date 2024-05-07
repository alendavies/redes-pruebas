from abc import abstractmethod
from lib.loggers.BaseLogger import BaseLogger

class ServerFileService:
    
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.logger = BaseLogger("ServerFiles")

    def save_file_on_server(self, filename: str, data: bytes):
        self.logger.debug("Saving file: " + filename)
        file = open(self.storage_dir + '/' + filename, "wb")
        file.write(data)
        file.close()

    def get_file_from_server(self, filename: str):
        self.logger.debug("Getting file: " + filename)
        file = open(self.storage_dir + '/' + filename, "rb")
        data = file.read()
        return data

class ClientFileService:

    def __init__(self):
        self.logger = BaseLogger("ClientFiles")

    def save_file_local(self, destination: str, data: bytes):
        self.logger.debug("Saving file: " + destination)
        file = open(destination, "wb")
        file.write
        file.close()

    def get_file_local(self, source: str):
        self.logger.debug("Getting file: " + source)
        file = open(source, "rb")
        data = file.read()
        return data

