from http import client
from socket import *
import time
from config import *
from file_service import FileService
from logger import PacketLogger
from packet import *
from protocol import Connection
import custom_errors

class ServerConnection:
    """
    Handles the server side of things.
    """

    def __init__(self, connection: Connection):
        self.connection = connection
        self.logger = PacketLogger()

    def handle(self, packet: bytes):
        """
        Initiates the handling of an incoming message.

        This message should be either a read or write request,
        in which cases they will be handled.

        Otherwise, it throws an unexpected packet type exception.

        Returns... ¿algo?
        """

        instance = MasterOfPackets.get_packet(packet)

        if isinstance(instance, WriteRequestPacket):
            self.logger.debug("Received write request for file: " + instance.get_filename())
            self._handle_write_request(instance)

        elif isinstance(instance, ReadRequestPacket):
            self.logger.debug("Received read request for file: " + instance.get_filename())
            self._handle_read_request(instance)

        else:
            raise Exception("Unexpected packet type")


    def _handle_read_request(self, request: ReadRequestPacket):
        """
        Handles the read request.

        Begins the transmission of the requested resource, \
        if the request is valid.

        Otherwise, it throws an appropiate error.
        # TODO: acá tenemos que manejar los casos (file not found...)

        Returns... ¿algo?
        """
        try:
            file = FileService.get_file(request.get_filename())
        except:
            raise Exception("File not found")

        try:
            print("sending file")
            result = self.connection.send_file(file)
            print("File sent")
        except:
            raise Exception("Error sending file")


    def _handle_write_request(self, request: WriteRequestPacket):
        """
        Handles the write request.

        Acknowledges the request if it is valid, and waits for \
        the transmission of the resource.

        Otherwise, throws appropiate exception.
        # TODO: acá manejamos los casos (file too large x ej)

        Returns... ¿algo?
        """
        attempts = 0
        received = False

        while attempts < MAX_ATTEMPTS and received == False:

            try:
                self.connection.send_ACK(0)
                print("Waiting for first data packet")
                packet = self._wait_first_data_packet()

                if isinstance(packet, DataPacket):
                    print("Received first data packet")
                    received = True

            except custom_errors.Timeout:
                attempts += 1
                print("Timeout, resending ACK")

        try:
            print("Receiving file")
            file = self.connection.receive_file(packet.get_block_number(), packet.get_data())
            print(file)
        except:
            raise Exception("Error receiving file")


    def _wait_first_data_packet(self) -> DataPacket:
        """
        Waits MAX_TIME for the acknowledgment of the read
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        while True:
            try:
                packet, _ = self.connection.receive()
                print("Received packet: ", packet)

                if isinstance(packet, DataPacket):
                    if packet.get_block_number() == 0:
                        print("Received first data packet")
                        return packet

                elif isinstance(packet, ErrorPacket):
                    print("Received error packet")
                    # TODO: narrow this exception, define protocol errors
                    raise Exception

            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time
            if elapsed_time >= TIMEOUT:
                print("Max time reached")
                break

        raise custom_errors.Timeout

