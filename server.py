from socket import *
from struct import pack
import time
from config import *

from packet import *

def main():

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", SERVER_PORT))
    print("The server is ready to receive")

    while True:
        packet, clientAddress = serverSocket.recvfrom(2048)
        handle_conection(packet, clientAddress, serverSocket)


def handle_conection(packet, clientAddress, serverSocket):

    handlePacketByType(packet, clientAddress, serverSocket)


def handlePacketByType(packet, clientAddress, serverSocket):

    packet = BasePacket.get_packet(packet)

    if isinstance(packet, WriteRequestPacket):
        print("Received WRITE REQUEST packet")
        handleWriteRequest(packet, clientAddress, serverSocket)

    elif isinstance(packet, ReadRequestPacket):
        print("Received READ REQUEST packet")
        handleReadRequest(packet, clientAddress, serverSocket)

    else:
        raise Exception("Unexpected packet type")


def handleWriteRequest(req_packet: WriteRequestPacket, clientAddress, serverSocket):

    print("Handling WRITE REQUEST packet")
    print(req_packet)

    bufer = []

    ack_packet = AckPacket(0)
    serverSocket.sendto(ack_packet.serialize(), clientAddress)
    print("ACK packet sent")

    while True:

        packet, clientAddress = serverSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)

        if isinstance(packet, DataPacket):

            print("Received DATA packet: ")
            print(packet)
            bufer.append(packet.get_data())

            ack_packet = AckPacket(packet.get_block_number())
            serverSocket.sendto(ack_packet.serialize(), clientAddress)
            print("ACK packet sent")

            if packet.is_final_packet():
                break

        else:
            raise Exception("Unexpected packet type")

    data = "".join(bufer)

    print(data)

def trap(bloqnum, socket) -> int:

    # Esperar ACK o alcanzar el tiempo de espera
    timeout = 5  # Tiempo de espera en segundos
    start_time = time.time()

    while True:

        packet, _ = socket.recvfrom(2048)

        if isinstance(packet, AckPacket):
            if packet.get_block_number() == bloqnum:
                print("Received ACK packet")
                return bloqnum+1
        else:
            # Verificar si se ha excedido el tiempo máximo de espera
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                print("Tiempo de espera excedido")
                break
    return bloqnum

def handleReadRequest(req_packet: ReadRequestPacket, clientAddress, serverSocket):

    print("Handling READ REQUEST packet")

    data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

    bloqnum = 0
    es_ultimo = False
    serverSocket.setblocking(0)
    attempts = 0

    while es_ultimo == False and attempts <= MAX_ATTEMPTS:

        if len(data[bloqnum*PACKET_SIZE:]) < PACKET_SIZE:

            cacho = data[bloqnum*PACKET_SIZE:].encode()
            es_ultimo = True

        else:
            cacho = data[bloqnum*PACKET_SIZE:(bloqnum+1) * PACKET_SIZE].encode()

        data_packet = DataPacket(bloqnum, cacho)
        serverSocket.sendto(data_packet.serialize(), clientAddress)
        print("DATA packet sent")

        prev_bloqnum = bloqnum
        bloqnum = trap(bloqnum, serverSocket)

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

if __name__ == "__main__":
    main()
