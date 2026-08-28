from types import SimpleNamespace

import numpy as np
from PyQt6.QtGui import QColor

from digitalsreeni_image_annotator.image_label import (
    ImageLabel,
    _annotation_mask,
    _mask_overlay_image,
)
from digitalsreeni_image_annotator.utils import calculate_area, calculate_bbox


def test_temporary_brush_overlay_is_transparent_outside_stroke():
    mask = np.zeros((4, 5), dtype=np.uint8)
    mask[2, 3] = 255

    overlay = _mask_overlay_image(mask, QColor(255, 128, 0))

    untouched = overlay.pixelColor(0, 0)
    painted = overlay.pixelColor(3, 2)
    assert untouched.alpha() == 0
    assert painted.getRgb() == (255, 128, 0, 128)


def test_eraser_only_changes_selected_class_and_preserves_hole(qtbot):
    label = ImageLabel()
    qtbot.addWidget(label)
    unchanged_arc = {
        "segmentation": [2, 2, 21, 2, 21, 21, 2, 21],
        "category_name": "external_arc",
        "number": 1,
    }
    droplet = {
        "segmentation": [2, 2, 21, 2, 21, 21, 2, 21],
        "category_name": "droplet",
        "number": 1,
    }
    label.annotations = {
        "external_arc": [unchanged_arc.copy()],
        "droplet": [droplet],
    }
    saved = {}
    label.set_main_window(
        SimpleNamespace(
            current_class="droplet",
            current_slice=None,
            image_file_name="frame.png",
            all_annotations=saved,
            update_annotation_list=lambda: None,
            save_current_annotations=lambda: None,
            update_slice_list_colors=lambda: None,
        )
    )
    eraser = np.zeros((24, 24), dtype=np.uint8)
    eraser[9:15, 9:15] = 255
    label.temp_eraser_mask = eraser

    label.commit_eraser_changes()

    assert label.annotations["external_arc"] == [unchanged_arc]
    assert len(label.annotations["droplet"]) == 1
    edited = label.annotations["droplet"][0]
    assert edited["holes"]
    edited_mask = _annotation_mask(edited, eraser.shape)
    assert edited_mask[5, 5] == 255
    assert edited_mask[11, 11] == 0
    assert saved["frame.png"] is label.annotations


def test_eraser_can_split_one_annotation_into_two(qtbot):
    label = ImageLabel()
    qtbot.addWidget(label)
    label.annotations = {
        "droplet": [
            {
                "segmentation": [2, 2, 21, 2, 21, 21, 2, 21],
                "category_name": "droplet",
                "number": 1,
            }
        ]
    }
    label.set_main_window(
        SimpleNamespace(
            current_class="droplet",
            current_slice=None,
            image_file_name="frame.png",
            all_annotations={},
            update_annotation_list=lambda: None,
            save_current_annotations=lambda: None,
            update_slice_list_colors=lambda: None,
        )
    )
    eraser = np.zeros((24, 24), dtype=np.uint8)
    eraser[:, 11:13] = 255
    label.temp_eraser_mask = eraser

    label.commit_eraser_changes()

    assert len(label.annotations["droplet"]) == 2


def test_geometry_helpers_include_multiple_polygons_and_subtract_holes():
    annotation = {
        "segmentation": [
            [0, 0, 10, 0, 10, 10, 0, 10],
            [20, 20, 25, 20, 25, 25, 20, 25],
        ],
        "holes": [[2, 2, 6, 2, 6, 6, 2, 6]],
    }

    assert calculate_area(annotation) == 109.0
    assert calculate_bbox(annotation["segmentation"]) == [0, 0, 25, 25]


def test_geometry_helpers_accept_empty_segmentation():
    annotation = {"segmentation": []}

    assert calculate_area(annotation) == 0
    assert calculate_bbox(annotation["segmentation"]) == [0, 0, 0, 0]
