from enum import IntEnum

<<<<<<< Updated upstream
PACKET_SIZE = 512
MAX_ATTEMPTS = 3
=======
# PACKET_SIZE = 512
PACKET_SIZE = 5
>>>>>>> Stashed changes


class Type(IntEnum):
    READ_REQUEST = 1
    WRITE_REQUEST = 2
    DATA = 3
    ACKOWLEDGMENT = 4
    ERROR = 5
