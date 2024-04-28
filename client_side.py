from socket import *
import time
from packet import *
from config import *
from protocol import Connection
import custom_errors

# TODO: documentar bien y loguear

class ClientSide:

    def __init__(self, connection: Connection):
        self.connection = connection

    def initiate_read_request(self, filename: str):

        packet_req = ReadRequestPacket(filename)
        self.connection.send(packet_req.serialize())

        attempts = 0

        while attempts <= MAX_ATTEMPTS:

            try:
                req_ack = self._wait_read_req_ack()

            except custom_errors.Timeout:
                attempts+=1
                print("couldt connect with the server")

            """ except custom_errors.ErrorPacket:
                print("Error packet received")
                raise custom_errors.ErrorPacket """

        if attempts == MAX_ATTEMPTS:
            raise custom_errors.ReadRequestNotAcknowledged

        # By this point, the read request is supposed to ack, by
        # having received the first packet.

        try:
            file = self.connection.receive_file(req_ack.get_block_number(), req_ack.get_data())

        except Exception as e:
            # TODO: Acá manejar error
            print(e)
            raise Exception

        return file

    def initiate_write_request(self, bytes: bytes):

        packet_req = WriteRequestPacket(bytes)
        self.connection.send(packet_req.serialize())

        attempts = 0

        while attempts <= MAX_ATTEMPTS:

            try:
                req_ack = self._wait_write_req_ack()

            except custom_errors.Timeout:
                attempts+=1
                print("couldt connect with the server")

            """ except custom_errors.ErrorPacket:
                print("Error packet received")
                raise custom_errors.ErrorPacket """

        if attempts == MAX_ATTEMPTS:
            raise custom_errors.WriteRequestNotAcknowledged

        # By this point, the write request is supposed to ack, by
        # having received the first packet.

        try:
            result = self.connection.send_file(bytes)

        except Exception as e:
            # TODO: Acá manejar error
            print(e)
            raise Exception

        return result


    def _wait_write_req_ack(self) -> AckWriteRequest:
        """
        Waits MAX_TIME for the acknowledgment of the write
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        while True:
            try:
                packet, _ = self.connection.receive()
                if isinstance(packet, AckPacket):
                    print("Received ACK packet")
                    return packet

                elif isinstance(packet, ErrorPacket):
                    print("Received error packet")
                    # TODO: narrow this exception, define protocol errors
                    raise Exception

                else:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= TIMEOUT:
                        print("Max time reached")
                        # TODO: throw
                        break

            except BlockingIOError:
                pass

        raise custom_errors.Timeout

    def _wait_read_req_ack(self) -> DataPacket:
        """
        Waits MAX_TIME for the acknowledgment of the read
        request, while ignoring any other packet received.
        """
        start_time = time.time()

        while True:
            try:
                packet, _ = self.connection.receive()
                if isinstance(packet, DataPacket):
                    if packet.get_block_number() == 0:
                        print("Received first data packet")
                        return packet

                elif isinstance(packet, ErrorPacket):
                    print("Received error packet")
                    # TODO: narrow this exception, define protocol errors
                    raise Exception

                else:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= TIMEOUT:
                        print("Max time reached")
                        break

            except BlockingIOError:
                pass

        raise custom_errors.Timeout
