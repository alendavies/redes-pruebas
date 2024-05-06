from lib.loggers.BaseLogger import BaseLogger


class FileService:

    def __init__(self, path: str):
        self.path = path
        self.logger = BaseLogger("FileService")

    def save_file(self, filename: str, data: bytes):
        self.logger.debug("Saving file: " + filename)
        file = open(self.path + filename, "wb")
        file.write(data)
        file.close()

    def get_file(self, filename: str):

        file = open(self.path + filename, "rb")
        data = file.read()

        return data
