from struct import unpack
from .DownloadRequestPacket import DownloadRequestPacket
from .UploadRequestPacket import UploadRequestPacket
from .AckPacket import AckPacket
from .DataPacket import DataPacket
from .ErrorPacket import ErrorPacket
from .BasePacket import BasePacket

from .constants import Type


class PacketParser:

    FORMAT = "!H"

    def __init__(self, packet_type: Type):
        self.packet_type = packet_type

    @classmethod
    def _create_packet_instance(cls, type: int, packet: bytes) -> BasePacket:
        case = {
                Type.READ_REQUEST: DownloadRequestPacket,
                Type.WRITE_REQUEST: UploadRequestPacket,
                Type.DATA: DataPacket,
                Type.ACKOWLEDGMENT: AckPacket,
                Type.ERROR: ErrorPacket,
        }
        try:
            return case[type].deserialize(packet)
        except Exception:
            raise ValueError(f"Invalid packet type: {type}")

    @classmethod
    def get_packet(cls, packet: bytes) -> BasePacket:
        packet_type = unpack(cls.FORMAT, packet[:2])[0]
        return cls._create_packet_instance(packet_type, packet)
