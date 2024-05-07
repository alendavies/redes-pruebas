from struct import pack, unpack

from .BasePacket import BasePacket
from .constants import PACKET_SIZE, Type


class DataPacket(BasePacket):
    FORMAT = "!HH"

    def __init__(self, block_number: int, data: bytes):
        self.type = Type.DATA
        self.block_number = block_number
        self.data = data

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type, self.block_number), self.data])

    def get_block_number(self):
        return self.block_number

    def get_data(self):
        return self.data

    def get_data_size(self):
        return len(self.data)

    def is_final_packet(self):
        return len(self.data) < PACKET_SIZE

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(unpack(cls.FORMAT, packet[:4])[1], packet[4:])

    def __str__(self):
        return f"[DATA] SEQNUM: {self.block_number}"
