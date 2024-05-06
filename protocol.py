from abc import abstractmethod
from config import *
from logger import PacketLogger
from packet import *
from socket import *

class Connection:
    def __init__(self, ip: str, port: int):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.logger = PacketLogger()

    def close(self):
        self.socket.close()

    def get_socket(self):
        return self.socket

    @abstractmethod
    def send_file(self, data: bytes):
        """
        Handles the sending side of the file transfer. Should
        guarantee reliable transfer, or throw.
        """

    def send(self, packet: BasePacket):
        self.socket.sendto(packet.serialize(), (self.ip, self.port))
        self.logger.debug("sent packet: " + packet.__str__())

    def receive(self) -> tuple[BasePacket, tuple[str, int]]:
        self.socket.setblocking(False)
        message, server_addr = self.socket.recvfrom(SOCKET_SIZE)

        try:
            packet = MasterOfPackets.get_packet(message)
        except custom_errors.UnknownPacketType:
            self.logger.error("Invalid packet type.")
            raise custom_errors.UnknownPacketType

        self.logger.debug("received packet from {ip}:{port}: {message}".format(ip=server_addr[0], port=server_addr[1], message=packet.__str__()))

        return packet, server_addr

    def send_ACK(self, bloqnum: int):
        ack_packet = AckPacket(bloqnum)
        self.send(ack_packet)

    @abstractmethod
    def receive_file(self, initial_bloqnum = 0) -> bytes:
        """
        Handles the reception side of the file transfer. Should
        guarantee reliable reception, or throw.
        """

