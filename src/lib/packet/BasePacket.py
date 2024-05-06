from abc import abstractmethod
from typing import Self


class BasePacket:

    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, packet: bytes) -> Self:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
