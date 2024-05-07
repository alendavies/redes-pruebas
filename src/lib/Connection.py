from socket import socket, AF_INET, SOCK_DGRAM
from lib.packets.BasePacket import BasePacket
from lib.packets.PacketParser import PacketParser
from lib.loggers.PacketLogger import PacketLogger

class Connection:
    SOCKET_SIZE = 1024

    def __init__(self, ip: str, port: int):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.logger = PacketLogger(self.ip, self.port)

    def send(self, packet: BasePacket):
        self.socket.sendto(packet.serialize(), (self.ip, self.port))
        self.logger.on_packet_sent(packet)

    def receive(self, blocking: bool = False) -> tuple[BasePacket, tuple[str, int]]:
        self.socket.setblocking(blocking)
        message, server_addr = self.socket.recvfrom(self.SOCKET_SIZE)

        try:
            packet = PacketParser.get_packet(message)
        except Exception as e:
            self.logger.on_unexpected_packet()
            raise e

        self.logger.on_packet_received(packet)

        return packet, server_addr

