from PIL import Image
import processor
from testing_utils import assert_has_logs, assert_not_logged
from unittest.mock import patch
from logging import INFO
import pytest
from os.path import isfile
from directorystats import Directory


@pytest.fixture
def caplog(caplog):
    caplog.set_level(INFO)
    return caplog


@pytest.fixture
def dest_dir(tmp_path):
    return Directory(tmp_path / "dest_dir")


def generate_test_files(root_dir, files):
    (root_dir / "src_dir").mkdir()
    (root_dir / "dest_dir").mkdir()
    for path_to_file, options in files.items():
        file = root_dir / path_to_file
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


def test_basic_flow(caplog, tmp_path, dest_dir):
    """ Test getting date from filename and from exif data """
    files = {
        "src_dir/fun_dir/20210707.jpg": {"exif_data": {306: "2021:07:07 00:00:00"}},
        "src_dir/20230809.jpg": {}
    }

    generate_test_files(tmp_path, files)

    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir")

    assert_has_logs(caplog.messages,
                    [
                        f"Processing file {tmp_path}/src_dir/fun_dir/20210707.jpg",
                        f"Getting date from exif data for {tmp_path}/src_dir/fun_dir/20210707.jpg",
                        f"Processing file {tmp_path}/src_dir/20230809.jpg",
                        f"Extracting date from file name for {tmp_path}/src_dir/20230809.jpg",
                        f"Copying {tmp_path}/src_dir/fun_dir/20210707.jpg to {tmp_path}/dest_dir/2021/Jul/20210707.jpg",
                        f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg"
                    ])
    assert dest_dir.file_count == 2
    assert isfile(f"{tmp_path}/dest_dir/2021/Jul/20210707.jpg")
    assert isfile(f"{tmp_path}/dest_dir/2023/Aug/20230809.jpg")


def test_dest_file_exists_and_same(caplog, tmp_path):
    files = {
        "src_dir/20230809.jpg": {},
        "dest_dir/2023/Aug/20230809.jpg": {}
    }

    generate_test_files(tmp_path, files)

    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir")

    assert_has_logs(caplog.messages,
                    [
                        f"Not copying {tmp_path}/src_dir/20230809.jpg as {tmp_path}/dest_dir/2023/Aug/20230809.jpg exists and is the same"
                    ])

    assert_not_logged(caplog.messages,
                      [
                          f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg"
                      ])


def test_dest_file_exists_and_not_same(caplog, tmp_path):
    files = {
        "src_dir/20230809.jpg": {"size":20},
        "dest_dir/2023/Aug/20230809.jpg": {"size":10}
    }

    generate_test_files(tmp_path, files)

    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir")

    assert_has_logs(caplog.messages,
                    [
                        f"Copying {tmp_path}/src_dir/20230809.jpg to {tmp_path}/dest_dir/2023/Aug/20230809.jpg"
                    ])

    assert_not_logged(caplog.messages,
                    [
                        f"Not copying {tmp_path}/src_dir/20230809.jpg as {tmp_path}/dest_dir/2023/Aug/20230809.jpg exists and is the same"
                    ])


def test_invalid_suffix(caplog, tmp_path):
    open(tmp_path / "invalidsuffix.xyz", "a").close()

    processor.process(tmp_path, tmp_path)

    assert_has_logs(caplog.messages,
                    [
                        f"Ignoring {tmp_path}/invalidsuffix.xyz as suffix .xyz not valid"
                    ])


def test_image_with_0_bytes(caplog, tmp_path):
    open(tmp_path / "emptyfile.jpg", "a").close()

    processor.process(tmp_path, tmp_path)

    assert_has_logs(caplog.messages,
                    [
                        f"Ignoring {tmp_path}/emptyfile.jpg as it has size 0 bytes"
                    ])


def test_mp4_file(caplog, tmp_path, dest_dir):
    files = {
        "src_dir/20200101.mp4": {}
    }

    generate_test_files(tmp_path, files)

    processor.process(tmp_path / "src_dir", tmp_path / "dest_dir")

    assert_has_logs(caplog.messages,
                    [
                        f"Processing file {tmp_path}/src_dir/20200101.mp4",
                        f"Extracting date from file name for {tmp_path}/src_dir/20200101.mp4",
                        f"Copying {tmp_path}/src_dir/20200101.mp4 to {tmp_path}/dest_dir/2020/Jan/20200101.mp4"
                    ])
    assert dest_dir.file_count == 1
    assert isfile(f"{tmp_path}/dest_dir/2020/Jan/20200101.mp4")
