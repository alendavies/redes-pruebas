from abc import abstractmethod


class BasePacket:

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, packet: bytes) -> 'BasePacket':
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
