from abc import abstractmethod
from config import *
from packet import *
from socket import *

class Connection:
    def __init__(self, ip: str, port: int):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        # bind?
        self.ip = ip
        self.port = port

    def close(self):
        self.socket.close()

    def get_socket(self):
        return self.socket

    @abstractmethod
    def send_file(self, message: bytes) -> bool:
        """
        Handles the sending side of the file transfer. Should
        guarantee reliable transfer, or throw.
        """

    def send(self, packet: bytes):
        self.socket.sendto(packet, (self.ip, self.port))

    def receive(self):
        return self.socket.recvfrom(SOCKET_SIZE)

    def send_ACK(self, bloqnum):
        ack_packet = AckPacket(bloqnum)
        self.socket.sendto(ack_packet.serialize(), (SERVER_IP, SERVER_PORT))

    @abstractmethod
    def receive_file(self, initial_bloqnum = 0, initial_data = b'') -> bytes:
        """
        Handles the reception side of the file transfer. Should
        guarantee reliable reception, or throw.
        """

