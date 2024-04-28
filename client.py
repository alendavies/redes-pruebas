from socket import *
from client_side import ClientSide
from file_service import FileService
from packet import *
from config import *
from stop_and_wait import StopAndWait

connection_protocol = StopAndWait(SERVER_IP, SERVER_PORT)

def handle_write():

    filename = input("Enter the path of the file to upload: ")
    file = FileService.get_file(filename)
    print(file)

    try:
        ClientSide(connection_protocol).initiate_write_request(file)
    except Exception as e:
        print(e)


def handle_read():
    filename = input("Enter the name of the requested file: ")

    try:
        file = ClientSide(connection_protocol).initiate_read_request(filename)
        print(file)
    except Exception as e:
        print(e)


def main():

    while True:
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

if __name__ == "__main__":
    main()
