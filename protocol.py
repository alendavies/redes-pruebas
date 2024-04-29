from abc import abstractmethod
from config import *
from logger import PacketLogger
from packet import *
from socket import *

class Connection:
    def __init__(self, ip: str, port: int):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setblocking(False)
        self.ip = ip
        self.port = port
        self.logger = PacketLogger()

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

    def send(self, packet: BasePacket):
        self.socket.sendto(packet.serialize(), (self.ip, self.port))
        self.logger.debug("sent packet: " + packet.__str__())

    def receive(self) -> BasePacket:
        message, _ = self.socket.recvfrom(SOCKET_SIZE)
        packet = MasterOfPackets.get_packet(message)
        self.logger.debug("received packet: " + packet.__str__())

        return packet

    def send_ACK(self, bloqnum: int):
        ack_packet = AckPacket(bloqnum)
        self.send(ack_packet)

    @abstractmethod
    def receive_file(self, initial_bloqnum = 0, initial_data = b'') -> bytes:
        """
        Handles the reception side of the file transfer. Should
        guarantee reliable reception, or throw.
        """

