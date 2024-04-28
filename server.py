from socket import *
from struct import pack
import time
from config import *
from packet import *
from server_side import ServerConnection
from stop_and_wait import StopAndWait

def main():

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", SERVER_PORT))
    print("The server is ready to receive")

    while True:
        packet, (ip, port) = serverSocket.recvfrom(2048)
        connection_protocol = StopAndWait(ip, port)

        try:
            ServerConnection(connection_protocol).handle(packet)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
