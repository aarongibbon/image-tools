from generic_file import GenericFile
from PIL import Image
from PIL.ExifTags import TAGS


class ImageFile(GenericFile):

    DATETIME_ORIGINAL_TAG_ID = 36867
    DATETIME_TAG_ID = 306
    TAG_IDS = [
        36867  # DateTimeOriginal
    ]

    def __init__(self, file_path, logger):
        super().__init__(file_path, logger)

    def get_meta_data(self):
        # See: https://pillow.readthedocs.io/en/stable/reference/open_files.html#image-lifecycle
        image = Image.open(self.relative_path)
        return_exif_data = {}
        exif_data = image.getexif()

        date_time = exif_data.get(self.DATETIME_ORIGINAL_TAG_ID, None)

        # Fall back to DateTime
        if not date_time:
            self.logger.debug(
                f"Could not find DateTimeOriginal in exif data for {self.absolute_path}, trying DateTime instead")
            date_time = exif_data.get(self.DATETIME_TAG_ID, None)
            if not date_time:
                self.logger.debug(f"Could not find DateTime in exif data for {self.absolute_path}")

        if isinstance(date_time, bytes):
            date_time = self.decode_bytes(date_time)
            if not date_time:
                self.logger.debug(f"Failed to decode date time meta data for {self.absolute_path}")

        if date_time:
            return_exif_data[self.META_DATA_DATETIME_KEY] = date_time

        image.close()
        return return_exif_data
