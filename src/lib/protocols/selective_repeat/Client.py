from lib.protocols.ProtocolClient import ProtocolClient
from lib.FileService import FileService
from lib.Connection import Connection


class Client(ProtocolClient):

    WINDOW_SIZE = 10

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def upload(self, filename: str):
        raise NotImplementedError

    def download(self, filename: str):
        raise NotImplementedError
