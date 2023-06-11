import pathlib
import filecmp
from image import ImageFile
from PIL import Image, UnidentifiedImageError
import logging
import os
from datetime import date
from sys import exit, argv
from shutil import copy2
from directorystats import Directory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def should_process(image):
    create_date = image.create_date
    if not create_date:
        return False
    elif create_date.year > date.today().year:
        return False

def directory_checks(source, destination):
    return_value = True
    if not source:
        logger.error(f"Source directory {source.dir} does not exist")
        return_value = False
    if not source.is_readable:
        logger.error(f"Source directory {source.dir} is not readable with current user")
        return_value = False
    if not destination:
        logger.error(f"Destination directory {destination.dir} does not exist")
        return_value = False
    if not destination.is_writeable:
        logger.error(f"Destination directory {destination.dir} is not writeable with current user")
        return_value = False
    return return_value

def process(src_root, dest_root):
    file_types = {'.jpg', '.gif', '.png', '.jpeg'}
    path = pathlib.Path('./')

    images = []

    # PIL.Image requires relative paths
    src=Directory(os.path.relpath(src_root))
    dest=Directory(dest_root)

    if not directory_checks(src, dest):
        logger.error(f"There was an issue with the target directories, exiting")
        exit(1)

    src_files = [file for file in src.directory.glob("**/*") if file.is_file()]
    dest_files = [file for file in src.directory.glob("**/*") if file.is_file()]

    for file in src_files:
        logger.info(f"Processing file {os.path.abspath(file)}")
        if file.suffix not in file_types:
            logger.info(f"Ignoring {file} as suffix not in {file_types}")
            continue
        if os.path.getsize(file) == 0:
            logger.error(f"Ignoring {file} as it has size 0 bytes")
            continue
        with Image.open(file) as image:
            images.append(ImageFile(image))

    for image in images:
        create_date = image.create_date
        if not create_date:
            dest_dir = f"{dest.dir}/misc"
        else:
            dest_dir = f"{dest.dir}/{create_date.year}/{create_date.month}"

        try:
            same = filecmp.cmp(image.filepath, f"{dest_dir}/{image.filename}", shallow=True)
        except FileNotFoundError:
            same = False

        if not same:
            os.makedirs(dest_dir, exist_ok=True)
            copy2(image.filepath, f"{dest_dir}/{image.filename}")

if __name__ == '__main__':
    process(argv[1], argv[2])
