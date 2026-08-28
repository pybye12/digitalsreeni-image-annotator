from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from PyQt6.QtGui import QColor

from digitalsreeni_image_annotator.review_package import export_review_package


def _write_source(path, value):
    pixels = np.full((20, 24, 3), value, dtype=np.uint8)
    Image.fromarray(pixels, mode="RGB").save(path)


def test_review_package_contains_exact_masks_overlays_and_browser_page(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    first = source_dir / "frame_001.png"
    second = source_dir / "frame_002.png"
    _write_source(first, 80)
    _write_source(second, 120)

    annotations = {
        first.name: {
            "droplet": [
                {
                    "segmentation": [4, 4, 12, 4, 12, 12, 4, 12],
                    "category_name": "droplet",
                    "category_id": 1,
                    "type": "polygon",
                }
            ]
        },
        second.name: {
            "droplet": [
                {
                    "segmentation": [2, 2, 8, 2, 8, 8, 2, 8],
                    "category_name": "droplet",
                    "category_id": 1,
                    "type": "polygon",
                }
            ]
        },
    }
    output = tmp_path / "review"

    result = export_review_package(
        annotations,
        {"droplet": QColor(255, 0, 0)},
        {first.name: str(first), second.name: str(second)},
        [],
        {},
        output,
        [first.name],
    )

    assert result["frame_count"] == 1
    assert (output / "images" / first.name).is_file()
    assert not (output / "images" / second.name).exists()
    assert (output / "overlays" / f"{first.name}_overlay.png").is_file()
    mask_path = output / "rgb_masks" / f"{first.name}_rgb_mask.png"
    assert mask_path.is_file()

    mask = np.asarray(Image.open(mask_path).convert("RGB"))
    assert tuple(mask[8, 8]) == (255, 0, 0)
    assert tuple(mask[0, 0]) == (0, 0, 0)

    review_html = Path(result["review_path"]).read_text(encoding="utf-8")
    assert "1 labels ready for review" in review_html
    assert "Exact RGB mask" in review_html
    assert "RGB (255, 0, 0)" in review_html
    assert (output / "README.txt").is_file()
    assert Path(result["archive_path"]).is_file()


def test_review_package_requires_a_selection(tmp_path):
    with pytest.raises(ValueError, match="Select at least one"):
        export_review_package({}, {}, {}, [], {}, tmp_path, [])


def test_review_package_does_not_overwrite_an_existing_package(tmp_path):
    (tmp_path / "overlays").mkdir()
    with pytest.raises(ValueError, match="unused output directory"):
        export_review_package(
            {"frame.png": {}},
            {},
            {},
            [],
            {},
            tmp_path,
            ["frame.png"],
        )


def test_review_package_does_not_reuse_an_existing_archive(tmp_path):
    output = tmp_path / "review"
    output.with_suffix(".zip").write_bytes(b"existing")

    with pytest.raises(ValueError, match="unused output directory"):
        export_review_package(
            {"frame.png": {}},
            {},
            {},
            [],
            {},
            output,
            ["frame.png"],
        )
