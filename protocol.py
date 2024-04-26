from abc import abstractmethod


class Protocol:

    def __init__(self):
        pass

    @abstractmethod
    def send_message(self, message: bytes):
        """
        Handles the sending side of the file transfer. Should
        guarantee reliable transfer, or throw.
        """
        pass

    def receive_message(self, initial_bloqnum = 0, initial_data = b''):
        """
        Handles the reception side of the file transfer. Should
        guarantee reliable reception, or throw.
        """
        bloqnum = initial_bloqnum
        data = initial_data
        pass
