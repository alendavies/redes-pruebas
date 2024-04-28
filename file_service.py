
class FileService:
    def __init__(self):
        pass

    @classmethod
    def get_file(self, path: str) -> bytes:
        """
        Getea un archivo.
        """

        return "Lorem ipsum dolor sit amet, consectetur adisciping elit.".encode()

    def save_file(self, filename: str):
        """
        Guarda bytes en un archivo.
        """

        return

