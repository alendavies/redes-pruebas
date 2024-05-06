from src.lib.packet.DownloadRequestPacket import DownloadRequestPacket
from src.lib.packet.UploadRequestPacket import UploadRequestPacket
from src.lib.ProtocolServer import ProtocolServer


class Server(ProtocolServer):

    def __init__(self, connection: Connection, file_service: FileService, logger: Logger):
        super().__init__(connection, file_service, logger)

    def _handle_upload(self, packet: UploadRequestPacket):
        pass

    def _handle_download(self, packet: DownloadRequestPacket):
        pass

