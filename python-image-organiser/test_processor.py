import runpy
from unittest.mock import patch, call
import pytest
import runpy
from PIL import Image
from PIL.ExifTags import TAGS
import processor

def run_processor():
    runpy.run_module("processor", run_name='__main__')

def generate_test_files(root_dir, files):
    for path_to_file, options in files.items():
        file = root_dir / path_to_file
        file.parent.mkdir(parents=True, exist_ok=True)
        size = options.get("size", (1,1))
        exif_data = options.get("exif_data", {})

        image = Image.new("RGB", size)

        exif = image.getexif()
        for key, value in exif_data.items():
            exif[key] = value

        image.save(file)

@pytest.fixture()
def mock_logger():
    with patch('processor.logger') as mock_logger:
        yield mock_logger


def test_basic_flow(mock_logger, tmp_path):
    files = {
        "srcdir/fun_dir/20210707.jpg": {"exif_data": {"0x0132": "2021:07:07"}},
        "srcdir/20230809.jpg": {}
    }
    generate_test_files(tmp_path, files)
    runpy.run_module("processor", run_name='__main__')
