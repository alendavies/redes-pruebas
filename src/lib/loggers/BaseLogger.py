import logging
from enum import Enum

logging.basicConfig(level = logging.DEBUG, format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")


class LogType(Enum):
    TRACE = 1,
    DEBUG = 2,
    INFO = 3,
    WARNING = 4,
    ERROR = 5,
    CRITICAL = 6

class VerbosityLevel(Enum):
    QUIET = 1
    NORMAL = 2
    VERBOSE = 3

class Colors(Enum):
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    PURPLE = "\x1b[35m"
    GRAY = "\x1b[35m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    # GRAY = "\033[0;37m"
    RESET = "\x1b[0m"

class BaseLogger:

    def __init__(self, name: str):
        logger = logging.getLogger(name)
        # logger.setLevel(logging.DEBUG)
        self.logger = logger

    def log(self, message: str, color: Colors):
        return "{color} {message} {reset}".format(color=color.value, message=message, reset=Colors.RESET.value)

    def critical(self, message):
        self.logger.critical(self.log(message, Colors.PURPLE))

    def debug(self, message):
        self.logger.debug(self.log(message, Colors.GRAY))

    def error(self, message):
        self.logger.error(self.log(message, Colors.RED))

    def success(self, message):
        self.logger.info(self.log(message, Colors.GREEN))

    def info(self, message):
        self.logger.info(self.log(message, Colors.CYAN))

    def warning(self, message):
        self.logger.warning(self.log(message, Colors.YELLOW))


    def on_max_retries(self):
        pass

    def on_ack_timeout(self):
        pass

    def on_unexpected_packet(self):
        pass

    def on_unhandled_exception(self, e: Exception):
        pass
