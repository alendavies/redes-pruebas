from socket import *
from struct import pack
from config import *

from packet import *

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


def handleReadRequest(req_packet: ReadRequestPacket, clientAddress, serverSocket):

    print("Handling READ REQUEST packet")

    data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

    bloqnum = 0
    es_ultimo = False

    while es_ultimo == False:

        if len(data[bloqnum*PACKET_SIZE:]) < PACKET_SIZE:

            cacho = data[bloqnum*PACKET_SIZE:].encode()
            es_ultimo = True

        else:
            cacho = data[bloqnum*PACKET_SIZE:(bloqnum+1) * PACKET_SIZE].encode()

        data_packet = DataPacket(bloqnum, cacho)
        serverSocket.sendto(data_packet.serialize(), clientAddress)
        print("DATA packet sent")

        packet, clientAddress = serverSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)

        if isinstance(packet, AckPacket):
            print("Received ACK packet")
        else:
            raise Exception("Unexpected packet type")


if __name__ == "__main__":
    main()
