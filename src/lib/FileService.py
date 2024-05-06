class FileService:
    
    def __init__(self):
        pass

    def write_file(self, filename: str, data: bytes):
        file = open('./files/' + filename, "wb")
        file.write(data)
        file.close()

    def get_file(self, filename: str):

        file = open('./files/' + filename, "rb")
        data = file.read()

        return data
