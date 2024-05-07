from socket import socket, AF_INET, SOCK_DGRAM
import argparse
import threading
import time

from lib.FileService import FileService
from lib.loggers.BaseLogger import BaseLogger
from lib.loggers.ServerSideLogger import ServerSideLogger
from lib.protocols.stop_and_wait.Server import Server as StopAndWait
from lib.protocols.selective_repeat.Server import Server as SelectiveRepeat
from lib.protocols.ProtocolServer import ProtocolServer
from lib.Connection import Connection


def main():
    description = "Provides the service of store and download files."
    usage = (
        "%(prog)s [ -h ] [ -v | -q ] -H ADDR -p PORT -s DIRPATH [ -sw | -sr ]"
    )

    parser = argparse.ArgumentParser(description=description, usage=usage)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity",
        default=True,
    )

    group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="decrease output verbosity",
        default=False,
    )

    requiredNamed = parser.add_argument_group("required arguments")

    requiredNamed.add_argument(
        "-H",
        "--host",
        metavar="",
        help="service IP address",
        default="127.0.0.1",
        type=str,
        required=True,
    )
    
    requiredNamed.add_argument(
        "-p",
        "--port",
        metavar="",
        help="service port",
        default=5000,
        type=int,
        required=True,
    )

    requiredNamed.add_argument(
        "-s",
        "--src",
        metavar="",
        help="storage dir path",
        type=str,
        required=True,
    )

    group2 = parser.add_mutually_exclusive_group()

    group2.add_argument(
        "-sw",
        "--stwa",
        action="store_true",
        help="stop and wait protocol",
        default=True,
    )

    group2.add_argument(
        "-sr",
        "--sere",
        action="store_true",
        help="selective repeat protocol",
        default=False,
    )

    args = parser.parse_args()

    if args.verbose and args.quiet:
        """
        This is because the default value is True and
        the user can't set both to True.
        In addition, the library does not automatically
        set the other arguments in the group to False if one is True.
        """
        args.verbose = False

    if args.stwa and args.sere:
        args.stwa = False

    logger = ServerSideLogger()

    # Now we can access the values with args.host, args.port, etc.
    connection_protocol: ProtocolServer
    file_service = FileService('./files/server_root/')

    # MAX_QUEUE = 5
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((args.host, args.port))
    # serverSocket.listen(MAX_QUEUE)
    print("The server is ready to receive on {}:{}.".format(args.host, args.port))


    while True:
        packet, (ip, port) = serverSocket.recvfrom(2048)
        
        logger.info("Incoming from {}:{}".format(ip, port))
        connection = Connection(ip, port)

        if args.stwa:
            connection_protocol = StopAndWait(connection, file_service)
            print("Using Stop and Wait protocol.")
        elif args.sere:
            connection_protocol = SelectiveRepeat(connection, file_service)
            print("Using Selective Repeat protocol.")
        else :
            print("No protocol selected.")
            break

        client_thread = threading.Thread(target=connection_protocol.handle, args=([packet]))
        client_thread.start()

        # try:
        #     print("Handling request")
        #     connection_protocol.handle(packet)
        # except Exception as e:
        #     print(e)

# def handle_incoming(protocol: ProtocolServer):
#     print("hola from thread")
#     time.sleep(10)
#     print("chau from thread")


if __name__ == "__main__":
    main()

