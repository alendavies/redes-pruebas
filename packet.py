from enum import Enum
from struct import pack, unpack

from config import PACKET_SIZE

class Type(Enum):
    READ_REQUEST = 1
    WRITE_REQUEST = 2
    DATA = 3
    ACKOWLEDGMENT = 4
    ERROR = 5


class ReadRequestPacket:
    FORMAT = "!H"
    
    def __init__(self, filename: str):
        self.type = Type.READ_REQUEST.value
        self.data = filename

    def serialize(self) -> bytes: 
        return b''.join([pack(self.FORMAT, self.type), self.data.encode()])
    
    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(packet[2:].decode())

    def __str__(self):
        return f"Type: Read Request, Filename: {self.data}"


class WriteRequestPacket:
    FORMAT = "!H"
    
    def __init__(self, filename: str):
        self.type = Type.WRITE_REQUEST.value
        self.data = filename

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type), self.data.encode()])

    @classmethod
    def deserialize(cls, packet: bytes):
        return cls(packet[2:].decode())

    def __str__(self):
        return f"Type: Write Request, Filename: {self.data}"


class DataPacket:
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

class AckPacket:
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


class ErrorPacket:
    FORMAT = "!H"
    
    def __init__(self):
        self.type = Type.ERROR.value

    def serialize(self) -> bytes:
        return b''.join([pack(self.FORMAT, self.type)])

    @classmethod
    def deserialize(cls):
        return cls()

    def __str__(self):
        return f"Type: Error"

class BasePacket:
    FORMAT = "!H"
    def __init__(self, packet_type):
        self.packet_type = packet_type.value

    @classmethod
    def create_packet_instance(cls, type: int, packet: bytes):
        if type == Type.READ_REQUEST.value:
            return ReadRequestPacket.deserialize(packet)
        elif type == Type.WRITE_REQUEST.value:
            return WriteRequestPacket.deserialize(packet)
        elif type == Type.DATA.value:
            return DataPacket.deserialize(packet) 
        elif type == Type.ACKOWLEDGMENT.value:
            return AckPacket.deserialize(packet)
        elif type == Type.ERROR.value:
            return ErrorPacket.deserialize()
        else: raise Exception("Invalid packet type")

    @classmethod
    def get_packet(cls, packet: bytes):
        packet_type = unpack(cls.FORMAT, packet[:2])[0]
        return cls.create_packet_instance(packet_type, packet) 
