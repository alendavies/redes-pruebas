import time

from lib.packets.AckPacket import AckPacket
from lib.packets.constants import MAX_ATTEMPTS, PACKET_SIZE
from lib.packets.DataPacket import DataPacket
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolServer import ProtocolServer


class Server(ProtocolServer):

    def __init__(self, connection, file_service):
        super().__init__(connection, file_service)

    def _handle_upload(self, req_packet: UploadRequestPacket):

        data = bytearray()

        bloqnum = 0
        es_ultimo = False
        attempts = 0

        while not es_ultimo and attempts < MAX_ATTEMPTS:

            try:
                ack_packet = AckPacket(bloqnum)
                data_packet = self._send_ack_and_wait_for_data_packet(ack_packet)

                data.extend(data_packet.get_data())

            except TimeoutError:
                self.logger.warning("Timeout: data block #{bloqnum} not received".format(bloqnum = str(bloqnum)))
                attempts += 1
                continue

            if data_packet.is_final_packet():
                es_ultimo = True
                self.logger.debug("That was the last packet.")
                # TODO: esperar un timeout por si no llega el ack
                self.connection.send(AckPacket(data_packet.get_block_number()))
                print("Data received: ", data)

            bloqnum += 1

        if attempts >= MAX_ATTEMPTS:
            raise Exception("Error: couldn't upload file.")

        try:
            self.file_service.save_file_on_server(req_packet.get_filename(), data)
        except FileExistsError:
            self.logger.error("Error: file already exists")
            raise FileExistsError

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

    def _handle_download(self, req_packet: DownloadRequestPacket):

        try:
            data = self.file_service.get_file_from_server(req_packet.get_filename())
        except FileNotFoundError:
            self.logger.error("Error: file not found")
            raise FileNotFoundError

        bloqnum = 1
        es_ultimo = False
        attempts = 0

        while not es_ultimo and attempts < MAX_ATTEMPTS:

            chunk_size = (bloqnum-1) * PACKET_SIZE

            if len(data[chunk_size:]) < PACKET_SIZE:
                chunk = data[chunk_size:]
                es_ultimo = True

            else:
                chunk = data[chunk_size:chunk_size+PACKET_SIZE]

            try:
                self._send_data_packet_and_wait_for_ack(DataPacket(bloqnum, chunk))
            except TimeoutError:
                self.logger.warning("Timeout: ack {bloqnum} not received".format(bloqnum = str(bloqnum)))
                attempts += 1
                continue

            bloqnum += 1

        if attempts >= MAX_ATTEMPTS:
            raise Exception("Error: couldn't download file.")

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
                raise TimeoutError("Timeout: #{bloqnum} not acknowledged".format(bloqnum = str(data_packet.get_block_number())))
