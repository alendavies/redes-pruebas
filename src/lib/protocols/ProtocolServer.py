from abc import abstractmethod

from lib.FileService import ServerFileService
from lib.loggers.ServerSideLogger import ServerSideLogger
from lib.packets.PacketParser import PacketParser
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.Connection import Connection

import time


class ProtocolServer:

    def __init__(self, connection: Connection, file_service: ServerFileService):
        self.connection = connection
        self.file_service = file_service
        self.logger = ServerSideLogger()

    def handle(self, packet: bytes):
        instance = PacketParser.get_packet(packet)

        if isinstance(instance, DownloadRequestPacket):
            self.logger.info("Handling download request for file: " + instance.get_filename())
            try:
                self._handle_download(instance)
                self.logger.success("Download successful.")
            except Exception as e:
                self.logger.error("Error handling download request: " + str(e))

        elif isinstance(instance, UploadRequestPacket):
            self.logger.info("Handling upload request for file: " + instance.get_filename())
            try:
                self._handle_upload(instance)
                self.logger.success("Upload successful.")
            except Exception as e:
                self.logger.error("Error handling upload request: " + str(e))

        else:
            self.logger.error("Unexpected request.")
            raise Exception("Unexpected request.")
        pass

    @abstractmethod
    def _handle_upload(self, req_packet: UploadRequestPacket):
        pass

    @abstractmethod
    def _handle_download(self, req_packet: DownloadRequestPacket):
        pass
