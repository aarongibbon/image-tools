import os
import pathlib


class Directory():

    def __init__(self, directory):
        self.dir = str(directory).rstrip("/")
        self.directory = pathlib.Path(directory)
        # TODO Add checks to see if directory exists

    def __bool__(self):
        # should we be using self.directory.is_dir instead?
        return os.path.isdir(self.dir)

    @property
    def file_count(self):
        if self.__bool__():
            return len([file for file in self.directory.glob("**/*") if file.is_file()])
        return None

    @property
    def is_writeable(self):
        return os.access(self.dir, os.W_OK)

    @property
    def is_readable(self):
        return os.access(self.dir, os.R_OK)
