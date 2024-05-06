from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolServer import ProtocolServer
from lib.Connection import Connection
from lib.FileService import FileService


class Server(ProtocolServer):

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def _handle_upload(self, packet: UploadRequestPacket):
        pass

    def _handle_download(self, packet: DownloadRequestPacket):
        pass

