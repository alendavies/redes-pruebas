from socket import *
import time
from config import *
from packet import *
from protocol import Connection

class ServerConnection:
    """
    Handles the server side of things.
    """

    def __init__(self, connection: Connection):
        self.connection = connection

    def handle(self, incoming: bytes):
        """
        Initiates the handling of an incoming message.

        This message should be either a read or write request,
        in which cases they will be handled.

        Otherwise, it throws an unexpected packet type exception.

        Returns... ¿algo?
        """
        raise NotImplementedError

    def _handle_read_request(self, request: ReadRequestPacket):
        """
        Handles the read request.

        Begins the transmission of the requested resource, \
        if the request is valid. 

        Otherwise, it throws an appropiate error.
        # TODO: acá tenemos que manejar los casos (file not found...)

        Returns... ¿algo?
        """
        raise NotImplementedError

    def _handle_write_request(self, request: WriteRequestPacket):
        """
        Handles the write request.

        Acknowledges the request if it is valid, and waits for \
        the transmission of the resource.

        Otherwise, throws appropiate exception.
        # TODO: acá manejamos los casos (file too large x ej)

        Returns... ¿algo?
        """
        raise NotImplementedError
