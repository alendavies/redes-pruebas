import os
from abc import abstractmethod

from lib.loggers.BaseLogger import BaseLogger


class ServerFileService:

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.logger = BaseLogger("ServerFiles")

    def save_file_on_server(self, filename: str, data: bytes):
        self.logger.debug("Saving file: " + filename)
        path = self.storage_dir + '/' + filename
        if os.path.isfile(path):
            raise FileExistsError
        file = open(path, "wb")
        file.write(data)
        file.close()

    def get_file_from_server(self, filename: str):
        self.logger.debug("Getting file: " + filename)
        path = self.storage_dir + '/' + filename
        if not os.path.isfile(path):
            raise FileNotFoundError
        file = open(path, "rb")
        data = file.read()
        return data

class ClientFileService:

    def __init__(self):
        self.logger = BaseLogger("ClientFiles")

    def save_file_local(self, destination: str, data: bytes):
        self.logger.debug("Saving file: " + destination)
        if os.path.isfile(destination):
            raise FileExistsError
        file = open(destination, "wb")
        file.write(data)
        file.close()

    def get_file_local(self, source: str):
        self.logger.debug("Getting file: " + source)
        if not os.path.isfile(source):
            raise FileNotFoundError
        file = open(source, "rb")
        data = file.read()
        return data
