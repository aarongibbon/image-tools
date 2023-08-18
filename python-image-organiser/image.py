from generic_file import GenericFile
from PIL import Image
from PIL.ExifTags import TAGS


class ImageFile(GenericFile):

    META_DATA_DATETIME_KEY = 'DateTimeOriginal'
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

        for tag_id in self.TAG_IDS:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id, None)

            if isinstance(data, bytes):
                try:
                    data = data.decode()
                except UnicodeDecodeError:
                    self.logger.error(f"Failed to decode tag {tag} in exif data for {self.absolute_path}")
                    continue
            return_exif_data[tag] = data

        image.close()
        return return_exif_data
