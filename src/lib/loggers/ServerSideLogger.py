from lib.loggers.BaseLogger import BaseLogger

class ServerSideLogger(BaseLogger):

    def __init__(self):
        super().__init__("Server")
