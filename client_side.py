from socket import *
import time
from packet import *
from config import *

class ClientSide:

    def __init__(self):

        self.socket = socket(AF_INET, SOCK_DGRAM)

    def handle_read(self):

        file = []
        filename = input("Enter the filename: ")

        packet_req = ReadRequestPacket(filename)

        self.socket.sendto(packet_req.serialize(), (SERVER_IP, SERVER_PORT))

        # wait for ack
        packet, _ = self.socket.recvfrom(2048)

        packet = BasePacket.get_packet(packet)

        if isinstance(packet, AckPacket):
            print("Received ACK")
        else:
            # TODO: handle errors / keep waiting for ack? Resend request?
            raise Exception("Invalid packet")

        while True:

            packet, _ = self.socket.recvfrom(2048)
            packet = BasePacket.get_packet(packet)

            if isinstance(packet, DataPacket):

                print("Received: ", packet)
                file.append(packet.data.decode())

                self.send_ACK(packet.get_block_number())

            else:
                # TODO: handle errors / wait for only data packets and no other type?
                raise Exception("Invalid packet")

            if len(packet.data) < PACKET_SIZE:
                print("Received file completed")
                # TODO: show file on terminal? what to do with the file received?
                # TODO: close socket?
                break


    def handle_write(self):

        filename = input("Enter the filename: ")

        packet_req = WriteRequestPacket(filename)

        self.socket.sendto(packet_req.serialize(), (SERVER_IP, SERVER_PORT))

        packet, _ = self.socket.recvfrom(2048)

        packet = BasePacket.get_packet(packet)

        if isinstance(packet, AckPacket):
            print("Received ACK")
        else:
            # TODO: handle errors / keep waiting for ack? Resend request?
            raise Exception("Invalid packet")

        # TODO: handle file, open if exists, etc

        file = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, ligula nec tincidunt luctus, odio est luctus orci, eu ultricies orci nunc nec nunc. Nullam nec lorem vel nunc lacinia aliquet. Etiam in semper nunc. Nulla facilisi. Nullam auctor, odio in ultricies tincidunt, nisl purus lacinia odio, nec lacinia nunc mi sit amet nunc."

        bloqnum = 0
        es_ultimo = False
        attempts = 0

        while es_ultimo == False and attempts <= MAX_ATTEMPTS:

            if len(file[bloqnum*PACKET_SIZE:]) < PACKET_SIZE:

                chunk = file[bloqnum*PACKET_SIZE:].encode()
                es_ultimo = True

            else:
                chunk = file[bloqnum*PACKET_SIZE:(bloqnum+1) * PACKET_SIZE].encode()

            data_packet = DataPacket(bloqnum, chunk)

            self.socket.sendto(data_packet.serialize(), (SERVER_IP, SERVER_PORT))
            print("DATA packet sent", data_packet)

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


    def send_ACK(self, bloqnum):

        ack_packet = AckPacket(bloqnum)
        self.socket.sendto(ack_packet.serialize(), (SERVER_IP, SERVER_PORT))
