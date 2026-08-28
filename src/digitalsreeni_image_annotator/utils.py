"""
Utility functions for the Image Annotator application.

This module contains helper functions used across the application.

@DigitalSreeni
Dr. Sreenivas Bhattiprolu
"""

import os

import numpy as np


def models_base_dir() -> str:
    """Return the absolute path of the `models/` directory used for ML weights.

    Resolution strategy (single source of truth used by sam_utils, dino_utils,
    and annotator_window so all three agree on where weights live):

    1. Editable / dev install: package source lives at
       ``<project_root>/src/digitalsreeni_image_annotator/utils.py``, so
       three ``dirname``s up is the project root and ``<root>/models`` is
       the canonical location.
    2. PyPI / site-packages install: the package lives in site-packages, where
       writing model weights would be wrong (system / venv dir, not
       user-visible). Fall back to ``<cwd>/models`` instead.
    """
    pkg_anchor = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    if "site-packages" not in pkg_anchor.replace(os.sep, "/"):
        return os.path.join(pkg_anchor, "models")
    return os.path.join(os.getcwd(), "models")


def _segmentation_polygons(segmentation):
    if not segmentation:
        return []
    if isinstance(segmentation[0], (list, tuple, np.ndarray)):
        return segmentation
    return [segmentation]


def _polygon_area(polygon):
    x_coordinates = polygon[0::2]
    y_coordinates = polygon[1::2]
    if len(x_coordinates) < 3:
        return 0
    return 0.5 * abs(
        sum(
            x_coordinates[index] * y_coordinates[index + 1]
            - x_coordinates[index + 1] * y_coordinates[index]
            for index in range(-1, len(x_coordinates) - 1)
        )
    )


def calculate_area(annotation):
    if "segmentation" in annotation and annotation["segmentation"] is not None:
        area = sum(
            _polygon_area(polygon)
            for polygon in _segmentation_polygons(annotation["segmentation"])
        )
        hole_area = sum(
            _polygon_area(polygon) for polygon in annotation.get("holes", [])
        )
        return max(0, area - hole_area)
    elif "bbox" in annotation:
        # Rectangle area
        x, y, w, h = annotation["bbox"]
        return w * h
    return 0


def calculate_bbox(segmentation):
    polygons = _segmentation_polygons(segmentation)
    x_coordinates = [
        coordinate for polygon in polygons for coordinate in polygon[0::2]
    ]
    y_coordinates = [
        coordinate for polygon in polygons for coordinate in polygon[1::2]
    ]
    if not x_coordinates or not y_coordinates:
        return [0, 0, 0, 0]
    x_min, y_min = min(x_coordinates), min(y_coordinates)
    x_max, y_max = max(x_coordinates), max(y_coordinates)
    width, height = x_max - x_min, y_max - y_min
    return [x_min, y_min, width, height]

def normalize_image(image_array):
    """Normalize image array to 8-bit range."""
    if image_array.dtype != np.uint8:
        image_array = ((image_array - image_array.min()) / (image_array.max() - image_array.min()) * 255).astype(np.uint8)
    return image_array

