from abc import abstractmethod

from lib.loggers.ClientSideLogger import ClientSideLogger

from ..Connection import Connection
from ..FileService import FileService


class ProtocolClient:

    def __init__(self, connection: Connection, file_service: FileService):
        self.connection = connection
        self.file_service = file_service
        self.logger = ClientSideLogger()

    @abstractmethod
    def upload(self, filename: str):
        pass

    @abstractmethod
    def download(self, filename: str):
        pass

