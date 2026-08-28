"""Team-friendly review package export."""

import html
import os
import shutil

import numpy as np
from PIL import Image

from .export_formats import _color_to_rgb, export_rgb_semantic_masks


def export_review_package(
    all_annotations,
    class_colors,
    image_paths,
    slices,
    image_slices,
    output_dir,
    selected_image_names,
):
    """Export exact RGB masks plus overlays and a browser review page."""
    selected_names = [str(name) for name in selected_image_names]
    if not selected_names:
        raise ValueError("Select at least one labeled frame to review.")

    output_dir = os.path.abspath(os.fspath(output_dir))
    archive_path = f"{output_dir}.zip"
    if os.path.lexists(archive_path) or (os.path.isdir(output_dir) and os.listdir(output_dir)):
        raise ValueError(
            "Review package export requires an unused output directory."
        )
    os.makedirs(output_dir, exist_ok=True)

    selected_set = set(selected_names)
    selected_annotations = {
        name: all_annotations.get(name, {}) for name in selected_names
    }
    selected_paths = {
        key: value
        for key, value in image_paths.items()
        if os.path.basename(str(key)) in selected_set
        or os.path.basename(str(value)) in selected_set
    }
    selected_slices = [entry for entry in slices if entry[0] in selected_set]
    selected_image_slices = {
        stack_name: [entry for entry in stack_slices if entry[0] in selected_set]
        for stack_name, stack_slices in image_slices.items()
    }
    selected_image_slices = {
        stack_name: stack_slices
        for stack_name, stack_slices in selected_image_slices.items()
        if stack_slices
    }

    output_dir = export_rgb_semantic_masks(
        selected_annotations,
        class_colors,
        selected_paths,
        selected_slices,
        selected_image_slices,
        output_dir,
    )
    images_dir = os.path.join(output_dir, "images")
    masks_dir = os.path.join(output_dir, "rgb_masks")
    overlays_dir = os.path.join(output_dir, "overlays")
    os.makedirs(overlays_dir)

    cards = []
    exported_names = []
    for image_name in sorted(os.listdir(images_dir), key=str.casefold):
        image_path = os.path.join(images_dir, image_name)
        if not os.path.isfile(image_path):
            continue
        mask_name = f"{image_name}_rgb_mask.png"
        mask_path = os.path.join(masks_dir, mask_name)
        if not os.path.isfile(mask_path):
            continue

        with Image.open(image_path) as source_image:
            source_rgb = np.asarray(source_image.convert("RGB"), dtype=np.uint8)
        with Image.open(mask_path) as mask_image:
            mask_rgb = np.asarray(mask_image.convert("RGB"), dtype=np.uint8)
        if source_rgb.shape != mask_rgb.shape:
            raise ValueError(
                f"Image and mask dimensions do not match for '{image_name}'."
            )

        overlay = source_rgb.copy()
        labeled = np.any(mask_rgb != 0, axis=2)
        overlay[labeled] = np.clip(
            source_rgb[labeled].astype(np.float32) * 0.45
            + mask_rgb[labeled].astype(np.float32) * 0.55,
            0,
            255,
        ).astype(np.uint8)
        overlay_name = f"{image_name}_overlay.png"
        Image.fromarray(overlay, mode="RGB").save(
            os.path.join(overlays_dir, overlay_name)
        )

        cards.append(
            "<article class='card'>"
            f"<h2>{html.escape(image_name)}</h2>"
            "<div class='views'>"
            f"<figure><img src='images/{html.escape(image_name, quote=True)}' "
            "alt='Source image'><figcaption>Source</figcaption></figure>"
            f"<figure><img src='overlays/{html.escape(overlay_name, quote=True)}' "
            "alt='Annotation overlay'><figcaption>Overlay</figcaption></figure>"
            f"<figure><img src='rgb_masks/{html.escape(mask_name, quote=True)}' "
            "alt='RGB mask'><figcaption>Exact RGB mask</figcaption></figure>"
            "</div></article>"
        )
        exported_names.append(image_name)

    if not exported_names:
        raise ValueError("No selected frames could be exported for review.")

    color_rows = []
    for class_name, color in class_colors.items():
        if class_name.startswith("Temp-"):
            continue
        red, green, blue = _color_to_rgb(color)
        color_rows.append(
            "<li>"
            f"<span class='swatch' style='background:rgb({red},{green},{blue})'></span>"
            f"<strong>{html.escape(class_name)}</strong> &nbsp; "
            f"RGB ({red}, {green}, {blue})</li>"
        )

    review_path = os.path.join(output_dir, "review.html")
    with open(review_path, "w", encoding="utf-8") as review_file:
        review_file.write(
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Annotation review</title><style>"
            "body{margin:0;background:#0b1220;color:#e8eef8;font-family:Arial,sans-serif}"
            "main{max-width:1400px;margin:auto;padding:32px}"
            "header{margin-bottom:28px}.eyebrow{color:#78a7ff;font-weight:700;"
            "letter-spacing:.12em;text-transform:uppercase;font-size:12px}"
            "h1{margin:8px 0;font-size:32px}.sub{color:#aebbd0}"
            ".legend{display:flex;gap:18px;flex-wrap:wrap;padding:0;list-style:none}"
            ".legend li{display:flex;align-items:center;color:#c7d2e5}"
            ".swatch{width:14px;height:14px;border-radius:4px;margin-right:8px;"
            "border:1px solid #526178}.card{background:#121c2c;border:1px solid #26364d;"
            "border-radius:14px;padding:20px;margin:18px 0;box-shadow:0 12px 32px #05091266}"
            ".card h2{font-size:16px;margin:0 0 16px}.views{display:grid;"
            "grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}"
            "figure{margin:0;background:#090f19;border-radius:10px;overflow:hidden}"
            "img{display:block;width:100%;height:auto}figcaption{padding:10px 12px;"
            "color:#aebbd0;font-size:13px}@media(max-width:800px){.views{grid-template-columns:1fr}}"
            "</style></head><body><main><header><div class='eyebrow'>Team review package</div>"
            f"<h1>{len(exported_names)} labels ready for review</h1>"
            "<p class='sub'>Compare the source, visual overlay, and exact training mask. "
            "The overlay is for inspection only.</p><ul class='legend'>"
            + "".join(color_rows)
            + "</ul></header>"
            + "".join(cards)
            + "</main></body></html>"
        )

    summary_path = os.path.join(output_dir, "README.txt")
    with open(summary_path, "w", encoding="utf-8") as summary_file:
        summary_file.write(
            "ANNOTATION REVIEW PACKAGE\n\n"
            f"Frames: {len(exported_names)}\n"
            "Open review.html in any web browser to inspect the labels.\n\n"
            "images/ contains the original source frames.\n"
            "rgb_masks/ contains the exact model-training masks.\n"
            "overlays/ contains previews for human review only.\n"
        )

    archive_path = shutil.make_archive(output_dir, "zip", output_dir)

    return {
        "output_dir": output_dir,
        "review_path": review_path,
        "summary_path": summary_path,
        "archive_path": archive_path,
        "frame_count": len(exported_names),
    }

