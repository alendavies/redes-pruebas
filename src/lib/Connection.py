from socket import socket, AF_INET, SOCK_DGRAM
from lib.packets.BasePacket import BasePacket
from lib.packets.PacketParser import PacketParser
from lib.loggers.PacketLogger import PacketLogger

import math
import time
import random

class Connection:
    SOCKET_SIZE = 1024

    def __init__(self, ip: str, port: int, packet_loss: float = 0, median_delay = 0):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.logger = PacketLogger(self.ip, self.port)
        self.packet_loss = packet_loss
        self.avg_delay = median_delay

    def send(self, packet: BasePacket):
        if random.random() < self.packet_loss:
            return
        time.sleep(random.randint(0, 2) * self.avg_delay)
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

