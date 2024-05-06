class FileService:
    
    def __init__(self, path: str):
        self.path = path

    def save_file(self, filename: str, data: bytes):
        file = open(self.path + filename, "wb")
        file.write(data)
        file.close()

    def get_file(self, filename: str):

        file = open(self.path + filename, "rb")
        data = file.read()

        return data
