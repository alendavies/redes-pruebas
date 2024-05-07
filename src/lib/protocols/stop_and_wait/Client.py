import time

from lib.Connection import Connection
from lib.FileService import ClientFileService
from lib.packets.AckPacket import AckPacket
from lib.packets.constants import PACKET_SIZE
from lib.packets.DataPacket import DataPacket
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolClient import ProtocolClient


class Client(ProtocolClient):

    def __init__(self, connection: Connection, file_service: ClientFileService):
        super().__init__(connection, file_service)

    def upload(self, source: str, filename: str):

        # Try to get file. Send ERROR and raise if fails.
        file = self.file_service.get_file_local(source) # TODO: add file exceptions
        data = bytearray(file)

        # Send request and wait for ack0.
        req_packet = UploadRequestPacket(filename)

        try:
            self._send_write_req_and_wait_for_ack0(req_packet)
        except Exception as e:
            self.logger.error(e)
            raise Exception("Couldn't connect to the server.")

        # Receive file.

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

    def download(self, destination: str, filename: str):
        data = bytearray()

        req_packet = DownloadRequestPacket(filename)

        try:
            data_packet = self._send_read_req_and_wait_for_first_data_block(req_packet)
            data.extend(data_packet.get_data())

        except Exception as e:
            self.logger.error(e)
            raise Exception("Couldn't connect to the server.")

        bloqnum = 1

        es_ultimo = False

        # TODO: attempts

        while not es_ultimo:

            if data_packet.is_final_packet():
                es_ultimo = True
                self.logger.debug("That was the last packet.")
                # TODO: esperar un timeout por si no llega el ack
                self.connection.send(AckPacket(data_packet.get_block_number()))
                print("Data received: ", data)
                # TODO: wait few seconds in case ack is lost
                break
            try:
                ack_packet = AckPacket(bloqnum)
                data_packet = self._send_ack_and_wait_for_data_packet(ack_packet)

                data.extend(data_packet.get_data())

            except Exception as e:
                self.logger.error(f"Error con paquete: {e}")
                break

            bloqnum += 1

        self.file_service.save_file_local(destination, data)

    def _send_ack_and_wait_for_data_packet(self, ack_packet: AckPacket, timeout = 2) -> DataPacket:
        """
        Sends an `AckPacket` for the `expected_bloqnum` and \
        waits `timeout` seconds for the data packet with \
        `expected_bloqnum`.
        Returns the `DataPacket` with said `expected_bloqnum`. MAL, es más uno! Corregir descripción!
        Otherwise, raises a Timeout exception.
        TODO: manejar EOF
        """
        start_time = time.time()

        self.connection.send(ack_packet)

        while True:
            try:
                packet, _ = self.connection.receive()

                if isinstance(packet, DataPacket):
                    if packet.get_block_number() == ack_packet.get_block_number() + 1:
                        return packet

                # TODO: check for error pacekt
            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= timeout:
                self.logger.warning("Timeout: data block #{bloqnum} not received".format(bloqnum = str(ack_packet.get_block_number())))
                raise TimeoutError("Timeout: data block #{bloqnum} not received".format(bloqnum = str(ack_packet.get_block_number())))

    def _send_read_req_and_wait_for_first_data_block(self, \
        rdq_packet: DownloadRequestPacket) -> DataPacket:

        start_time = time.time()
        self.connection.send(rdq_packet)

        while True:
            try:
                packet, server_addr = self.connection.receive()

                if isinstance(packet, DataPacket):
                    if packet.get_block_number() == 1:
                        self.connection.ip = server_addr[0]
                        self.connection.port = server_addr[1]
                        return packet

            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= 2:
                self.logger.warning("Timeout: first data block not received.")
                raise TimeoutError


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
