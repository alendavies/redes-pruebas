from abc import abstractmethod
from msilib.schema import File


class ProtocolClient:

    def __init__(self, connection: Connection, file_service: FileService, logger: Logger):
        self.connection = connection
        self.file_service = file_service
        self.logger = logger

    @abstractmethod
    def upload(self, filename: str):
        pass

    @abstractmethod
    def download(self, filename: str):
        pass

