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

logging.basicConfig(level=logging.ERROR)

def should_process(image):
    create_date = image.create_date
    if not create_date:
        return False
    elif create_date.year > date.today().year:
        return False

def dest_checks(directory):
    if not os.path.isdir(dest):
        logging.error(f"Destination directory {directory} does not exist, exiting")
        return False
    if not os.access(directory, os.W_OK):
        logging.error(f"Destination directory {directory} is not writeable with current user, exiting")
        return False
    return True

file_types = {'.jpg', '.gif', '.png', '.jpeg'}
path = pathlib.Path('./')

images = []

# PIL.Image requires relative paths
src=os.path.relpath(argv[1])
dest=argv[2]

if not dest_checks(dest):
    exit(1)

for file in path.glob(f"{src}/**/*"):
    if file.suffix in file_types:
        if os.path.getsize(file) == 0:
            logging.error(f"File {file} has size 0 bytes, not processing")
            continue
        with Image.open(file) as image:
            images.append(ImageFile(image))


for image in images:
    create_date = image.create_date
    if not create_date:
        dest_dir = f"{dest}/misc"
    else:
        dest_dir = f"{dest}/{create_date.year}/{create_date.month}"
    
    try:
        same = filecmp.cmp(image.filepath, f"{dest_dir}/{image.filename}", shallow=True)
    except FileNotFoundError:
        same = False

    if not same:
        os.makedirs(dest_dir, exist_ok=True)
        copy2(image.filepath, f"{dest_dir}/{image.filename}")