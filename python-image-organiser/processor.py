import argparse
import filecmp
import logging
import os
from datetime import date
from shutil import copy2
from sys import argv, exit

from directorystats import Directory
from image import ImageFile
from video import VideoFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def should_process(file):
    create_date = file.create_date
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


def find_files(root):
    return [file for file in root.directory.glob("**/*") if file.is_file()]


def process(src_root, dest_root, dry_run=False, delete_source=False):
    file_types = {'.jpg': ImageFile, '.gif': ImageFile, '.png': ImageFile, '.jpeg': ImageFile, '.mp4': VideoFile}

    valid_files = []

    # PIL.Image requires relative paths
    src = Directory(src_root)
    dest = Directory(dest_root)

    if not directory_checks(src, dest):
        logger.error(f"There was an issue with the target directories, exiting")
        exit(1)

    src_files = find_files(src)
    dest_files = find_files(dest)

    for file in src_files:
        absolute_path = os.path.abspath(file)
        logger.info(f"Processing file {absolute_path}")
        if file.suffix not in file_types.keys():
            logger.info(f"Ignoring {absolute_path} as suffix {file.suffix} not valid")
            continue
        if os.path.getsize(file) == 0:
            logger.info(f"Ignoring {absolute_path} as it has size 0 bytes")
            continue
        file_class = file_types.get(file.suffix)
        valid_files.append(file_class(file))

    for file in valid_files:
        create_date = file.create_date
        if not create_date:
            dest_dir = f"{dest.dir}/misc"
        else:
            dest_dir = f"{dest.dir}/{create_date.year}/{create_date.strftime('%b')}"

        dest_file = f"{dest_dir}/{file.name}"

        try:
            same = filecmp.cmp(file.absolute_path, dest_file, shallow=True)
        except FileNotFoundError:
            same = False
        logger.info(same)
        if same:
            logger.info(f"Not copying {file.absolute_path} as {dest_file} exists and is the same")
            continue

        logger.info(f"Copying {file.absolute_path} to {dest_file}")
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            copy2(file.absolute_path, dest_file)

        if delete_source:
            logger.info(f"Deleting {file.absolute_path}")
            if not dry_run:
                os.remove(file.absolute_path)


if __name__ == '__main__':
    # TODO: Add dry run option
    # TODO: Use argsparse or something with a helper function
    parser = argparse.ArgumentParser(
        prog='Media Organiser', description='A program for organising media files by year and month')
    parser.add_argument('-s', '--source', required=True)
    parser.add_argument('-d', '--destination', required=True)
    parser.add_argument('--dry-run', action='store_true', default=False,
                        required=False, help='Disables copying of files and directory creation', dest='dry_run')
    parser.add_argument('--delete-source', action='store_true', default=False,
                        required=False, help='Delete the source files after copying them', dest='delete_source')
    args = parser.parse_args()

    process(args.source, args.destination, args.dry_run, args.delete_source)
