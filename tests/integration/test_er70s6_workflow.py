import numpy as np
import pytest
from PIL import Image
from PyQt6.QtGui import QColor

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator
from digitalsreeni_image_annotator.export_formats import export_rgb_semantic_masks
from digitalsreeni_image_annotator.welding_defaults import (
    ER70S6_CAVITAR_CLASSES,
    ER70S6_CLASSES,
)


def _write_image(path):
    Image.new("RGB", (8, 8), (20, 20, 20)).save(path)


def test_er70s6_presets_use_protocol_colors():
    assert [(name, color.getRgb()[:3]) for name, color in ER70S6_CLASSES] == [
        ("molten_consumable", (255, 128, 0)),
        ("droplet", (255, 0, 0)),
        ("external_arc", (0, 0, 255)),
        ("internal_arc", (255, 255, 0)),
    ]
    assert [name for name, _ in ER70S6_CAVITAR_CLASSES] == [
        "molten_consumable",
        "droplet",
    ]


def test_rgb_export_writes_exact_colors_and_background_masks(tmp_path):
    labeled_image = tmp_path / "labeled.png"
    background_image = tmp_path / "background.png"
    _write_image(labeled_image)
    _write_image(background_image)
    annotations = {
        "labeled.png": {
            "molten_consumable": [
                {"segmentation": [1, 1, 3, 1, 3, 3, 1, 3]}
            ],
            "droplet": [
                {"segmentation": [5, 5, 6, 5, 6, 6, 5, 6]}
            ],
        },
    }

    export_rgb_semantic_masks(
        annotations,
        dict(ER70S6_CLASSES),
        {
            "labeled.png": str(labeled_image),
            "background.png": str(background_image),
        },
        [],
        {},
        str(tmp_path / "export"),
    )

    mask_dir = tmp_path / "export" / "rgb_masks"
    labeled_mask = np.asarray(Image.open(mask_dir / "labeled.png_rgb_mask.png"))
    background_mask = np.asarray(Image.open(mask_dir / "background.png_rgb_mask.png"))

    assert tuple(labeled_mask[2, 2]) == (255, 128, 0)
    assert tuple(labeled_mask[5, 5]) == (255, 0, 0)
    assert tuple(labeled_mask[0, 0]) == (0, 0, 0)
    assert not background_mask.any()
    assert (mask_dir / "class_rgb_mapping.txt").read_text().splitlines() == [
        "Background: 0, 0, 0",
        "molten_consumable: 255, 128, 0",
        "droplet: 255, 0, 0",
        "external_arc: 0, 0, 255",
        "internal_arc: 255, 255, 0",
    ]


def test_rgb_export_rejects_annotations_without_a_configured_color(tmp_path):
    image_path = tmp_path / "frame.png"
    _write_image(image_path)

    try:
        export_rgb_semantic_masks(
            {"frame.png": {"unknown": [{"bbox": [0, 0, 2, 2]}]}},
            {"droplet": QColor(255, 0, 0)},
            {"frame.png": str(image_path)},
            [],
            {},
            str(tmp_path / "export"),
        )
    except ValueError as exc:
        assert "unknown" in str(exc)
    else:
        raise AssertionError("missing class color should reject the export")


def test_rgb_export_includes_untouched_image_from_annotator(qtbot, tmp_path):
    image_path = tmp_path / "untouched.png"
    _write_image(image_path)
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    window.add_images_to_list([str(image_path)], auto_save=False)
    window.save_current_annotations()

    assert image_path.name not in window.all_annotations
    export_rgb_semantic_masks(
        window.all_annotations,
        {},
        window.image_paths,
        window.slices,
        window.image_slices,
        str(tmp_path / "untouched_export"),
    )

    mask = np.asarray(
        Image.open(
            tmp_path
            / "untouched_export"
            / "rgb_masks"
            / "untouched.png_rgb_mask.png"
        )
    )
    assert not mask.any()


def test_rgb_export_preserves_extensions_for_same_stem_images(tmp_path):
    jpg_path = tmp_path / "sample.jpg"
    png_path = tmp_path / "sample.png"
    _write_image(jpg_path)
    _write_image(png_path)

    export_rgb_semantic_masks(
        {},
        {},
        {
            jpg_path.name: str(jpg_path),
            png_path.name: str(png_path),
        },
        [],
        {},
        str(tmp_path / "mixed_export"),
    )

    mask_names = {
        path.name
        for path in (tmp_path / "mixed_export" / "rgb_masks").glob("*.png")
    }
    assert mask_names == {
        "sample.jpg_rgb_mask.png",
        "sample.png_rgb_mask.png",
    }


def test_rgb_export_rejects_reused_destination(tmp_path):
    image_path = tmp_path / "frame.png"
    _write_image(image_path)
    output_dir = tmp_path / "existing_export"
    stale_dir = output_dir / "rgb_masks"
    stale_dir.mkdir(parents=True)
    stale_file = stale_dir / "stale.png"
    stale_file.write_bytes(b"old")

    with pytest.raises(ValueError, match="unused output directory"):
        export_rgb_semantic_masks(
            {},
            {},
            {image_path.name: str(image_path)},
            [],
            {},
            str(output_dir),
        )

    assert stale_file.read_bytes() == b"old"
    assert not (output_dir / "images").exists()


def test_rgb_export_rejects_cross_class_overlap_without_partial_output(tmp_path):
    image_path = tmp_path / "overlap.png"
    _write_image(image_path)
    polygon = {"segmentation": [1, 1, 5, 1, 5, 5, 1, 5]}
    output_dir = tmp_path / "overlap_export"

    with pytest.raises(ValueError, match="Overlapping class annotations"):
        export_rgb_semantic_masks(
            {
                image_path.name: {
                    "molten_consumable": [polygon],
                    "droplet": [polygon],
                }
            },
            dict(ER70S6_CAVITAR_CLASSES),
            {image_path.name: str(image_path)},
            [],
            {},
            str(output_dir),
        )

    assert not (output_dir / "images").exists()
    assert not (output_dir / "rgb_masks").exists()
