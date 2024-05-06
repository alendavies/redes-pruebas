from lib.Connection import Connection
from lib.FileService import FileService
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolClient import ProtocolClient
from lib.packets.AckPacket import AckPacket
from lib.packets.DataPacket import DataPacket
from lib.packets.constants import PACKET_SIZE
import time


class Client(ProtocolClient):

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def upload(self, filename: str):
       
        # Send upload request.
        req_packet = UploadRequestPacket(filename)
        file = self.file_service.get_file(filename)
        data = bytearray(file)

        try:
            self._send_write_req_and_wait_for_ack0(req_packet)
        except Exception as e:
            self.logger.error(e)

        bloqnum = 1
        es_ultimo = False

        while not es_ultimo:

            offset = (bloqnum-1) * PACKET_SIZE

            if len(data[offset:]) < PACKET_SIZE:

                chunk = data[offset:]
                es_ultimo = True

            else:
                chunk = data[offset:offset+PACKET_SIZE]

            try:
                self._send_data_packet_and_wait_for_ack(DataPacket(bloqnum, chunk))
            except Exception as e:
                self.logger.error(e)
                raise Exception("Nunca se recibió ack del paquete {}".format(str(bloqnum)))

            bloqnum += 1

    def download(self, filename: str):
        raise NotImplementedError


    def _send_write_req_and_wait_for_ack0(self, \
        wrq_packet: UploadRequestPacket) -> AckPacket:
        """
        Waits MAX_TIME for the acknowledgment of the write
        request, while ignoring any other packet received.
        """

        start_time = time.time()
        self.connection.send(wrq_packet)

        while True:
            try:
                packet, server_addr = self.connection.receive()

                if isinstance(packet, AckPacket):
                    if packet.get_block_number() == 0:
                        self.connection.ip = server_addr[0]
                        self.connection.port = server_addr[1]
                        return packet

                # elif isinstance(packet, ErrorPacket):
                #     # TODO: narrow this exception, define protocol errors
                #     raise Exception

            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= 2: # TODO: global timeout
                self.logger.warning("Timeout: ack for #0 not received.")
                # raise custom_errors.Timeout
                raise TimeoutError # TODO: exceptions

    def _send_data_packet_and_wait_for_ack(self, data_packet: DataPacket, timeout = 2) -> AckPacket:
        """
        Waits `timeout` seconds for the ackowledgement of the \
        `bloqnum` packet.
        Returns the `AckPacket` for the `bloqnum`.
        Otherwise, raises a Timeout exception.
        """
        start_time = time.time()

        self.connection.send(data_packet)

        while True:
            try:
                packet, _ = self.connection.receive()

                if isinstance(packet, AckPacket):
                    if packet.get_block_number() == data_packet.get_block_number():
                        return packet

            except BlockingIOError as e:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= timeout:
                self.logger.warning("Timeout: #{bloqnum} not acknowledged".format(bloqnum = str(data_packet.get_block_number())))
                # raise custom_errors.Timeout
                raise TimeoutError
