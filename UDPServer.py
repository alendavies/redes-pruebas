import threading
import time
from socket import *
from struct import pack

from packet import *

PACKET_SIZE = 20


class Packet:

    FORMAT = "!I"

    def __init__(self, seqnum, data):
        self.seqnum = seqnum
        self.data = data

    def serialize(self) -> bytes:
        return b"".join([pack(Packet.FORMAT, 1), self.data.encode()])

    def __str__(self):
        return f"SeqNum: {self.seqnum}, Data: {self.data}"


def deserialize(data: bytes) -> Packet:
    return Packet(data[0], data[1:].decode())


def main():

    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", serverPort))
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


def handleWriteRequest(packet: WriteRequestPacket, clientAddress, serverSocket):

    print("Handling WRITE REQUEST packet")
    print(packet)

    bufer = []

    ackPacket = AckPacket()
    serverSocket.sendto(ackPacket.serialize(), clientAddress)
    print("ACK packet sent")

    while True:

        packet, clientAddress = serverSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)

        if isinstance(packet, DataPacket):

            print("Received DATA packet: ")
            print(packet)
            bufer.append(packet.data.decode())

            ackPacket = AckPacket()
            serverSocket.sendto(ackPacket.serialize(), clientAddress)
            print("ACK packet sent")

            if len(packet.data) < PACKET_SIZE:
                # End of file
                break

        else:
            raise Exception("Unexpected packet type")

    data = "".join(bufer)

    print(data)


def handleReadRequest(packet: ReadRequestPacket, clientAddress, serverSocket):

    print("Handling READ REQUEST packet")

    data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

    while True:

        if len(data) < PACKET_SIZE:
            packet = DataPacket(data.encode())
            serverSocket.sendto(packet.serialize(), clientAddress)
            print("DATA packet sent")

            packet, clientAddress = serverSocket.recvfrom(2048)
            packet = BasePacket.get_packet(packet)

            if isinstance(packet, AckPacket):
                print("Received ACK packet")
                break
            else:
                raise Exception("Unexpected packet type")

        packet = DataPacket(data[:PACKET_SIZE].encode())
        serverSocket.sendto(packet.serialize(), clientAddress)
        print("DATA packet sent")

        packet, clientAddress = serverSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)

        if isinstance(packet, AckPacket):
            print("Received ACK packet")
        else:
            raise Exception("Unexpected packet type")

        data = data[PACKET_SIZE:]


if __name__ == "__main__":
    main()
