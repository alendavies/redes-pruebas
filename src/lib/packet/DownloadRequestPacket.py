from struct import pack

from BasePacket import BasePacket
from constants import Type


class DownloadRequestPacket(BasePacket):
    FORMAT = "!H"

    def __init__(self, filename: str):
        self.type = Type.READ_REQUEST
        self.data = filename

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type), self.data.encode()])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(packet[2:].decode())

    def get_filename(self):
        return self.data

    def __str__(self):
        return f"Type: Read Request, Filename: {self.data}"
