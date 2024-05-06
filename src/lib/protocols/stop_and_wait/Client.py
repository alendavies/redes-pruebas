from src.lib.ProtocolClient import ProtocolClient


class Client(ProtocolClient):

    def __init__(self, connection, file_service, logger):
        super().__init__(connection, file_service, logger)

    def upload(self, filename):
        pass

    def download(self, filename):
        pass
