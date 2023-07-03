from PIL.ExifTags import TAGS
from PIL import Image
import re
from datetime import datetime
import dateutil.parser
import logging
import os
import sys
from generic_file import GenericFile

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

class ImageFile(GenericFile):

    def __init__(self, file_path):
        super().__init__(file_path)

    def get_meta_data(self):
        # See: https://pillow.readthedocs.io/en/stable/reference/open_files.html#image-lifecycle
        image = Image.open(self.relative_path)
        image.close()
        return_exif_data = {}
        exif_data = image.getexif()
        for tag_id in exif_data:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            # decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            return_exif_data[tag] = data
        return return_exif_data
