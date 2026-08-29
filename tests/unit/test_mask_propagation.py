import cv2
import numpy as np

from digitalsreeni_image_annotator.mask_propagation import (
    interpolate_annotations,
    propagate_annotations,
)


def _circle_frame(center):
    image = np.zeros((96, 128, 3), dtype=np.uint8)
    cv2.circle(image, center, 13, (230, 230, 230), -1)
    return image


def _circle_annotation(center):
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    points = np.column_stack(
        (center[0] + 13 * np.cos(angles), center[1] + 13 * np.sin(angles))
    )
    return {
        "droplet": [
            {
                "segmentation": points.flatten().tolist(),
                "category_id": 1,
                "category_name": "droplet",
            }
        ]
    }


def _centroid(annotation):
    points = np.asarray(annotation["segmentation"]).reshape(-1, 2)
    return points.mean(axis=0)


def test_propagation_preserves_identity_on_identical_adjacent_frames():
    image = _circle_frame((45, 45))
    result = propagate_annotations(
        image, image.copy(), _circle_annotation((45, 45)), {"droplet": 1}
    )

    annotation = result["droplet"][0]
    assert annotation["source"] == "propagated_candidate"
    assert annotation["confidence"] > 0.95
    assert np.linalg.norm(_centroid(annotation) - np.array([45, 45])) < 2.0


def test_keyframe_interpolation_places_mask_between_keyframes():
    result = interpolate_annotations(
        _circle_annotation((30, 45)),
        _circle_annotation((70, 45)),
        (96, 128),
        {"droplet": 1},
        0.5,
    )

    annotation = result["droplet"][0]
    assert annotation["source"] == "keyframe_interpolation"
    assert np.linalg.norm(_centroid(annotation) - np.array([50, 45])) < 3.0
