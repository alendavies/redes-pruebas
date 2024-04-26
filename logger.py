from enum import Enum
import logging

from packet import AckPacket, DataPacket, ReadRequestPacket, WriteRequestPacket


class LogType(Enum):
    TRACE = 1,
    DEBUG = 2,
    INFO = 3,
    WARNING = 4,
    ERROR = 5,
    CRITICAL = 6

class VerbosityLevel(Enum):
    SILENT = 1
    NORMAL = 2
    VERBOSE = 3

class Logger:

    def __init__(self, level: VerbosityLevel):
        self.level = level

    def log(self, message: str, type: LogType):
        pass

    def on_write_request_sent(self, message: WriteRequestPacket):
        pass

    def on_read_request_sent(self, message: ReadRequestPacket):
        pass

    def on_data_sent(self, message: DataPacket):
        pass

    def on_data_received(self, message: DataPacket):
        pass

    def on_first_data_sent(self, message: DataPacket):
        pass

    def on_last_data_sent(self, message: DataPacket):
        pass

    def on_ack_sent(self, message: AckPacket):
        pass

    def on_ack_received(self, message: AckPacket):
        pass

    def on_max_retries(self):
        pass

    def on_ack_timeout(self):
        pass

    def on_unexpected_packet(self):
        pass

    def on_unhandled_exception(self, e: Exception):
        pass
