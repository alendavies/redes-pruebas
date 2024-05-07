import argparse
from lib.FileService import ClientFileService
from lib.loggers.BaseLogger import BaseLogger
from lib.loggers.ClientSideLogger import ClientSideLogger
from lib.protocols.stop_and_wait.Client import Client as StopAndWait
from lib.protocols.selective_repeat.Client import Client as SelectiveRepeat
from lib.protocols.ProtocolClient import ProtocolClient 
from lib.Connection import Connection

def main():
    description = "Upload a file to a server with the desired name."
    usage = "%(prog)s [ -h ] [ -v | -q ] -H ADDR -p PORT -s FILEPATH -n FILENAME [ -sw | -sr ]"

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
        help="server IP address",
        type=str,
        required=True,
    )

    requiredNamed.add_argument(
        "-p", "--port", metavar="", help="server port", type=int, required=True
    )

    requiredNamed.add_argument(
        "-s",
        "--src",
        metavar="",
        help="source file path",
        type=str,
        required=True,
    )

    requiredNamed.add_argument(
        "-n", "--name", metavar="", help="file name", type=str, required=True
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

    connection_protocol: ProtocolClient 
    connection = Connection(args.host, args.port)
    file_service = ClientFileService()
    logger = ClientSideLogger()

    if args.stwa:
        connection_protocol = StopAndWait(connection, file_service)
        logger.debug("Using Stop and Wait protocol.")
    elif args.sere:
        connection_protocol = SelectiveRepeat(connection, file_service)
        logger.debug("Using Selective Repeat protocol.")
    else:
        logger.error("No protocol selected.")
        return
    
    try:
        logger.info("Handling upload request for file: " + args.name)
        connection_protocol.upload(args.src, args.name)
        logger.success("Completed upload of {}.".format(args.name))
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
