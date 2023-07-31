import logging
import sys

from generic_file import GenericFile
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class ImageFile(GenericFile):

    def __init__(self, file_path, logger):
        super().__init__(file_path, logger)

    def get_meta_data(self):
        # See: https://pillow.readthedocs.io/en/stable/reference/open_files.html#image-lifecycle
        image = Image.open(self.relative_path)
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
        image.close()
        return return_exif_data
