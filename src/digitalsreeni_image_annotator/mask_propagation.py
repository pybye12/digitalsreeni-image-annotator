"""Fast mask propagation and keyframe interpolation helpers."""

import copy
from math import exp

import cv2
import numpy as np


def _annotation_mask(annotation, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    points = np.asarray(annotation.get("segmentation", []), dtype=np.float32)
    if points.size < 6 or points.size % 2:
        return mask
    polygon = np.rint(points.reshape(-1, 2)).astype(np.int32)
    cv2.fillPoly(mask, [polygon], 255)
    for hole in annotation.get("holes", []):
        hole_points = np.asarray(hole, dtype=np.float32)
        if hole_points.size >= 6 and hole_points.size % 2 == 0:
            cv2.fillPoly(mask, [np.rint(hole_points.reshape(-1, 2)).astype(np.int32)], 0)
    return mask


def _mask_components(mask, min_area=12):
    contours, hierarchy = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )
    if hierarchy is None:
        return []
    hierarchy = hierarchy[0]
    components = []
    for index, contour in enumerate(contours):
        if hierarchy[index][3] != -1 or cv2.contourArea(contour) < min_area:
            continue
        holes = []
        child = hierarchy[index][2]
        while child != -1:
            if cv2.contourArea(contours[child]) >= min_area:
                holes.append(contours[child].reshape(-1, 2).flatten().tolist())
            child = hierarchy[child][0]
        components.append((contour.reshape(-1, 2).flatten().tolist(), holes))
    return components


def annotations_to_class_masks(annotations, shape):
    masks = {}
    for class_name, class_annotations in annotations.items():
        combined = np.zeros(shape, dtype=np.uint8)
        for annotation in class_annotations:
            combined = cv2.bitwise_or(combined, _annotation_mask(annotation, shape))
        if np.any(combined):
            masks[class_name] = combined
    return masks


def _confidence(previous_gray, next_gray, remap_x, remap_y, warped_mask):
    warped_image = cv2.remap(
        previous_gray, remap_x, remap_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
    )
    region = warped_mask > 0
    if not np.any(region):
        return 0.0
    residual = np.mean(np.abs(warped_image[region].astype(float) - next_gray[region]))
    return float(max(0.0, min(1.0, exp(-residual / 36.0))))


def propagate_annotations(previous_image, next_image, annotations, class_mapping):
    """Warp annotations one frame forward with dense optical flow.

    The return value is a new annotation mapping. Existing input objects are
    never mutated. Confidence reflects photometric agreement inside each mask;
    it is a review hint, not a calibrated model probability.
    """
    if previous_image is None or next_image is None:
        return {}
    previous_gray = cv2.cvtColor(previous_image, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_image, cv2.COLOR_BGR2GRAY)
    if previous_gray.shape != next_gray.shape:
        raise ValueError("Adjacent frames must have the same dimensions.")

    backward_flow = cv2.calcOpticalFlowFarneback(
        next_gray, previous_gray, None, 0.5, 3, 21, 3, 5, 1.2, 0
    )
    height, width = previous_gray.shape
    grid_x, grid_y = np.meshgrid(
        np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32)
    )
    remap_x = grid_x + backward_flow[..., 0]
    remap_y = grid_y + backward_flow[..., 1]

    result = {}
    for class_name, mask in annotations_to_class_masks(
        annotations, previous_gray.shape
    ).items():
        warped = cv2.remap(
            mask, remap_x, remap_y, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT
        )
        confidence = _confidence(previous_gray, next_gray, remap_x, remap_y, warped)
        for segmentation, holes in _mask_components(warped):
            annotation = {
                "segmentation": segmentation,
                "category_id": class_mapping[class_name],
                "category_name": class_name,
                "source": "propagated_candidate",
                "confidence": round(confidence, 3),
            }
            if holes:
                annotation["holes"] = holes
            result.setdefault(class_name, []).append(annotation)
    return result


def _signed_distance(mask):
    foreground = (mask > 0).astype(np.uint8)
    background = 1 - foreground
    return cv2.distanceTransform(foreground, cv2.DIST_L2, 5) - cv2.distanceTransform(
        background, cv2.DIST_L2, 5
    )


def interpolate_annotations(first, second, shape, class_mapping, fraction):
    """Interpolate class masks between two keyframes with signed distances."""
    fraction = float(fraction)
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    first_masks = annotations_to_class_masks(first, shape)
    second_masks = annotations_to_class_masks(second, shape)
    result = {}
    for class_name in first_masks.keys() & second_masks.keys():
        first_mask = first_masks[class_name]
        second_mask = second_masks[class_name]
        first_moments = cv2.moments(first_mask)
        second_moments = cv2.moments(second_mask)
        if first_moments["m00"] and second_moments["m00"]:
            first_center = np.array(
                [
                    first_moments["m10"] / first_moments["m00"],
                    first_moments["m01"] / first_moments["m00"],
                ]
            )
            second_center = np.array(
                [
                    second_moments["m10"] / second_moments["m00"],
                    second_moments["m01"] / second_moments["m00"],
                ]
            )
            motion = second_center - first_center
            first_matrix = np.array(
                [[1.0, 0.0, fraction * motion[0]], [0.0, 1.0, fraction * motion[1]]],
                dtype=np.float32,
            )
            second_matrix = np.array(
                [
                    [1.0, 0.0, -(1.0 - fraction) * motion[0]],
                    [0.0, 1.0, -(1.0 - fraction) * motion[1]],
                ],
                dtype=np.float32,
            )
            first_mask = cv2.warpAffine(
                first_mask, first_matrix, (shape[1], shape[0]), flags=cv2.INTER_NEAREST
            )
            second_mask = cv2.warpAffine(
                second_mask, second_matrix, (shape[1], shape[0]), flags=cv2.INTER_NEAREST
            )
        level_set = (
            (1.0 - fraction) * _signed_distance(first_mask)
            + fraction * _signed_distance(second_mask)
        )
        mask = (level_set >= 0).astype(np.uint8) * 255
        for segmentation, holes in _mask_components(mask):
            annotation = {
                "segmentation": segmentation,
                "category_id": class_mapping[class_name],
                "category_name": class_name,
                "source": "keyframe_interpolation",
                "confidence": round(1.0 - abs(0.5 - fraction), 3),
            }
            if holes:
                annotation["holes"] = holes
            result.setdefault(class_name, []).append(annotation)
    return copy.deepcopy(result)
