from PIL import Image
import processor
from testing_utils import assert_has_logs


def generate_test_files(root_dir, files):
    (root_dir / "src_dir").mkdir()
    (root_dir / "dest_dir").mkdir()
    for path_to_file, options in files.items():
        file = root_dir / path_to_file
        file.parent.mkdir(parents=True, exist_ok=True)
        size = options.get("size", (1,1))
        exif_data = options.get("exif_data", {})
        image = Image.new("RGB", size)
        exif = image.getexif()
        for key, value in exif_data.items():
            exif[key] = value
        image.save(file, exif=exif)


def test_basic_flow(caplog, tmp_path):
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
                        f"Extracting date from filename for {tmp_path}/src_dir/20230809.jpg"
                    ])
