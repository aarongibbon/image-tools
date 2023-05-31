from PIL.ExifTags import TAGS
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

    def __init__(self, image):
        self.filepath = image.filename
        self.filename = self.filepath.split("/")[-1]
        logger.info(f"Processing image {self.filename}")
        self.exif_data = self.get_exif_data(image)
        self.create_date = self.get_create_date()
        self.size = os.path.getsize(self.filepath)
        # TODO
        # self.lastmodifieddate ??

    def get_exif_data(self, image):
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
        logger.info('Getting date from exif data')
        return datetime.strptime(create_date.split(" ")[0], self.EXIF_DATE_FORMAT).date()
        
    def extract_date_from_filename(self):
        logger.info(f"Extracting date from filename for {self.filepath}")
        create_date = re.search(self.CREATE_DATE_REGEX, self.filepath)
        if create_date:
            try:
                return dateutil.parser.parse(create_date.group()).date()
            except dateutil.parser.ParserError:
                logger.error(f"Invalid date {create_date.group()} found in {self.filepath}, cannot parse")
                return None
        logger.error(f"No date found in {self.filepath} with CREATE_DATE_REGEX")
        return None
