from socket import *
import time
from logger import ClientSideLogger
from packet import *
from config import *
from protocol import Connection
import custom_errors

# TODO: documentar bien y loguear

class ClientSide:

    def __init__(self, connection: Connection):
        self.connection = connection
        self.logger = ClientSideLogger()

    def initiate_read_request(self, filename: str):

        self.logger.debug("Initiating read request")

        packet_req = ReadRequestPacket(filename)

        attempts = 0
        received = False
        req_ack = None

        while attempts <= MAX_ATTEMPTS and received == False:

            self.logger.debug("Attempt number: " + str(attempts))

            try:
                self.connection.send(packet_req)
                req_ack = self._wait_read_req_ack()

                if isinstance(req_ack, DataPacket):
                    self.logger.debug("Received first data packet")
                    received = True

            except custom_errors.Timeout:
                self.logger.warning("Read request timed out.")
                attempts+=1

            except custom_errors.ErrorPacket:
                raise custom_errors.ErrorPacket

        if attempts == MAX_ATTEMPTS:
            self.logger.error("Could not establish connection with the server.")
            raise custom_errors.ReadRequestNotAcknowledged

        # By this point, the read request is supposed to ack, by
        # having received the first packet.

        if not req_ack:
            self.logger.error("Request not acknowledged.")
            raise Exception

        try:
            file = self.connection.receive_file(req_ack.get_block_number(), req_ack.get_data())

        except Exception as e:
            # TODO: Acá manejar error
            self.logger.error(e)
            raise Exception

        return file

    def initiate_write_request(self, file: bytes, filename):

        self.logger.debug("Initiating write request")
        packet_req = WriteRequestPacket(filename)

        attempts = 0
        received = False

        while attempts <= MAX_ATTEMPTS and received == False:

            self.logger.debug("Attempt number: " + str(attempts))

            try:
                self.connection.send(packet_req)
                req_ack = self._wait_write_req_ack()

                if isinstance(req_ack, AckPacket):
                    self.logger.debug("Received ackowledgement packet")
                    received = True

            except custom_errors.Timeout:
                attempts+=1
                self.logger.warning("Read request timed out.")

            except custom_errors.ErrorPacket:
                print("Error packet received")
                raise custom_errors.ErrorPacket

        if attempts == MAX_ATTEMPTS:
            self.logger.error("Could not establish connection with the server.")
            raise custom_errors.WriteRequestNotAcknowledged

        # By this point, the writr request is supposed to ack, by
        # having received the first packet.

        try:
            result = self.connection.send_file(file)

        except Exception as e:
            # TODO: Acá manejar error
            self.logger.error(e)
            raise Exception

        return result


    def _wait_write_req_ack(self) -> AckPacket:
        """
        Waits MAX_TIME for the acknowledgment of the write
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        while True:
            try:
                packet, server_addr = self.connection.receive()

                if isinstance(packet, AckPacket):
                    print("Received ACK packet")
                    self.connection.ip = server_addr[0]
                    self.connection.port = server_addr[1]
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
                # TODO: throw
                break

        raise custom_errors.Timeout

    def _wait_read_req_ack(self) -> DataPacket:
        """
        Waits MAX_TIME for the acknowledgment of the read
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        while True:
            try:
                packet, server_addr = self.connection.receive()

                if isinstance(packet, DataPacket):
                    if packet.get_block_number() == 0:
                        print("Received first data packet")
                        self.connection.ip = server_addr[0]
                        self.connection.port = server_addr[1]
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
