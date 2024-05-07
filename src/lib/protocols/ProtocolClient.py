from abc import abstractmethod

from lib.FileService import ClientFileService
from lib.loggers.ClientSideLogger import ClientSideLogger

from ..Connection import Connection

class ProtocolClient:

    def __init__(self, connection: Connection, file_service: ClientFileService):
        self.connection = connection
        self.file_service = file_service
        self.logger = ClientSideLogger()

    @abstractmethod
    def upload(self, source: str, filename: str):
        """
        Uploads the local `source` to the server as `filename`.
        """
        pass

    @abstractmethod
    def download(self, destination: str, filename: str):
        """
        Downloads the server's `filename` to the local `destination`.
        """
        pass

