from socket import socket, AF_INET, SOCK_DGRAM
import argparse

from lib.FileService import FileService
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

    # Now we can access the values with args.host, args.port, etc.

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((args.host, args.port))
    print("The server is ready to receive")


    while True:
        packet, (ip, port) = serverSocket.recvfrom(2048)
            
        connection_protocol: ProtocolServer
        connection = Connection(ip, port)
        file_service = FileService()

        if args.stwa:
            connection_protocol = StopAndWait(connection, file_service)
            print("Using Stop and Wait protocol.")
        elif args.sere:
            connection_protocol = SelectiveRepeat(connection, file_service)
            print("Using Selective Repeat protocol.")
        else :
            print("No protocol selected.")
            break

        try:
            print("Handling request")
            connection_protocol.handle(packet)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()

