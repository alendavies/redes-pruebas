from socket import *
import time
from config import *
from packet import *

class ServerSide:

    def __init__(self, server_port):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("", server_port))
        self.socket.setblocking(0)
        print("The server is ready to receive")


    def handle_read_request(self, client_address):

        print("Handling READ REQUEST packet")

        ack_packet = AckPacket(0)
        self.socket.sendto(ack_packet.serialize(), client_address)
        print("ACK packet for request sent")

        data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

        bloqnum = 1
        es_ultimo = False
        attempts = 0

        while es_ultimo == False and attempts <= MAX_ATTEMPTS:

            if len(data[bloqnum*PACKET_SIZE:]) < PACKET_SIZE:

                cacho = data[bloqnum*PACKET_SIZE:].encode()
                es_ultimo = True

            else:
                cacho = data[bloqnum*PACKET_SIZE:(bloqnum+1) * PACKET_SIZE].encode()

            data_packet = DataPacket(bloqnum, cacho)
            self.socket.sendto(data_packet.serialize(), client_address)
            print("DATA packet sent")

            prev_bloqnum = bloqnum
            bloqnum = self.trap(bloqnum, self.socket)

            if prev_bloqnum == bloqnum:
                attempts+=1
            else:
                attempts = 0

        if es_ultimo == True:
            print("Final packet sent")
            return True

        if attempts == MAX_ATTEMPTS:
            print("Max attempts reached")
            return False


    def trap(self, bloqnum, server_socket) -> int:

        # Esperar ACK o alcanzar el tiempo de espera
        max_time = 5  # Tiempo de espera en segundos
        start_time = time.time()

        while True:

            packet, _ = server_socket.recvfrom(2048)

            if isinstance(packet, AckPacket):
                if packet.get_block_number() == bloqnum:
                    print("Received ACK packet")
                    return bloqnum+1
            else:
                # Verificar si se ha excedido el tiempo máximo de espera
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_time:
                    print("Tiempo de espera excedido")
                    break

        return bloqnum


    def handle_write_request(self, client_address):

        print("Handling WRITE REQUEST packet")

        bufer = []

        self.send_ACK(0, client_address)
        print("ACK packet sent for request packet")

        while True:

            packet, client_address = self.socket.recvfrom(2048)
            packet = BasePacket.get_packet(packet)

            if isinstance(packet, DataPacket):

                print("Received DATA packet: ", packet)

                bufer.append(packet.get_data())

                self.send_ACK(packet.get_block_number(), client_address)
                print("ACK packet sent for data packet")

                if packet.is_final_packet():
                    print("Final packet received")
                    break

            else:

                # TODO: Implementar manejo de errores
                # Lo mismo que trap pero para DataPacket??
                # Si no me llega un data packet seguir esperando hasta timeout?

                raise Exception("Unexpected packet type")

            # TODO: escribir archivo con la data recibida


    def send_ACK(self, bloqnum, client_address):

        ack_packet = AckPacket(bloqnum)
        self.socket.sendto(ack_packet.serialize(), client_address)
