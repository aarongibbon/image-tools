import pathlib
from image import ImageFile
from sys import argv
from PIL import Image, UnidentifiedImageError
import logging
import os
from datetime import date

def should_process(image):
    create_date = image.create_date
    if not create_date:
        return False
    elif create_date.year > date.today().year:
        return False

file_types = {'.jpg', '.gif', '.png', '.jpeg'}
path = pathlib.Path('./')

images = []

logging.basicConfig(level=logging.ERROR)

# PIL.Image requires relative paths
src=os.path.relpath(argv[1])
dest=argv[2]

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
        dest_file = f"{dest}/misc/{image.filename}"
    else:
        dest_file = f"{dest}/{create_date.year}/{create_date.month}/{create_date.day}/{image.filename}"
    print(dest_file)
