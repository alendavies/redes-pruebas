from lib.Connection import Connection
from lib.FileService import FileService
from lib.protocols.ProtocolClient import ProtocolClient


class Client(ProtocolClient):

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def upload(self, filename: str):
        raise NotImplementedError

    def download(self, filename: str):
        raise NotImplementedError
