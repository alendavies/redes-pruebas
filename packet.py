from abc import abstractmethod
from enum import Enum
from struct import pack, unpack
from typing import LiteralString, Self

from config import PACKET_SIZE

class Type(Enum):
    READ_REQUEST = 1
    WRITE_REQUEST = 2
    DATA = 3
    ACKOWLEDGMENT = 4
    ERROR = 5
    ACK_READ_REQ = 6
    ACK_WRITE_REQ = 7

# TODO: rename "deserialize" to "create_from_bytes"

class BasePacket:

    @abstractmethod
    def serialize(cls) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, packet: bytes) -> Self:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

class ReadRequestPacket(BasePacket):
    FORMAT = "!H"

    def __init__(self, filename: str):
        self.type = Type.READ_REQUEST.value
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


class WriteRequestPacket(BasePacket):
    FORMAT = "!H"

    def __init__(self, filename: str):
        self.type = Type.WRITE_REQUEST.value
        self.data = filename

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type), self.data.encode()])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(packet[2:].decode())

    def get_filename(self):
        return self.data

    def __str__(self):
        return f"Type: Write Request, Filename: {self.data}"


class DataPacket(BasePacket):
    FORMAT = "!HH"

    def __init__(self, block_number: int, data: bytes):
        self.type = Type.DATA.value
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
        return f"Type: Data, Block Number: #{self.block_number}, Data: {self.data}"

class AckReadRequest(BasePacket):
    FORMAT = "!HH"

    def __init__(self, file_size: int):
        self.type = Type.ACK_READ_REQ.value
        self.file_size = file_size

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type, self.file_size)])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(unpack(cls.FORMAT, packet)[1])

# TODO: chequear nombre de archivo, espacio dispnible, etc

class AckWriteRequest(BasePacket):
    FORMAT = "!HH"

    def __init__(self):
        self.type = Type.ACK_WRITE_REQ.value

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type)])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls()

class AckPacket(BasePacket):
    FORMAT = "!HH"

    def __init__(self, block_number: int):
        self.type = Type.ACKOWLEDGMENT.value
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


class ErrorPacket(BasePacket):
    FORMAT = "!H"

    def __init__(self):
        self.type = Type.ERROR.value

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type)])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls()

    def __str__(self):
        return f"Type: Error"


class MasterOfPackets:
    FORMAT = "!H"
    def __init__(self, packet_type: Type):
        self.packet_type = packet_type.value

    @classmethod
    def _create_packet_instance(cls, type: int, packet: bytes):
        case = {
                Type.READ_REQUEST.value: ReadRequestPacket,
                Type.WRITE_REQUEST.value: WriteRequestPacket,
                Type.DATA.value: DataPacket,
                Type.ACKOWLEDGMENT.value: AckPacket,
                Type.ERROR.value: ErrorPacket
        }
        return case[type].deserialize(packet)
        # TODO: contemplar caso donde type no es válido

    @classmethod
    def get_packet(cls, packet: bytes) -> BasePacket:
        packet_type = unpack(cls.FORMAT, packet[:2])[0]
        return cls._create_packet_instance(packet_type, packet)
