from lib.loggers.BaseLogger import BaseLogger

class ClientSideLogger(BaseLogger):

    def __init__(self):
        super().__init__("Client")

