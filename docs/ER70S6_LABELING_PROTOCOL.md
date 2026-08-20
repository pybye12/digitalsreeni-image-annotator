# ER70S-6 Labeling Protocol

This protocol matches the August 19, 2026 team instructions. Labels are
multiclass: each output pixel has one RGB value, and unlabeled pixels are
background.

## Class Palette

| Class | RGB | Rule |
|---|---:|---|
| Background | `0, 0, 0` | Includes the weld pool, spatter, and every intentionally unlabeled pixel. |
| Molten consumable | `255, 128, 0` | Starts at the solidus line and remains this class while attached to the wire. |
| Droplet | `255, 0, 0` | Begins only after detachment. It never overlaps molten consumable. |
| External arc | `0, 0, 255` | Full silhouette of the largest arc from the wire to the workpiece. |
| Internal arc | `255, 255, 0` | Inner metal-vapor arc, whether or not it touches the molten consumable. |

## Dataset Presets

- **CAVITAR droplets:** use **Welding > Add ER70S-6 CAVITAR Classes** and
  label only `molten_consumable` and `droplet`.
- **Droplet + arc:** use **Welding > Add ER70S-6 Full Arc Classes** and label
  all four foreground classes.

The presets update the colors of matching classes in an existing project, so
projects made with the older cyan/magenta palette can be corrected safely.
Custom classes remain supported for other datasets.

## Labeling Workflow

1. Open a project. For the Drive dataset, use **Add New Images** and select one
   sampled PNG sequence folder at a time. For an unsampled source video, use
   **Video > Open Video Clip** and choose a manageable range; use a stride only
   when the labeling plan allows skipped source frames.
2. Apply the preset for the recording type.
3. Use the display brightness and contrast sliders to reveal faint boundaries.
   These controls change only the preview; source pixels, SAM input, saved
   projects, and exports remain unchanged.
4. Draw or correct polygons. An attached molten region is orange; change to
   red only on the first detached frame. Leave the weld pool and small spatter
   unmarked.
5. Review every propagated mask. SAM output is a proposal, not ground truth.
6. Correct any pixels where different classes overlap, then choose **RGB
   Semantic Masks** and select a fresh output directory. Existing export
   folders are rejected to prevent stale training files. The `rgb_masks`
   directory contains dense three-channel PNG masks named
   `<source-filename>_rgb_mask.png`, and `class_rgb_mapping.txt` records the
   palette. Frames without foreground labels export as all-black masks.

For CAVITAR work, do not add arc labels just because a faint arc is visible.
Only molten consumable and detached droplets are part of that assignment.
