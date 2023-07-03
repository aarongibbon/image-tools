from PIL.ExifTags import TAGS
from PIL import Image
import re
from datetime import datetime
import dateutil.parser
import logging
import os
import sys

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

class ImageFile:

    CREATE_DATE_REGEX=r'20\d{2}-?(0[1-9]|1[012])-?(0[1-9]|[12][0-9]|3[01])'
    EXIF_DATETIME_KEY='DateTime'
    EXIF_DATETIME_FORMAT='%Y:%m:%d %H:%M:%S'
    EXIF_DATE_FORMAT='%Y:%m:%d'

    def __init__(self, filepath):
        self.relative_path = os.path.relpath(filepath)
        self.absolute_path = os.path.abspath(filepath)
        self.filename = self.absolute_path.split("/")[-1]
        self.exif_data = self.get_exif_data()
        self.create_date = self.get_create_date()
        self.size = os.path.getsize(self.absolute_path)
        # TODO
        # self.lastmodifieddate ??

    def get_exif_data(self):
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

    def get_create_date(self):
        create_date = self.exif_data.get('DateTime') # do we need to consider DateTimeOriginal here?
        if not create_date:
            return self.extract_date_from_filename()
        logger.info(f"Getting date from exif data for {self.absolute_path}")
        return datetime.strptime(create_date.split(" ")[0], self.EXIF_DATE_FORMAT).date()
        
    def extract_date_from_filename(self):
        logger.info(f"Extracting date from filename for {self.absolute_path}")
        create_date = re.search(self.CREATE_DATE_REGEX, self.filename)
        if create_date:
            try:
                return dateutil.parser.parse(create_date.group()).date()
            except dateutil.parser.ParserError:
                logger.error(f"Invalid date {create_date.group()} found in {self.absolute_path}, cannot parse")
                return None
        logger.error(f"No date found in {self.absolute_path} with CREATE_DATE_REGEX")
        return None
