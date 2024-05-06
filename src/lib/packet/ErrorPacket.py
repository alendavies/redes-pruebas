from struct import pack

from BasePacket import BasePacket
from constants import Type


class ErrorPacket(BasePacket):
    FORMAT = "!H"

    def __init__(self):
        self.type = Type.ERROR

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type)])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls()

    def __str__(self):
        return f"Type: Error"
