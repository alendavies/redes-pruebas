from lib.FileService import ClientFileService
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.constants import PACKET_SIZE
from lib.protocols.ProtocolClient import ProtocolClient
from lib.Connection import Connection
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.packets.AckPacket import AckPacket
from lib.packets.DataPacket import DataPacket

import time

class Client(ProtocolClient):

    # esto a SelectiveRepeatClass
    WINDOW_SIZE = 5 
    PACKET_TIMEOUT = 1
    MAX_ATTEMPTS = 5

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

        # Paquetes en vuelo, tuplas de DataPacket, timestamp. 
        in_flight: list[tuple[DataPacket, float, int]] = []
        base = 1 # first block in the window
        next = 1 # next block to be sent
        last = len(data) // PACKET_SIZE + 1
        sent_last = False

        # TODO: se puede hacer más elegante lo del timestamp
        # si el data packet tiene un atributo timestamp
        # y cuando se envía, se le setea sólo... pienso...

        while len(in_flight) > 0 or next <= last:
            # Mando paquetes hasta llenar la ventana.
            while next - base + 1 < self.WINDOW_SIZE and not sent_last:
                offset = (next-1) * PACKET_SIZE
                self.logger.debug("OFFSET: " + str(offset))

                # El contenido del paquete es PACKET_SIZE,
                # o menos si es el último.
                if len(data[offset:]) < PACKET_SIZE:
                    chunk = data[offset:]
                else:
                    chunk = data[offset:offset+PACKET_SIZE]

                data_packet = DataPacket(next, chunk)
                self.connection.send(data_packet)

                in_flight.append((data_packet, time.time(), 0))
                
                if data_packet.is_final_packet():
                    sent_last = True
                next += 1

            for packet, timestamp, attempts in in_flight:
                if attempts >= self.MAX_ATTEMPTS:
                    self.logger.error("Max attempts reached.")
                    raise Exception("Max attempts reached.")
                if time.time() - timestamp > self.PACKET_TIMEOUT:
                    self.connection.send(packet)
                    timestamp = time.time()

            # TODO: esto podría ser un while receive
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
                if len(in_flight) > 0 and packet.get_block_number() == base:
                    base = in_flight[0][0].get_block_number()
            

    def download(self, destination: str, filename: str):

        req_packet = DownloadRequestPacket(filename)

        try:
            packet = self._send_read_req_and_wait_for_some_data_block(req_packet)
        except Exception as e:
            self.logger.error(e)
            raise Exception("Couldn't connect to the server.")
            
        temp_file = bytearray()
        acknowledged = {}
        continue_receiving = True

        # TODO: data packet get_block_offset()
        # aux function que haga receive y valide que sea un data

        while continue_receiving:
            if isinstance(packet, DataPacket):
                n = packet.get_block_number()
                self.connection.send(AckPacket(n))

                if n not in acknowledged:
                    temp_file[n*PACKET_SIZE:n*PACKET_SIZE] = packet.get_data()
                    acknowledged[n] = True

                if len(packet.data) < PACKET_SIZE:
                    continue_receiving = False
                    self.logger.debug("Last packet received.")
                    for i in range(1, packet.block_number):
                        if i not in acknowledged:
                            continue_receiving = True
                            break
                    print("Continue receiving is: " + str(continue_receiving))
            else:
                self.logger.warning("Unexpected packet received.")

            try:
                packet, _ = self.connection.receive()
            except BlockingIOError:
                pass
            except Exception as e:
                self.logger.error("Error receiving packets: " + str(e))

        self.file_service.save_file_local(destination, temp_file)

        # TODO: add logger tpo file service

    def _send_read_req_and_wait_for_some_data_block(self, rrq_packet: DownloadRequestPacket) -> DataPacket:
        start_time = time.time()
        self.connection.send(rrq_packet)

        while True:
            try:
                packet, server_addr = self.connection.receive()

                if isinstance(packet, DataPacket):
                    self.connection.ip = server_addr[0]
                    self.connection.port = server_addr[1]
                    return packet
            except BlockingIOError:
                pass

            elapsed_time = time.time() - start_time

            if elapsed_time >= 2: # TODO: global timeout
                self.logger.warning("Timeout: never received data.")
                # raise custom_errors.Timeout
                raise TimeoutError # TODO: exceptions


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
