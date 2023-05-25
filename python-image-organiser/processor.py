import pathlib
import filecmp
from image import ImageFile
from sys import argv
from PIL import Image, UnidentifiedImageError
import logging
import os
from datetime import date
from sys import exit
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

file_types = {'.jpg', '.gif', '.png', '.jpeg'}
path = pathlib.Path('./')

images = []

# PIL.Image requires relative paths
src=Directory(os.path.relpath(argv[1]))
dest=Directory(argv[2])

if not directory_checks(src, dest):
    logger.error(f"There was an issue with the target directories, exiting")
    exit(1)

for file in path.glob(f"{src.dir}/**/*"):
    if file.suffix in file_types:
        if os.path.getsize(file) == 0:
            logger.error(f"File {file} has size 0 bytes, not processing")
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