import logging
import os
import re
import sys
from datetime import datetime

import dateutil.parser


class GenericFile:

    # Overwrite these as needed in classes that inherit from this one
    CREATE_DATE_REGEX = r'20\d{2}-?(0[1-9]|1[012])-?(0[1-9]|[12][0-9]|3[01])'
    META_DATA_DATETIME_KEY = 'date_time'
    META_DATA_DATETIME_FORMAT = '%Y:%m:%d %H:%M:%S'
    META_DATA_DATE_FORMAT = '%Y:%m:%d'

    def __init__(self, file_path, logger):
        self.logger = logger
        self.relative_path = os.path.relpath(file_path)
        self.absolute_path = os.path.abspath(file_path)
        self.name = self.absolute_path.split("/")[-1]
        self.meta_data = self.get_meta_data()
        self.create_date = self.get_create_date()
        self.size = os.path.getsize(self.absolute_path)
        # TODO
        # self.lastmodifieddate ??

    def get_meta_data(self):
        # TODO write docstring
        return {}

    def decode_bytes(self, data):
        try:
            return data.decode()
        except UnicodeDecodeError:
            return None

    def get_create_date(self):
        create_date = self.meta_data.get(self.META_DATA_DATETIME_KEY)
        if not create_date:
            return self.extract_date_from_file_name()
        self.logger.debug(f"Getting date from meta data for {self.absolute_path}")
        return datetime.strptime(create_date.split(" ")[0], self.META_DATA_DATE_FORMAT).date()

    def extract_date_from_file_name(self):
        self.logger.debug(f"Extracting date from file name for {self.absolute_path}")
        create_date = re.search(self.CREATE_DATE_REGEX, self.name)
        if create_date:
            try:
                return dateutil.parser.parse(create_date.group()).date()
            except dateutil.parser.ParserError:
                self.logger.debug(f"Invalid date {create_date.group()} found in {self.absolute_path}, cannot parse")
                return None
        self.logger.debug(f"No date found in name of file at {self.absolute_path}")
        return None
