class File:
    def __init__(self, filename: str, data: bytes):
        self.filename = filename
        self.data = data
        
    def get_filename(self) -> str:
        return self.filename
        
    def get_data(self) -> bytes:
        return self.data

    def get_size(self) -> int:
        return len(self.data)

class FileService:
    def __init__(self):
        pass

    @classmethod
    def get_file(self, path: str) -> File:
        """
        Getea un archivo.
        """
        file = str("Lorem ipsum dolor sit amet, consectetur adisciping elit.")

        return File(path, file.encode())

    def save_file(self, file: File):
        """
        Guarda bytes en un archivo.
        """

        return

