import time
from packet import *
from protocol import *
from config import *


class StopAndWait(Connection):

    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    def trap(self, bloqnum) -> int:

        # Esperar ACK o alcanzar el tiempo de espera
        start_time = time.time()

        while True:

            try:
                packet, _ = self.receive()
                if isinstance(packet, AckPacket):
                    if packet.get_block_number() == bloqnum:
                        print("Received ACK packet")
                        return bloqnum+1
                else:
                    # Verificar si se ha excedido el tiempo máximo de espera
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= TIMEOUT:
                        print("Tiempo de espera excedido")
                        break
            except BlockingIOError as e:
                pass

        return bloqnum

    def send_file(self, message: bytes) -> bool:

        data = bytearray(message)

        bloqnum = 0
        es_ultimo = False
        attempts = 0

        while es_ultimo == False and attempts <= MAX_ATTEMPTS:

            if len(data[bloqnum*PACKET_SIZE:]) < PACKET_SIZE:

                chunk = data[bloqnum*PACKET_SIZE:]
                es_ultimo = True

            else:
                chunk = data[bloqnum*PACKET_SIZE:(bloqnum+1) * PACKET_SIZE]

            data_packet = DataPacket(bloqnum, chunk)
            self.socket.send(data_packet.serialize())
            print("DATA packet sent")

            prev_bloqnum = bloqnum

            bloqnum = self.trap(bloqnum)

            if prev_bloqnum == bloqnum:
                attempts+=1
            else:
                attempts = 0

        if es_ultimo == True:
            print("Final packet sent")
            return True

        if attempts == MAX_ATTEMPTS:
            print("Max attempts reached")
            # acá debería raise, not true / false
            return False

        return True

    def receive_file(self, initial_bloqnum = 0, initial_data = b'') -> bytes:

        bufer: list[bytes] = []

        while True:

            packet, _ = self.receive()
            packet = MasterOfPackets.get_packet(packet)

            if isinstance(packet, DataPacket):

                print("Received DATA packet: ", packet)

                bufer.append(packet.get_data())

                self.send_ACK(packet.get_block_number())

                if packet.is_final_packet():
                    print("Final packet received")
                    return b''.join(bufer)

            else:

                # TODO: Implementar manejo de errores
                # Lo mismo que trap pero para DataPacket??
                # Si no me llega un data packet seguir esperando hasta timeout?

                raise Exception("Unexpected packet type")

            # TODO: escribir archivo con la data recibida
