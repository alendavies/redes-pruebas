from lib.loggers.BaseLogger import BaseLogger

from lib.packets.BasePacket import BasePacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.DataPacket import DataPacket
from lib.packets.AckPacket import AckPacket
from lib.packets.ErrorPacket import ErrorPacket

class PacketLogger(BaseLogger):

    def __init__(self):
        super().__init__("Packet")

    def on_packet_sent(self, packet: BasePacket):
        self.debug("[SENT] {}".format(packet.__str__()))

    def on_packet_received(self, packet: BasePacket):
        self.debug("[RECEIVED] {}".format(packet.__str__()))

    def on_upload_request_sent(self, packet: UploadRequestPacket):
        pass

    def on_upload_request_received(self, packet: UploadRequestPacket):
        pass

    def on_download_request_sent(self, packet: DownloadRequestPacket):
        pass

    def on_download_request_received(self, packet: DownloadRequestPacket):
        pass

    def on_data_sent(self, packet: DataPacket):
        pass

    def on_data_received(self, packet: DataPacket):
        pass

    def on_ack_sent(self, packet: AckPacket):
        pass

    def on_ack_received(self, packet: AckPacket):
        pass

    def on_error_sent(self, packet: ErrorPacket):
        pass

    def on_error_received(self, packet: ErrorPacket):
        pass

    def on_unexpected_packet(self):
        pass

