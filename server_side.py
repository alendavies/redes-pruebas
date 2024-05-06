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

    def __init__(self, connection: Connection, logger = PacketLogger(), file_service = FileService()):
        self.connection = connection
        self.logger = logger
        self.file_service = file_service

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
            # TODO: try except
            self._handle_write_request(instance)

        elif isinstance(instance, ReadRequestPacket):
            self.logger.debug("Received read request for file: " + instance.get_filename())
            # TODO: try except
            self._handle_read_request(instance)

        else:
            self.logger.error("Unexpected packet type")
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
            file = self.file_service.get_file(request.get_filename())
        except:
            # TODO: enviar error
            raise Exception("File not found")

        rrq_ack = AckReadRequest(file.get_size())

        try:
            ack_0 = self._send_read_request_ack_and_wait_for_ack0(rrq_ack)
        except Exception as e:
            self.logger.error(e)
            raise Exception("Error sending ack for read request")

        try:
            result = self.connection.send_file(file.get_data())
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
        # attempts = 0
        # received = False
        # 
        # # Send the ackowledgement for the write request
        # while attempts < MAX_ATTEMPTS and received == False:
        #
        #     try:
        #         self.connection.send_ACK(0)
        #         # print("Waiting for first data packet")
        #         packet = self._wait_first_data_packet()
        #
        #         if isinstance(packet, DataPacket):
        #             # print("Received first data packet")
        #             received = True
        #
        #     except custom_errors.Timeout:
        #         attempts += 1
        #         self.logger.warning("Timeout")
        #         # print("Timeout, resending ACK")

        # TODO: chequear con el file service q esté todo ok en la request

        # self.connection.send(AckWriteRequest())

        try:
            # print("Receiving file")
            file = self.connection.receive_file(0)
            print(file)
        except:
            raise Exception("Error receiving file")

    def _send_read_request_ack_and_wait_for_ack0(self, \
        rrq_ack: AckReadRequest) -> AckPacket:
        """
        Waits MAX_TIME for the acknowledgment of the read
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        self.connection.send(rrq_ack)
        self.logger.debug(rrq_ack.__str__())

        while True:
            try:
                packet, _ = self.connection.receive()

                if isinstance(packet, AckPacket):
                    if packet.get_block_number() == 0:
                        return packet

                elif isinstance(packet, ErrorPacket):
                    print("Received error packet")
                    # TODO: narrow this exception, define protocol errors
                    raise Exception

            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= TIMEOUT:
                self.logger.warning("Timeout: ack for 0 not received")
                raise custom_errors.Timeout
