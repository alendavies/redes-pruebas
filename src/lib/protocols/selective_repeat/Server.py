from lib.Connection import Connection
from lib.FileService import FileService
from lib.packets.AckPacket import AckPacket
from lib.packets.constants import PACKET_SIZE
from lib.packets.DataPacket import DataPacket
from lib.packets.DownloadRequestPacket import DownloadRequestPacket
from lib.packets.UploadRequestPacket import UploadRequestPacket
from lib.protocols.ProtocolServer import ProtocolServer


class Server(ProtocolServer):

    def __init__(self, connection: Connection, file_service: FileService):
        super().__init__(connection, file_service)

    def _handle_upload(self, packet_req: UploadRequestPacket):

        self.logger.debug("Handling upload request for file: " + packet_req.get_filename())

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
                raise TimeoutError("Timeout error: no packets received in the last 30 seconds.")

            except BlockingIOError:
                pass
            except Exception as e:
                self.logger.error("Error receiving packets: " + str(e))

        try:
            self.file_service.save_file(packet_req.get_filename(), temp_file)
        except Exception as e:
            self.logger.error("Error saving file: " + str(e))


    def _handle_download(self, packet: DownloadRequestPacket):
        # get file
        # transmit file
        raise NotImplementedError("Not implemented.")

