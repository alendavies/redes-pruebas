from enum import IntEnum

PACKET_SIZE = 512
MAX_ATTEMPTS = 3


class Type(IntEnum):
    READ_REQUEST = 1
    WRITE_REQUEST = 2
    DATA = 3
    ACKOWLEDGMENT = 4
    ERROR = 5
