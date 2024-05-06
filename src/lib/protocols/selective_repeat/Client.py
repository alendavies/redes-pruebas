from src.lib.ProtocolClient import ProtocolClient


class Client(ProtocolClient):

    WINDOW_SIZE = 10

    def __init__(self, connection: Connection, file_service: FileService, logger: Logger):
        super().__init__(connection, file_service, logger)

    def upload(self, filename: str):
        pass

    def download(self, filename: str):
        pass
