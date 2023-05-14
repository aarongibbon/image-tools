import pathlib
import os

class Directory():

    def __init__(self, directory):
        self.dir = directory
        self.directory = pathlib.Path(directory)
        #TODO Add checks to see if directory exists

    def __bool__(self):
        if os.path.isdir(self.dir):
            return True
        return False

    @property
    def file_count(self):
        return len([file for file in self.directory.glob("**/*") if file.is_file()])

    @property
    def is_writeable(self):
        if os.access(self.dir, os.W_OK):
            return True
        return False

    @property
    def is_readable(self):
        if os.access(self.dir, os.R_OK):
            return True
        return False
