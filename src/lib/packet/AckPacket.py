from struct import pack, unpack

from BasePacket import BasePacket
from constants import Type


class AckPacket(BasePacket):
    FORMAT = "!HH"

    def __init__(self, block_number: int):
        self.type = Type.ACKOWLEDGMENT
        self.block_number = block_number

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type, self.block_number)])

    def get_block_number(self):
        return self.block_number

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(unpack(cls.FORMAT, packet)[1])

    def __str__(self):
        return f"Type: Ack, Block Number: #{self.block_number}"
