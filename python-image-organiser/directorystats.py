import pathlib

class DirectoryStats():

    def __init__(self, directory):
        self.directory = pathlib.Path(directory)

    @property
    def file_count(self):
        return len([file for file in self.directory.glob("**/*") if file.is_file()])