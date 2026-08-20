# Runtime View

## Application Startup

```
┌──────────┐
│  main()  │
└────┬─────┘
     │
     ├─> Create QApplication
     │
     ├─> Initialize ImageAnnotator
     │   │
     │   ├─> Create ImageLabel
     │   ├─> Initialize SAMUtils
     │   ├─> Create Menu Bar
     │   ├─> Create Tool Buttons
     │   ├─> Create Class List Widget
     │   └─> Create Annotation List Widget
     │
     ├─> Show Main Window
     │
     └─> Enter Event Loop (app.exec())
```

## Annotation Creation - Manual Polygon

```
User clicks on image
    │
    ├─> ImageLabel.mousePressEvent()
    │   │
    │   ├─> Check current_tool == "Polygon"
    │   │
    │   ├─> Convert screen coords to image coords
    │   │   (account for zoom_factor, offset)
    │   │
    │   ├─> Add point to current_annotation list
    │   │
    │   └─> update() to trigger repaint
    │
User continues clicking points...
    │
User presses Enter
    │
    ├─> ImageLabel.keyPressEvent()
    │   │
    │   ├─> Check key == Qt.Key_Return
    │   │
    │   ├─> main_window.add_annotation(polygon_points)
    │   │   │
    │   │   ├─> Create annotation dict:
    │   │   │   {
    │   │   │     "segmentation": [x1, y1, x2, y2, ...],
    │   │   │     "category": current_class
    │   │   │   }
    │   │   │
    │   │   ├─> all_annotations[image_file_name].append(annotation)
    │   │   │
    │   │   ├─> Update annotation list widget
    │   │   │
    │   │   └─> Trigger autosave (if enabled)
    │   │
    │   └─> Clear current_annotation
    │
    └─> update() to show final annotation
```

## SAM-Assisted Annotation

```
User selects SAM model
    │
    ├─> ImageAnnotator.change_sam_model()
    │   │
    │   └─> SAMUtils.change_sam_model("SAM 2 tiny")
    │       │
    │       ├─> Download model if first use (cached after)
    │       │
    │       └─> Load SAM model instance
    │
User clicks "SAM Point" button
    │
    ├─> sam_points_active = True
    │
User clicks positive points (left click)
    │
    ├─> ImageLabel.mousePressEvent()
    │   │
    │   └─> sam_positive_points.append((x, y))
    │
User clicks negative points (right click)
    │
    ├─> ImageLabel.mousePressEvent()
    │   │
    │   └─> sam_negative_points.append((x, y))
    │
User presses Enter to run SAM
    │
    ├─> ImageLabel.keyPressEvent()
    │   │
    │   ├─> SAMUtils.apply_sam_points(
    │   │       image=current_qimage,
    │   │       positive_points=sam_positive_points,
    │   │       negative_points=sam_negative_points
    │   │   )
    │   │   │
    │   │   ├─> Convert QImage to numpy array
    │   │   │   (handle 8-bit, 16-bit, grayscale, RGB)
    │   │   │
    │   │   ├─> sam_model.predict(
    │   │   │       image,
    │   │   │       points=[[...positive...], [...negative...]],
    │   │   │       labels=[[1, 1, ...], [0, 0, ...]]
    │   │   │   )
    │   │   │
    │   │   ├─> Extract mask from results[0].masks.data[0]
    │   │   │
    │   │   ├─> Convert mask to polygon contours
    │   │   │   (cv2.findContours)
    │   │   │
    │   │   └─> Return {"segmentation": [...], "score": float}
    │   │
    │   ├─> Display prediction as temp_sam_prediction
    │   │
    │   └─> User accepts (Enter) or rejects (Esc)
    │
User accepts prediction
    │
    ├─> main_window.add_annotation(prediction["segmentation"])
    │
    └─> Clear SAM state, reset to normal mode
```

## SAM 3 Welding Video Tracking

1. The user opens a selected range from a video or an extracted-frame folder.
2. For a video, `probe_video()` reads metadata without loading frames. The user
   selects inclusive start/end frames and a stride.
3. `VideoExtractionThread` streams the selected range through OpenCV into an
   application cache, then copies it into the project's `images/` directory
   before returning. Both phases report progress, support cancellation, and
   roll back partial files on failure.
4. `FrameSequence` maps clip positions and filenames to source-frame indices.
5. The user annotates objects on a starting frame and initializes SAM 3.
6. The app converts each selected polygon to a source mask, persistent source
   ID, and per-run SAM object ID. The adapter uses exact mask seeding when the
   installed predictor exposes it and dense foreground/background refinement
   points otherwise.
7. Initialization builds an isolated, numerically named workspace containing
   only the active sequence, so SAM 3 frame indices cannot be shifted by other
   project images.
8. `SAM3Tracker.track_polygons()` resets the session, submits all polygon prompts,
   streams forward propagation on a worker `QThread`, and converts each
   full-resolution mask to compact polygons before retaining the result.
9. Returned polygons are mapped back to their classes, committed to later
   frames, and autosaved.

The prompt frame is not overwritten. Re-running the same source-frame/source-ID
pair replaces its earlier SAM 3 generated annotations. Tracking success is
reported only after autosave succeeds; a failed save leaves the generated
annotations in memory and warns the annotator not to navigate away. Selecting another clip
closes the active SAM 3 predictor session while keeping every persisted clip
session; opening another project replaces the project-level clip collection.

## Video Project Save/Load

1. The import worker copies extracted frames into the project's `images/`
   directory before registering them in `all_images`, `image_paths`, and
   `all_annotations`.
2. Session registration and `.iap` writing are the commit step. A failed save
   removes the session, list entries, and copied frame files. Project JSON is
   written to a same-directory temporary file and atomically replaces the live
   `.iap` only after serialization and file `fsync` succeed. POSIX builds also
   attempt to `fsync` the parent directory after replacement; Windows relies
   on same-volume atomic replacement semantics.
   Ordinary project-image copies use same-directory temporary files and
   `os.replace` too. A failed copy or JSON commit removes every destination
   created by that save attempt and restores the prior `image_paths` mapping.
3. The optional `video_sessions` object records each clip's source type/path,
   FPS, selection, and ordered `{name, source_index}` entries. Direct frame
   folders use the same registration/save/rollback transaction as videos.
4. Project load remains backward compatible: projects without `video_sessions`
   load as ordinary image projects. When the key is present, the application
   rebuilds the active `FrameSequence` from the project-local image paths.
5. Missing frame files are handled by the existing missing-image workflow.
   Every saved session, including inactive clips, is pruned against the final
   project image set before ownership is rebuilt, so dead entries cannot block
   a later import.
6. Selecting an image from another saved clip activates that clip's sequence,
   so frame navigation and tracking use its own source mapping. Filename maps
   make sequence and session lookup constant-time during navigation.
7. Removing a frame from the active sequence first closes the SAM 3 session and
   deletes its isolated workspace, then rebuilds `FrameSequence`.
8. Each project image filename has at most one clip-session owner. Filename
   identity is case-folded so projects remain safe when moved to Windows. A new
   folder with an already-owned name is rejected; duplicate ownership in older
   project data is resolved in favor of the first persisted session.
9. An unowned frame that is already loaded under the exact same filename and
   has identical bytes is adopted into the new session without duplicating the
   project image. Case-only name variants are rejected rather than creating two
   annotation identities for one physical file.

## LLM-Assisted Detection (Grounding DINO + SAM)

End-to-end flow when the user clicks "Detect Current Image" in the DINO panel:

```
User clicks "Detect Current Image"
    │
    ├─> Preflight: dino_model_loaded? sam_model selected? image loaded?
    │   (early return with QMessageBox if any check fails)
    │
    ├─> Resolve DINO model path via _resolve_dino_model_path()
    │   │
    │   ├─> Path exists → skip download
    │   └─> Missing  → DINOUtils.download_model() pulls from HuggingFace Hub
    │                  (huggingface_hub.snapshot_download into models/<name>/)
    │
    ├─> Build class_configs from widgets (single source of truth):
    │   - phrases:    dino_phrase_panel.get_phrases_for(class_name)
    │   - thresholds: dino_class_table.get_class_configs()
    │
    ├─> DINOUtils.detect(qimage, class_configs, model_name)
    │   │
    │   ├─> Convert QImage to numpy (on calling thread)
    │   ├─> _run_sync: spawn QThread, pump caller's event loop while waiting
    │   ├─> On the worker thread:
    │   │     - Load (or reuse cached) GroundingDinoForObjectDetection
    │   │     - Run inference per phrase, apply per-class NMS
    │   │     - Apply cross-class NMS
    │   └─> Returns [{class_name, bbox: [x1,y1,x2,y2], score, label}, ...]
    │
    ├─> Feed DINO bboxes into SAMUtils.apply_sam_predictions_batch()
    │   │
    │   ├─> Convert QImage to numpy, run Ultralytics SAM on worker thread
    │   └─> Returns one {segmentation: [...], score: ...} per bbox
    │
    ├─> Build temp_annotations (segmentation + class + score + source="dino")
    │
    ├─> image_label.temp_annotations = ...
    ├─> image_label.setFocus()                ← so Enter/Esc work without clicking
    └─> image_label.update()                  ← orange preview masks render

User presses Enter
    │
    └─> accept_dino_results()
        │
        ├─> For each temp annotation:
        │     - add_class(class_name) if new
        │     - image_label.annotations.setdefault(class_name, []).append(ann)
        │     - add_annotation_to_list(ann)   ← assigns per-class "number"
        │
        └─> save_current_annotations()        ← syncs to all_annotations

User presses Esc
    │
    └─> reject_dino_results() → discard temp_annotations
```

**Batch mode** (`Detect All Images`) loops over every image. In "Review before
accepting" the results land in `dino_batch_results[image_name]` and the GUI
walks the user through them image-by-image. In "Auto-accept all detections"
`_commit_dino_results()` writes directly to `all_annotations` for non-current
images; for the currently-displayed image it routes through
`image_label.annotations` so the canvas stays in sync and the next
`save_current_annotations()` doesn't overwrite the additions.

## Project Save

```
User clicks "Save" or Ctrl+S
    │
    ├─> ImageAnnotator.save_project()
    │   │
    │   ├─> Check is_loading_project flag
    │   │   (skip if loading to prevent corruption)
    │   │
    │   ├─> Build project data dict:
    │   │   {
    │   │     "images": all_images,
    │   │     "image_paths": image_paths,
    │   │     "classes": list(class_mapping.keys()),
    │   │     "class_colors": class_colors,
    │   │     "annotations": all_annotations,
    │   │     "image_dimensions": image_dimensions,
    │   │     "image_shapes": image_shapes
    │   │   }
    │   │
    │   ├─> json.dump(project_data, file)
    │   │
    │   └─> Show success message (if show_message=True)
    │
    └─> Return
```

## Project Load

```
User clicks "Open" or Ctrl+O
    │
    ├─> Select .json file via QFileDialog
    │
    ├─> ImageAnnotator.load_project_data()
    │   │
    │   ├─> Set is_loading_project = True
    │   │   (disable autosave during load)
    │   │
    │   ├─> Parse JSON file
    │   │
    │   ├─> Load images:
    │   │   │
    │   │   ├─> For each image_path:
    │   │   │   │
    │   │   │   ├─> Check if multi-dimensional (TIFF/CZI)
    │   │   │   │   │
    │   │   │   │   ├─> Extract slices
    │   │   │   │   │
    │   │   │   │   └─> Store in image_slices
    │   │   │   │
    │   │   │   └─> Load as QImage for regular images
    │   │   │
    │   │   └─> Update all_images list
    │   │
    │   ├─> Load classes and colors
    │   │   │
    │   │   └─> Populate class list widget
    │   │
    │   ├─> Load annotations
    │   │   │
    │   │   ├─> all_annotations = project_data["annotations"]
    │   │   │
    │   │   └─> Update annotation list widget
    │   │
    │   ├─> Display first image
    │   │
    │   ├─> Set is_loading_project = False
    │   │
    │   └─> Show success message
    │
    └─> Return
```

## Multi-dimensional Image Loading

```
User adds TIFF stack
    │
    ├─> ImageAnnotator.add_images()
    │   │
    │   ├─> Detect .tif/.tiff extension
    │   │
    │   ├─> TiffFile(path).asarray()
    │   │   │
    │   │   └─> shape = (10, 50, 3, 512, 512)
    │   │
    │   ├─> Show DimensionDialog
    │   │   │
    │   │   ├─> User assigns: T, Z, C, _, H, W
    │   │   │   (for each dimension)
    │   │   │
    │   │   └─> dimension_string = "TZCHW"
    │   │
    │   ├─> Extract slices:
    │   │   │
    │   │   ├─> For each T, Z, C combination:
    │   │   │   │
    │   │   │   ├─> Extract 2D slice
    │   │   │   │
    │   │   │   ├─> Convert to QImage
    │   │   │   │
    │   │   │   ├─> Name: "file_T0_Z5_C0"
    │   │   │   │
    │   │   │   └─> Store in image_slices[filename]
    │   │   │
    │   │   └─> Display first slice
    │   │
    │   └─> Store dimension metadata
    │       (image_dimensions, image_shapes)
    │
User navigates slices (Up/Down arrows)
    │
    ├─> ImageLabel.keyPressEvent()
    │   │
    │   ├─> Get slice list for current stack
    │   │
    │   ├─> current_slice_index += 1 or -1
    │   │
    │   ├─> Load new slice QImage
    │   │
    │   ├─> Load annotations for this slice
    │   │   (from all_annotations[slice_name])
    │   │
    │   └─> update() to display
    │
    └─> Return
```

## Export to YOLO

```
User clicks "Export" > "YOLO v8/v11"
    │
    ├─> Select output directory
    │
    ├─> export_yolo_v5plus(all_annotations, class_mapping, ...)
    │   │
    │   ├─> Create directory structure:
    │   │   output_dir/
    │   │   ├── data.yaml
    │   │   ├── train/
    │   │   │   ├── images/
    │   │   │   └── labels/
    │   │   └── valid/
    │   │       ├── images/
    │   │       └── labels/
    │   │
    │   ├─> For each annotated image:
    │   │   │
    │   │   ├─> Copy image to train/images/ or valid/images/
    │   │   │
    │   │   ├─> Convert annotations to YOLO format:
    │   │   │   │
    │   │   │   ├─> For polygon: compute bounding box
    │   │   │   │   class_id x_center y_center width height
    │   │   │   │   (normalized to 0-1)
    │   │   │   │
    │   │   │   └─> Write to labels/image_name.txt
    │   │   │
    │   │   └─> Next image
    │   │
    │   ├─> Write data.yaml:
    │   │   train: train/images
    │   │   val: valid/images
    │   │   nc: num_classes
    │   │   names: [class1, class2, ...]
    │   │
    │   └─> Show success message
    │
    └─> Return
```
