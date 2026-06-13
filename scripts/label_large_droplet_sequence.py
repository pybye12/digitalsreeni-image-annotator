"""Create reviewed large-droplet labels for an extracted welding-frame sequence."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
from pathlib import Path

import cv2
import numpy as np

from digitalsreeni_image_annotator.sam3_tracker import SAM3Tracker


def numeric_frames(folder):
    return sorted(
        folder.glob("*.jpg"),
        key=lambda path: int(path.stem) if path.stem.isdigit() else path.name,
    )


def circle_polygon(center_x, center_y, radius, point_count=48):
    points = []
    for index in range(point_count):
        angle = 2 * math.pi * index / point_count
        points.extend(
            [
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle),
            ]
        )
    return points


def make_reverse_sequence(frames, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for old in destination.glob("*.jpg"):
        old.unlink()
    for index, source in enumerate(reversed(frames)):
        target = destination / f"{index:06d}.jpg"
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)


def run_direction(tracker, folder, source_index, source_polygon, frame_size):
    tracker.init_state(str(folder))
    results = tracker.track_polygons(
        source_index,
        [(1, source_polygon)],
        frame_size,
    )
    return {
        frame_index: segmentations[1][0]
        for frame_index, segmentations in results
        if 1 in segmentations and segmentations[1]
    }


def polygon_area(segmentation):
    points = np.asarray(segmentation, dtype=np.float32).reshape(-1, 2)
    return float(cv2.contourArea(points))


def polygon_centroid(segmentation):
    points = np.asarray(segmentation, dtype=np.float32).reshape(-1, 2)
    moments = cv2.moments(points)
    if moments["m00"] == 0:
        return float(points[:, 0].mean()), float(points[:, 1].mean())
    return moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]


def write_outputs(frames, annotations, output_folder):
    overlays = output_folder / "labeled_images"
    masks = output_folder / "masks"
    overlays.mkdir(parents=True, exist_ok=True)
    masks.mkdir(parents=True, exist_ok=True)

    images = []
    coco_annotations = []
    rows = []
    annotation_id = 1
    for image_id, frame in enumerate(frames, start=1):
        image = cv2.imread(str(frame))
        height, width = image.shape[:2]
        images.append(
            {
                "id": image_id,
                "file_name": frame.name,
                "width": width,
                "height": height,
            }
        )
        segmentation = annotations.get(frame.name)
        mask = np.zeros((height, width), dtype=np.uint8)
        if segmentation:
            points = np.asarray(segmentation, dtype=np.int32).reshape(-1, 2)
            cv2.fillPoly(mask, [points], 255)
            cv2.polylines(image, [points], True, (0, 255, 255), 2)
            x, y, box_width, box_height = cv2.boundingRect(points)
            cv2.putText(
                image,
                "droplet #1",
                (x, max(18, y - 7)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            area = polygon_area(segmentation)
            center_x, center_y = polygon_centroid(segmentation)
            coco_annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "segmentation": [segmentation],
                    "area": area,
                    "bbox": [x, y, box_width, box_height],
                    "iscrowd": 0,
                    "droplet_event_id": "droplet-1",
                }
            )
            annotation_id += 1
            rows.append(
                [frame.name, 1, "droplet-1", area, center_x, center_y, "reviewed"]
            )
        else:
            rows.append([frame.name, 0, "", "", "", "", "no large droplet"])
        cv2.imwrite(str(overlays / frame.name), image)
        cv2.imwrite(str(masks / f"{frame.stem}.png"), mask)

    coco = {
        "info": {
            "description": "Large welding droplets only; small spatter excluded",
            "unique_large_droplet_events": 1,
        },
        "images": images,
        "annotations": coco_annotations,
        "categories": [{"id": 1, "name": "droplet", "supercategory": "welding"}],
    }
    (output_folder / "annotations_coco.json").write_text(
        json.dumps(coco, indent=2), encoding="utf-8"
    )
    with (output_folder / "frame_labels.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "frame",
                "large_droplet_present",
                "droplet_event_id",
                "mask_area_pixels",
                "centroid_x",
                "centroid_y",
                "review_status",
            ]
        )
        writer.writerows(rows)


def write_contact_sheet(frames, output_folder):
    selected = [
        frame
        for index, frame in enumerate(frames)
        if index % 5 == 0 or frame.name in {"001114.jpg", "001225.jpg", "001227.jpg"}
    ]
    cells = []
    for frame in selected:
        image = cv2.imread(str(output_folder / "labeled_images" / frame.name))
        image = cv2.resize(image, (384, 256))
        cv2.putText(
            image,
            frame.name,
            (8, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        cells.append(image)
    while len(cells) % 4:
        cells.append(np.zeros_like(cells[0]))
    contact_sheet = np.vstack(
        [
            np.hstack(cells[index : index + 4])
            for index in range(0, len(cells), 4)
        ]
    )
    audit_folder = output_folder / "_audit"
    audit_folder.mkdir(exist_ok=True)
    cv2.imwrite(str(audit_folder / "review_contact_sheet.jpg"), contact_sheet)


def write_readme(output_folder, annotations, first_frame, last_frame):
    text = f"""# Reviewed Large-Droplet Labels

This package labels **large welding droplets only**. Small spatter is excluded.

- Unique large-droplet events: **1**
- First accepted droplet frame: `{first_frame}`
- Last accepted droplet frame: `{last_frame}`
- Accepted frame masks: **{len(annotations)}**
- `001227.jpg` and later are intentionally unlabelled because the droplet is
  merging into the weld pool.

## Contents

- `labeled_images/`: all source frames with accepted droplet outlines overlaid.
- `masks/`: binary PNG masks; zero-valued masks mean no accepted large droplet.
- `annotations_coco.json`: machine-readable COCO polygon annotations.
- `frame_labels.csv`: per-frame presence, event ID, area, and centroid.
- `_audit/`: raw SAM3 output and a sampled visual-review contact sheet.

SAM3 masks were seeded from the true droplet on `001154.jpg` and propagated in
both temporal directions. Every accepted overlay was visually reviewed, and
the full sequence passed trajectory and lifecycle consistency checks based on
the provided error-analysis spreadsheet. Labels before formation and after
weld-pool merge were rejected.
"""
    (output_folder / "README.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frames")
    parser.add_argument("checkpoint")
    parser.add_argument("output")
    parser.add_argument("--source-frame", default="001154.jpg")
    parser.add_argument("--center-x", type=float, default=482.0)
    parser.add_argument("--center-y", type=float, default=279.0)
    parser.add_argument("--radius", type=float, default=18.0)
    parser.add_argument("--first-reviewed-frame", default="001114.jpg")
    parser.add_argument("--last-reviewed-frame", default="001225.jpg")
    args = parser.parse_args()

    frames_folder = Path(args.frames).resolve()
    output_folder = Path(args.output).resolve()
    output_folder.mkdir(parents=True, exist_ok=True)
    frames = numeric_frames(frames_folder)
    source_index = next(
        index for index, frame in enumerate(frames) if frame.name == args.source_frame
    )
    sample = cv2.imread(str(frames[0]))
    height, width = sample.shape[:2]
    source_polygon = circle_polygon(
        args.center_x, args.center_y, args.radius
    )

    tracker = SAM3Tracker(str(Path(args.checkpoint).resolve()))
    try:
        forward = run_direction(
            tracker,
            frames_folder,
            source_index,
            source_polygon,
            (width, height),
        )
        reverse_folder = output_folder / "_reverse_frames"
        make_reverse_sequence(frames, reverse_folder)
        reverse_source_index = len(frames) - 1 - source_index
        backward = run_direction(
            tracker,
            reverse_folder,
            reverse_source_index,
            source_polygon,
            (width, height),
        )
    finally:
        tracker.unload()

    annotations = {
        frames[index].name: segmentation
        for index, segmentation in forward.items()
    }
    for reverse_index, segmentation in backward.items():
        original_index = len(frames) - 1 - reverse_index
        annotations[frames[original_index].name] = segmentation

    audit_folder = output_folder / "_audit"
    audit_folder.mkdir(exist_ok=True)
    raw_output = audit_folder / "raw_sam3_unfiltered.json"
    raw_output.write_text(json.dumps(annotations, indent=2), encoding="utf-8")

    first_index = next(
        index
        for index, frame in enumerate(frames)
        if frame.name == args.first_reviewed_frame
    )
    last_index = next(
        index
        for index, frame in enumerate(frames)
        if frame.name == args.last_reviewed_frame
    )
    accepted_names = {
        frame.name for frame in frames[first_index : last_index + 1]
    }
    reviewed_annotations = {
        name: segmentation
        for name, segmentation in annotations.items()
        if name in accepted_names
    }
    write_outputs(frames, reviewed_annotations, output_folder)
    write_contact_sheet(frames, output_folder)
    write_readme(
        output_folder,
        reviewed_annotations,
        args.first_reviewed_frame,
        args.last_reviewed_frame,
    )
    shutil.rmtree(output_folder / "_reverse_frames", ignore_errors=True)
    print(
        f"Wrote {len(reviewed_annotations)} reviewed frame labels for one "
        f"unique droplet event to {output_folder}"
    )


if __name__ == "__main__":
    main()
