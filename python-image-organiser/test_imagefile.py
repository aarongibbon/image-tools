from image import ImageFile
import pytest
from unittest.mock import patch

class MockImage():
    filename: str = None
    exif_data: dict = {}

    def getexif(self):
        return self.exif_data

class MockStatResult():
    def __init__(self, size: int):
        self.st_size = size

@pytest.fixture
def mock_image():
    return MockImage()

@pytest.fixture
def non_zero_size():
    with patch("os.stat", return_value=MockStatResult(10)):
        yield

def test_noexif_invalid_date_19991231dotjpg(non_zero_size, mock_image):
    """ Test date below year 2000 """
    mock_image.filename = "19991231.jpg"
    image = ImageFile(mock_image)
    assert image.create_date is None

def test_noexif_valid_date_20000101dotjpg(non_zero_size, mock_image):
    """ Test date within year 2000 """
    mock_image.filename = "20000101.jpg"
    image = ImageFile(mock_image)
    assert image.create_date.year == 2000
    assert image.create_date.month == 1
    assert image.create_date.day == 1

def test_noexif_valid_date_Screenshot_20230407_213656_Bluebookdotjpg(non_zero_size, mock_image):
    """ Test date within other text """
    mock_image.filename = "Screenshot_20230407_213656_Bluebook.jpg"
    image = ImageFile(mock_image)
    assert image.create_date.year == 2023
    assert image.create_date.month == 4
    assert image.create_date.day == 7

def test_noexif_invalid_date_nodateheredotjpg(non_zero_size, mock_image):
    """ Test no date """
    mock_image.filename = "nodatehere.jpg"
    image = ImageFile(mock_image)
    assert image.create_date is None

def test_noexif_invalid_date_20070229dotjpg(non_zero_size, mock_image):
    """ Test invalid date that at first glance looks valid """
    mock_image.filename = "20070229.jpg"
    image = ImageFile(mock_image)
    assert image.create_date is None
