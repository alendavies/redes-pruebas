from lib.Connection import Connection
from lib.FileService import ServerFileService
from lib.packets.AckPacket import AckPacket
from lib.packets.constants import PACKET_SIZE
from lib.packets.DataPacket import DataPacket
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolServer import ProtocolServer
import time
from typing import TypedDict

class TypeInFlight(TypedDict):
    packet: DataPacket
    timestamp: float
    attempts: int

class Server(ProtocolServer):

    WINDOW_SIZE = 5
    PACKET_TIMEOUT = 1
    MAX_ATTEMPTS = 10

    def __init__(self, connection: Connection, file_service: ServerFileService):
        super().__init__(connection, file_service)

    def _handle_upload(self, req_packet: UploadRequestPacket):

        self.logger.debug("Handling upload request for file: " + req_packet.get_filename())

        temp_file = bytearray()
        acknowledged = {}

        ack0 = AckPacket(0)
        self.connection.send(ack0)
        continue_receiving = True

        while continue_receiving is True:

            try:
                packet, _ = self.connection.receive()
                if not isinstance(packet, DataPacket):
                    self.logger.error("Unexpected packet received.")
                    continue
                n = packet.block_number
                self.connection.send(AckPacket(n))

                if n not in acknowledged:
                    temp_file[n*PACKET_SIZE:n*PACKET_SIZE] = packet.data
                    acknowledged[n] = True

                if len(packet.data) < PACKET_SIZE:
                    continue_receiving = False
                    self.logger.debug("Last packet received.")
                    for i in range(1, packet.block_number):
                        if i not in acknowledged:
                            continue_receiving = True
                            break
                    print("Continue receiving is: " + str(continue_receiving))
            except TimeoutError:
                # TODO: ? esto funca? dónde tira tiemeout?
                raise TimeoutError("Timeout error: no packets received in the last 30 seconds.")

            except BlockingIOError:
                pass
            except Exception as e:
                self.logger.error("Error receiving packets: " + str(e))

        try:
            self.file_service.save_file_on_server(req_packet.get_filename(), temp_file)
        except Exception as e:
            self.logger.error("Error saving file: " + str(e))


    def _handle_download(self, req_packet: DownloadRequestPacket):

        # TODO: try exccept
        data = self.file_service.get_file_from_server(req_packet.get_filename())

        # Paquetes en vuelo, tuplas de DataPacket, timestamp. 
        # TypeInFlight = {
        #         "packet": DataPacket,
        #         "timestamp": float,
        #         "attempts": int
        # }
        in_flight: list[TypeInFlight] = []
        base = 1 # first block in the window
        next = 1 # next block to be sent
        last = len(data) // PACKET_SIZE + 1
        sent_last = False


        while len(in_flight) > 0 or next <= last:
            print("in_flight: {}, base: {}, next: {}, last: {}".format(len(in_flight), base, next, last))
            # Mando paquetes hasta llenar la ventana.
            # TODO: revisar este + 1
            while next - base < self.WINDOW_SIZE and not sent_last:
                offset = (next-1) * PACKET_SIZE
                # self.logger.debug("OFFSET: " + str(offset))

                # El contenido del paquete es PACKET_SIZE,
                # o menos si es el último.
                if len(data[offset:]) < PACKET_SIZE:
                    chunk = data[offset:]
                else:
                    chunk = data[offset:offset+PACKET_SIZE]

                data_packet = DataPacket(next, chunk)
                self.connection.send(data_packet)

                in_flight.append({"packet": data_packet, "timestamp": time.time(), "attempts": 0})
                
                # Si acabo de mandar el último, no aumento más la ventana.
                # No se van a mandar más paquetes.
                if data_packet.is_final_packet():
                    sent_last = True
                next += 1

            for p in in_flight:
                if p["attempts"] >= self.MAX_ATTEMPTS:
                    self.logger.error("Max attempts reached.")
                    raise Exception("Max attempts reached.")
                if time.time() - p["timestamp"] > self.PACKET_TIMEOUT:
                    self.logger.warning("Sending packet again: " + str(p["packet"].get_block_number()))
                    self.connection.send(p["packet"])
                    p["timestamp"]= time.time()
                    p["attempts"] += 1

            try:
                packet, _ = self.connection.receive()
            except Exception:
                continue
            
            if isinstance(packet, AckPacket):
                # Saco el paquete acknowledged the in_flight.
                for i in range(len(in_flight)):
                    if in_flight[i]["packet"].get_block_number() == packet.get_block_number():
                        in_flight.pop(i)
                        break
                # Si el paquete acknowledgeado es el base, actualizo la base al primero in_flight.
                if len(in_flight) > 0 and packet.get_block_number() == base:
                    base = in_flight[0]["packet"].get_block_number()

