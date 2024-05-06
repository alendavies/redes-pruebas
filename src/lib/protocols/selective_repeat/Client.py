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
    PACKET_TIMEOUT = 1

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
        last = len(data) // PACKET_SIZE + 1
        print(last)
        sent_last = False

        # TODO: se puede hacer más elegante lo del timestamp
        # si el data packet tiene un atributo timestamp
        # y cuando se envía, se le setea sólo... pienso...

        while len(in_flight) > 0 or next <= last:
            # Mando paquetes hasta llenar la ventana.
            while next - base + 1 < self.WINDOW_SIZE and not sent_last:
                offset = (next-1) * PACKET_SIZE

                # El contenido del paquete es PACKET_SIZE,
                # o menos si es el último.
                if len(data[offset:]) < PACKET_SIZE:
                    chunk = data[offset:]
                else:
                    chunk = data[offset:offset+PACKET_SIZE]

                data_packet = DataPacket(next, chunk)
                self.connection.send(data_packet)

                in_flight.append((data_packet, time.time()))
                
                # Si acabo de mandar el último, no aumento más la ventana.
                # No se van a mandar más paquetes.
                if data_packet.is_final_packet():
                    sent_last = True
                next += 1

            for packet, timestamp in in_flight:
                if time.time() - timestamp > self.PACKET_TIMEOUT:
                    self.connection.send(packet)
                    timestamp = time.time()

            try:
                packet, _ = self.connection.receive()
            except Exception:
                continue
            
            if isinstance(packet, AckPacket):
                # Saco el paquete acknowledged the in_flight.
                for i in range(len(in_flight)):
                    if in_flight[i][0].get_block_number() == packet.get_block_number():
                        in_flight.pop(i)
                        break
                # Si el paquete acknowledgeado es el base, actualizo la base al primero in_flight.
                if packet.get_block_number() == base:
                    base = in_flight[0][0].get_block_number()
            


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
