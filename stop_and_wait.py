import time
from packet import *
from protocol import *
from config import *
import custom_errors


class StopAndWait(Connection):

    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    # def _retry_n_times()

    def receive_file(self, initial_bloqnum = 0, initial_packet = None) -> bytes:
        """
        Receives a file using the Stop and Wait protocol.

        It begins by acknowledging the `initial_bloqnum`th \
        packet and waiting for the next one.
        """

        self.logger.debug("Beggining file reception")

        bufer: list[bytes] = []

        bloqnum = initial_bloqnum

        while True:

        # TODO: agregar attempts
            try:
                packet = self._send_ack_and_wait_for_data_packet(AckPacket(bloqnum))
            # TODO: manejar EOF
            except Exception as e:
                self.logger.error("Never received expected packet with block number {}".format(str(initial_bloqnum)))
                raise Exception("Nunca se recibió {}".format(str(bloqnum)))

            bufer.append(packet.get_data())

            if packet.is_final_packet():
                self.logger.debug("That was the last packet.")
                break

            bloqnum += 1

        return b''.join(bufer)
        
    def send_file(self, data: bytes):
        """
        Sends the file in `data` using the Stop and Wait protocol.
        """

        self.logger.debug("Beggining file transfer")

        # data = bytearray(data)
        
        bloqnum = 1
        es_ultimo = False
       
        # TODO: add attempts
        while not es_ultimo:

            offset = (bloqnum-1) * PACKET_SIZE

            if len(data[offset:]) < PACKET_SIZE:

                chunk = data[offset:]
                es_ultimo = True

            else:
                chunk = data[offset:offset+PACKET_SIZE]
            
            try:
                ack_packet = self._send_data_packet_and_wait_for_ack(DataPacket(bloqnum, chunk))
            except Exception as e:
                self.logger.error(e)
                raise Exception("Nunca se recibió ack del paquete {}".format(str(bloqnum)))

            bloqnum += 1

    def _send_ack_and_wait_for_data_packet(self, ack_packet: AckPacket, timeout = TIMEOUT) -> DataPacket:
        """
        Sends an `AckPacket` for the `expected_bloqnum` and \
        waits `timeout` seconds for the data packet with \
        `expected_bloqnum`.

        Returns the `DataPacket` with said `expected_bloqnum`. MAL, es más uno! Corregir descripción!

        Otherwise, raises a Timeout exception.


        TODO: manejar EOF 
        """
        start_time = time.time()

        self.send(ack_packet)

        while True:
            try:
                packet, _ = self.receive()

                if isinstance(packet, DataPacket):
                    if packet.get_block_number()  == ack_packet.get_block_number() + 1:
                        return packet

                # TODO: check for error pacekt
            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= timeout:
                self.logger.warning("Timeout: data block #{bloqnum} not received".format(bloqnum = str(ack_packet.get_block_number())))
                raise custom_errors.Timeout

    def _send_data_packet_and_wait_for_ack(self, data_packet: DataPacket, timeout = TIMEOUT) -> AckPacket:
        """
        Waits `timeout` seconds for the ackowledgement of the \
        `bloqnum` packet.

        Returns the `AckPacket` for the `bloqnum`.

        Otherwise, raises a Timeout exception.
        """
        start_time = time.time()

        self.send(data_packet)

        while True:
            try:
                packet, _ = self.receive()

                if isinstance(packet, AckPacket):
                    if packet.get_block_number() == data_packet.get_block_number():
                        return packet

            except BlockingIOError as e:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= timeout:
                self.logger.warning("Timeout: #{bloqnum} not acknowledged".format(bloqnum = str(data_packet.get_block_number())))
                raise custom_errors.Timeout


