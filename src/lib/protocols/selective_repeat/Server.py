from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolServer import ProtocolServer
from lib.Connection import Connection
from lib.FileService import FileService


class Server(ProtocolServer):

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def _handle_upload(self, packet: UploadRequestPacket):
        # send ack0 and wait for first data
        # process first data
        # continue receiving data
        raise NotImplementedError("Not implemented.")

    def _handle_download(self, packet: DownloadRequestPacket):
        # get file
        # transmit file
        raise NotImplementedError("Not implemented.")

