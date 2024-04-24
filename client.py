from socket import *
from packet import *
from time import sleep
from config import *

clientSocket = socket(AF_INET, SOCK_DGRAM)

def handle_read():
    file = []
    filename = input("Enter the filename: ")

    packet_req = ReadRequestPacket(filename)

    clientSocket.sendto(packet_req.serialize(), (SERVER_IP, SERVER_PORT))

    while 1:
        packet, serverAddress = clientSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)
        if isinstance(packet, DataPacket):
            print("Received: ", packet)
            file.append(packet.data.decode())
            ack_packet = AckPacket(packet.get_block_number())
            clientSocket.sendto(ack_packet.serialize(), (SERVER_IP, SERVER_PORT))
        else:
            raise Exception("Invalid packet")

        if len(packet.data) < PACKET_SIZE:
            print("Completed")
            break

    print("File content: ", "".join(file))


def handle_write():
    filename = input("Enter the filename: ")

    file = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, ligula nec tincidunt luctus, odio est luctus orci, eu ultricies orci nunc nec nunc. Nullam nec lorem vel nunc lacinia aliquet. Etiam in semper nunc. Nulla facilisi. Nullam auctor, odio in ultricies tincidunt, nisl purus lacinia odio, nec lacinia nunc mi sit amet nunc."

    packet_req = WriteRequestPacket(filename)

    clientSocket.sendto(packet_req.serialize(), (SERVER_IP, SERVER_PORT))

    packet, serverAddress = clientSocket.recvfrom(2048)

    packet = BasePacket.get_packet(packet)

    if isinstance(packet, AckPacket):
        print("Received ACK")
    else:
        raise Exception("Invalid packet")

    bloqnum = 0

    while 1:
        data_packet = DataPacket(bloqnum, file[:PACKET_SIZE].encode())
        print("Sending: ", data_packet)
        clientSocket.sendto(data_packet.serialize(), (SERVER_IP, SERVER_PORT))
        packet, serverAddress = clientSocket.recvfrom(2048)
        packet = BasePacket.get_packet(packet)

        if isinstance(packet, AckPacket):
            print("Received ACK")
            file = file[PACKET_SIZE:]
            bloqnum += 1
            if len(file) == 0:
                print("Completed")
                break
        else:
            raise Exception("Invalid packet")

        sleep(0.2)

while 1:
    message = input("¿What do you want to do? [U]pload, [D]ownload, [E]xit: ")
    if message == "U":
        handle_write()
    elif message == "D":
        handle_read()
    elif message == "E":
        break
    else:
        print("Invalid option")
        continue

    # packet = Packet(1, message)
    # print("Created packet: ", packet)

    # serialized = packet.serialize()
    # print("Sending: ", serialized)
    # clientSocket.sendto(serialized, (SERVER_IP, SERVER_PORT))
    #
    # print("Waiting for server response...")
    #
    # response, serverAddress = clientSocket.recvfrom(2048)
    # print("Received: ", response)
    #
    # parsed_res = deserialize(response)
    # print("Parsed response: ", parsed_res)

clientSocket.close()

