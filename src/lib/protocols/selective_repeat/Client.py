from lib.packets.constants import PACKET_SIZE
from lib.protocols.ProtocolClient import ProtocolClient
from lib.FileService import FileService
from lib.Connection import Connection
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.packets.AckPacket import AckPacket
from lib.packets.DataPacket import DataPacket

import time

class Client(ProtocolClient):

    WINDOW_SIZE = 10

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def upload(self, filename: str):

        # Try to get file. Send ERROR and raise if fails.
        file = self.file_service.get_file(filename) # TODO: add file exceptions
        data = bytearray(file)

        # Send request and wait for ack0.
        req_packet = UploadRequestPacket(filename)

        try:
            self._send_write_req_and_wait_for_ack0(req_packet)
        except Exception as e:
            self.logger.error(e)
            raise Exception("Couldn't connect to the server.")

        # Paquetes en vuelo, tuplas de DataPacket, timestamp. 
        in_flight: list[tuple[DataPacket, float]] = []
        base = 1 # first block in the window
        next = 1 # next block to be sent

        # TODO: se puede hacer más elegante lo del timestamp
        # si el data packet tiene un atributo timestamp
        # y cuando se envía, se le setea sólo... pienso...

        while True:
            # Mando paquetes hasta llenar la ventana.
            while next - base < self.WINDOW_SIZE:
                offset = (next-1) * PACKET_SIZE
                chunk = data[offset:offset+PACKET_SIZE]

                data_packet = DataPacket(next, chunk)
                self.connection.send(data_packet)

                in_flight.append((data_packet, time.time()))
                next += 1


        # transmit file
        # mientras haya paquetes en vuelo O queden paquetes por mandar
        # mandar paquetes hasta llenar la ventana
        # recibir acks, sacarlos de inflight y actualizar base

    def download(self, filename: str):
        # send download request
        # wait for first data block
        # process first data block

        # continue receiving data blocks
        raise NotImplementedError("Not implemented.")

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
