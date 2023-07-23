import logging
import sys

from generic_file import GenericFile
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class VideoFile(GenericFile):

    def __init__(self, file_path):
        super().__init__(file_path)
