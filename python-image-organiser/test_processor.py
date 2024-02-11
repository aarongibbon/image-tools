from logging import INFO
from os.path import isfile
from unittest.mock import Mock, call, patch

import pytest
from PIL import Image

import processor
from directorystats import Directory


def generate_test_files(root_dir, files):
    for path_to_file, options in files.items():

        file = root_dir / path_to_file

        if path_to_file.endswith("/"):
            file.mkdir(parents=True, exist_ok=True)
            continue

        file.parent.mkdir(parents=True, exist_ok=True)
        size = options.get("size", 1)
        mtime = options.get("mtime", None)

        if path_to_file.endswith(".mp4"):
            with open(file, "wb") as f:
                f.write(b'0' * size)
                f.close()
        else:
            exif_data = options.get("exif_data", {})
            image = Image.new("RGB", (size, size))
            exif = image.getexif()
            for key, value in exif_data.items():
                exif[key] = value
            image.save(file, exif=exif)


def test_basic_flow(tmp_path):
    """ Test getting date from filename and from exif data """
    # TODO: Test when a file doesnt contain a valid date
    files = {
        "src_dir/fun_dir/20210707.jpg": {"exif_data": {36867: "2021:07:07 00:00:00"}},
        "src_dir/20230809.jpg": {},
        "dest_dir/": {}
    }

    generate_test_files(tmp_path, files)
    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger)

    mock_logger.info.assert_has_calls([
        call(f"Processing file {tmp_path}/src_dir/20230809.jpg"),
        call(f"Could not find DateTimeOriginal in exif data for {tmp_path}/src_dir/20230809.jpg, trying DateTime instead"),
        call(f"Could not find DateTime in exif data for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Extracting date from file name for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Processing file {tmp_path}/src_dir/fun_dir/20210707.jpg"),
        call(f"Getting date from meta data for {tmp_path}/src_dir/fun_dir/20210707.jpg"),
        call(f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg"),
        call(f"Copying {tmp_path}/src_dir/fun_dir/20210707.jpg to {tmp_path}/dest_dir/2021/Jul/20210707.jpg"),
        call(f"Source contained 2 files before processing and 2 after"),
        call(f"Destination contained 0 files before processing and 2 after")
    ])

    assert isfile(f"{tmp_path}/dest_dir/2021/Jul/20210707.jpg")
    assert isfile(f"{tmp_path}/dest_dir/2023/Aug/20230809.jpg")


def test_dest_file_exists_and_same(tmp_path):
    files = {
        "src_dir/20230809.jpg": {},
        "dest_dir/2023/Aug/20230809.jpg": {}
    }

    generate_test_files(tmp_path, files)
    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger)

    mock_logger.info.assert_has_calls([
        call(f"Not copying {tmp_path}/src_dir/20230809.jpg as {tmp_path}/dest_dir/2023/Aug/20230809.jpg exists and is the same"),
    ])

    assert call(f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg") not in mock_logger.info.mock_calls


def test_dest_file_exists_and_not_same(tmp_path):
    files = {
        "src_dir/20230809.jpg": {"size": 20},
        "dest_dir/2023/Aug/20230809.jpg": {"size": 10}
    }

    generate_test_files(tmp_path, files)
    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger)

    mock_logger.info.assert_has_calls([
        call(f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg")
    ])

    assert call(f"Not copying {tmp_path}/src_dir/20230809.jpg as {tmp_path}/dest_dir/2023/Aug/20230809.jpg exists and is the same") not in mock_logger.info.mock_calls


def test_invalid_suffix(tmp_path):
    open(tmp_path / "invalidsuffix.xyz", "a").close()
    mock_logger = Mock()
    processor.process(tmp_path, tmp_path, mock_logger)

    mock_logger.warning.assert_has_calls([
        call(f"Ignoring {tmp_path}/invalidsuffix.xyz as suffix .xyz not valid")
    ])


def test_image_with_0_bytes(tmp_path):
    open(tmp_path / "emptyfile.jpg", "a").close()
    mock_logger = Mock()
    processor.process(tmp_path, tmp_path, mock_logger)

    mock_logger.warning.assert_has_calls([
        call(f"Ignoring {tmp_path}/emptyfile.jpg as it has size 0 bytes")
    ])


def test_mp4_file(tmp_path):
    files = {
        "src_dir/20200101.mp4": {},
        "dest_dir/": {}
    }

    generate_test_files(tmp_path, files)
    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger)

    mock_logger.info.assert_has_calls([
        call(f"Processing file {tmp_path}/src_dir/20200101.mp4"),
        call(f"Extracting date from file name for {tmp_path}/src_dir/20200101.mp4"),
        call(f"Copying {tmp_path}/src_dir/20200101.mp4 to {tmp_path}/dest_dir/2020/Jan/20200101.mp4")
    ])

    assert Directory(tmp_path / "dest_dir").file_count == 1
    assert isfile(f"{tmp_path}/dest_dir/2020/Jan/20200101.mp4")


def test_dry_run(tmp_path):
    files = {
        "src_dir/20230809.jpg": {},
        "dest_dir/": {}
    }

    generate_test_files(tmp_path, files)
    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger, dry_run=True)

    mock_logger.info.assert_has_calls([
        call(f"Processing file {tmp_path}/src_dir/20230809.jpg"),
        call(f"Could not find DateTimeOriginal in exif data for {tmp_path}/src_dir/20230809.jpg, trying DateTime instead"),
        call(f"Could not find DateTime in exif data for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Extracting date from file name for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg")
    ])

    assert Directory(tmp_path / "dest_dir").file_count == 0

    # Double check that faulty test data isn't the reason the above check passes
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger, dry_run=False)
    assert Directory(tmp_path / "dest_dir").file_count == 1


def test_deleting_source_true(tmp_path):
    files = {
        "src_dir/20230809.jpg": {},
        "dest_dir/": {}
    }

    generate_test_files(tmp_path, files)

    assert Directory(tmp_path / "src_dir").file_count == 1

    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger, dry_run=False, delete_source=True)

    mock_logger.info.assert_has_calls([
        call(f"Processing file {tmp_path}/src_dir/20230809.jpg"),
        call(f"Could not find DateTimeOriginal in exif data for {tmp_path}/src_dir/20230809.jpg, trying DateTime instead"),
        call(f"Could not find DateTime in exif data for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Extracting date from file name for {tmp_path}/src_dir/20230809.jpg"),
        call(f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg"),
        call(f"Deleting {tmp_path}/src_dir/20230809.jpg"),
        call(f"Source contained 1 files before processing and 0 after"),
        call(f"Destination contained 0 files before processing and 1 after")
    ])


def test_deleting_source_false(tmp_path):
    files = {
        "src_dir/20230809.jpg": {},
        "dest_dir/": {}
    }

    generate_test_files(tmp_path, files)

    assert Directory(tmp_path / "src_dir").file_count == 1

    mock_logger = Mock()
    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir", mock_logger, dry_run=False, delete_source=False)

    assert call(f"Deleting {tmp_path}/src_dir/20230809.jpg") not in mock_logger.info.mock_calls
    assert Directory(tmp_path / "src_dir").file_count == 1
