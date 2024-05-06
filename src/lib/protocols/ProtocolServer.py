from abc import abstractmethod

from lib.loggers.ServerSideLogger import ServerSideLogger
from lib.packets.PacketParser import PacketParser
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.Connection import Connection
from lib.FileService import FileService


class ProtocolServer:

    def __init__(self, connection: Connection, file_service: FileService):
        self.connection = connection
        self.file_service = file_service
        self.logger = ServerSideLogger()

    def handle(self, packet: bytes):
        instance = PacketParser.get_packet(packet)

        if isinstance(instance, DownloadRequestPacket):
            self.logger.info("Handling download request for file: " + instance.get_filename())
            # TODO: try except
            self._handle_download(instance)

        elif isinstance(instance, UploadRequestPacket):
            self.logger.info("Handling upload request for file: " + instance.get_filename())
            # TODO: try except
            self._handle_upload(instance)

        else:
            # self.logger.error("Unexpected packet type")
            raise Exception("Unexpected packet type")
        pass

    @abstractmethod
    def _handle_upload(self, packet: UploadRequestPacket):
        pass

    @abstractmethod
    def _handle_download(self, packet: DownloadRequestPacket):
        pass
