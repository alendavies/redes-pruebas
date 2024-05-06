from abc import abstractmethod

from src.lib.packet.DownloadRequestPacket import DownloadRequestPacket
from src.lib.packet.UploadRequestPacket import UploadRequestPacket


class ProtocolServer:

    def __init__(self, connection: Connection, file_service: FileService, logger: Logger):
        self.connection = connection
        self.file_service = file_service
        self.logger = logger

    def handle(self, packet: bytes):
        pass

    @abstractmethod
    def _handle_upload(self, packet: UploadRequestPacket):
        pass

    @abstractmethod
    def _handle_download(self, packet: DownloadRequestPacket):
        pass
