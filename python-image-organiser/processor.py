import argparse
import filecmp
import logging
import os
import sys
import traceback
from collections import Counter
from datetime import date, datetime
from shutil import copy2
from sys import argv, exit

from custom_log_formatters import (CustomStdoutEmailFormatter,
                                   CustomStdoutFormatter)
from directorystats import Directory
from image import ImageFile
from video import VideoFile

file_types = {'.jpg': ImageFile, '.jpeg': ImageFile, '.JPG': ImageFile,
              '.gif': ImageFile, '.png': ImageFile, '.mp4': VideoFile}
illegal_patterns = ['/@eaDir/']

base_log_format = '%(asctime)s | %(levelname)s | %(message)s'
base_log_formatter = logging.Formatter(base_log_format)

log_directory = "/tmp/media_organiser_log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = CustomStdoutFormatter(base_log_format)
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

os.makedirs(log_directory, exist_ok=True)
fh = logging.FileHandler(f"{log_directory}/media_organiser_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
fh.setLevel(logging.INFO)
fh.setFormatter(base_log_formatter)
logger.addHandler(fh)


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


def contains_illegal_pattern(path: str):
    for illegal_pattern in illegal_patterns:
        if illegal_pattern in path:
            return illegal_pattern
    return None


def validate_files(file_paths):
    valid_files = []
    ignored_files = []
    invalid_suffixes = []
    illegal_patterns = []
    empty_file_count = 0

    for file_path in file_paths:
        absolute_path = os.path.abspath(file_path)
        logger.debug(f"Processing file {absolute_path}")

        if file_path.suffix not in file_types.keys():
            logger.debug(f"Ignoring {absolute_path} as suffix {file_path.suffix} not valid")
            invalid_suffixes.append(file_path.suffix)
            ignored_files.append(absolute_path)
            continue

        if os.path.getsize(file_path) == 0:
            logger.debug(f"Ignoring {absolute_path} as it has size 0 bytes")
            empty_file_count += 1
            ignored_files.append(absolute_path)
            continue

        illegal_pattern = contains_illegal_pattern(str(absolute_path))

        if illegal_pattern:
            logger.debug(f"Ignoring {absolute_path} as it contains illegal pattern {illegal_pattern}")
            illegal_patterns.append(illegal_pattern)
            ignored_files.append(absolute_path)
            continue

        file_class = file_types.get(file_path.suffix)

        try:
            file = file_class(file_path, logger)
        except Exception:
            logger.critical(f"There was an error creating file object for {file_path}: {traceback.format_exc()}")
            continue

        valid_files.append(file)

    for invalid_suffix, count in Counter(invalid_suffixes).items():
        logger.warning(f"Ignoring {count} files with an invalid suffix of {invalid_suffix}")

    for illegal_pattern, count in Counter(illegal_patterns).items():
        logger.warning(f"Ignoring {count} files containing illegal pattern {illegal_pattern}")

    if empty_file_count > 0:
        logger.warning(f"Ignoring {empty_file_count} files with 0 bytes")

    return valid_files, ignored_files


def process(src_root, dest_root, dry_run=False, delete_source=False, delete_ignored=False):
    valid_files = []

    # PIL.Image requires relative paths
    src = Directory(src_root)
    dest = Directory(dest_root)

    pre_src_count = src.file_count
    pre_dest_count = dest.file_count

    if not directory_checks(src, dest):
        logger.error(f"There was an issue with the target directories, exiting")
        exit(1)

    src_files = find_files(src)

    valid_files, ignored_files = validate_files(src_files)

    for file in valid_files:
        create_date = file.create_date

        if not create_date:
            dest_dir = f"{dest.dir}/unorganised"
        else:
            dest_dir = f"{dest.dir}/{create_date.year}/{create_date.strftime('%b')}"

        dest_file = f"{dest_dir}/{file.name}"

        try:
            same = filecmp.cmp(file.absolute_path, dest_file, shallow=True)
        except FileNotFoundError:
            same = False

        if same:
            logger.info(f"Not copying {file.absolute_path} as {dest_file} exists and is the same")
            ignored_files.append(file.absolute_path)
            continue

        logger.info(f"Copying {file.absolute_path} to {dest_file}")

        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            copy2(file.absolute_path, dest_file)

        if delete_source:
            logger.debug(f"Deleting {file.absolute_path}")

            if not dry_run:
                os.remove(file.absolute_path)

    for absolute_path in ignored_files:
        if delete_ignored:
            logger.debug(f"Deleting {absolute_path}")

            if not dry_run:
                os.remove(absolute_path)

    post_src_count = src.file_count
    post_dest_count = dest.file_count

    logger.info(f"Ignored {len(ignored_files)} files")
    logger.info(f"Source contained {pre_src_count} files before processing and {post_src_count} after")
    logger.info(f"Destination contained {pre_dest_count} files before processing and {post_dest_count} after")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Media Organiser', description='A program for organising media files by year and month')
    parser.add_argument('-s', '--source', required=True)
    parser.add_argument('-d', '--destination', required=True)
    parser.add_argument('--dry-run', action='store_true', default=False,
                        required=False, help='Disables copying of files and directory creation', dest='dry_run')
    parser.add_argument('--delete-source', action='store_true', default=False,
                        required=False, help='Delete the source files after copying them', dest='delete_source')
    parser.add_argument('--delete-ignored-files', action='store_true', default=False,
                        required=False, help='Delete any invalid/ignored files', dest='delete_ignored')
    parser.add_argument('-e', action='store_true', default=False,
                        required=False, help='Format output logs for email', dest='email_format')
    args = parser.parse_args()

    if args.email_format:
        sh.setFormatter(base_log_formatter)
        sh.setLevel(logging.ERROR)

    process(args.source, args.destination, args.dry_run, args.delete_source, args.delete_ignored)
