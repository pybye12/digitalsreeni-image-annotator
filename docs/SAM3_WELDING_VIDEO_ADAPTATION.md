# SAM 3 Welding Video Annotator Adaptation

## Purpose

This fork adapts DigitalSreeni Image Annotator for extracted welding-video
frames and integrates Meta's SAM 3 video predictor. A user labels an object on
one starting frame, assigns a welding class, and propagates that object forward
through later frames.

The integration is a visual-prompt tracking workflow. It does not currently
provide text prompts, automatic open-vocabulary classification, backward
tracking, or a review-before-commit queue.

## What Was Inherited

The upstream application already provided:

- PyQt6 image annotation tools.
- Polygon, rectangle, brush, and SAM 2-assisted single-image annotation.
- Project persistence and autosave.
- COCO and YOLO export.
- Annotation class and color management.

## What Was Added

### Video frame workflow

`FrameSequence` loads an extracted-frame directory and reproduces Meta SAM 3's
ordering:

- Numeric filename stems sort numerically.
- Other filenames sort using case-sensitive lexical order.

The application maps between SAM 3's integer frame indices and the annotator's
filename-keyed annotations. Video menu actions and A/D/C shortcuts provide
frame navigation and manual copy-forward behavior.

### Welding classes

The Welding menu can add:

- `internal_arc`
- `external_arc`
- `droplet`
- `molten_consumable`

SAM 3 does not classify these concepts. The user assigns the class to a source
annotation, and tracking preserves that class.

### Official SAM 3 session adapter

`SAM3Tracker` wraps Meta's supported session-based video predictor:

```text
start_session
-> reset_session
-> add_prompt
-> propagate_in_video
-> close_session
```

Each selected polygon is validated with Shapely and rasterized into a binary
source mask. Interior foreground points and a ring of background points are
derived from that exact mask, normalized to the frame, and sent through SAM
3's supported visual-point prompt API. This keeps the prompt anchored to the
large droplet the user selected instead of asking SAM 3 to choose among nearby
bright welding regions.

### Stable source identity

SAM object IDs can change when the user selects a different subset or order.
Each source annotation therefore receives a persistent `sam3_source_id`.
Generated results store that identity so a repeated run replaces only results
belonging to the correct source object.

### Mask-to-polygon conversion

SAM 3 returns binary masks. OpenCV contour extraction converts each mask into
the annotator's existing flattened polygon schema:

```python
{
    "segmentation": [x1, y1, x2, y2, ...],
    "category_id": 3,
    "category_name": "droplet",
    "source": "sam3_track",
    "sam3_source_frame": "001218.jpg",
    "sam3_source_id": "persistent-source-id",
    "sam3_object_id": 1,
}
```

Using the existing schema preserves rendering, project saving, COCO export,
and YOLO segmentation export.

Before conversion, only the largest connected mask component is retained.
Disconnected small components are treated as spatter and are never saved as
additional droplets. The largest component is also rejected if it is smaller
than 15% of the manually selected source droplet or fewer than 50 pixels.
Masks that grow implausibly large compared with the source polygon or video
frame are rejected as tracking drift.

The prompt-frame result must overlap the manually selected source polygon. If
it does not, propagation stops immediately and the UI reports that no tracking
annotations were saved. This prevents a plausible-sized but unrelated bright
feature from being mislabeled as the selected droplet.

### Threading and lifecycle safety

Model loading and propagation use the existing `_run_sync` worker-thread
pattern. Qt continues processing events during inference, so state-changing
project, frame, class, image, import, and annotation actions are blocked while
SAM 3 is active.

Opening another frame folder invalidates the old session. Clearing or opening
another project unloads the tracker. Exact project-local copies of source
frames may be reopened; same-name files with different content are rejected.

### Windows fallback and unload

When neither `cc_torch` nor Triton is available, the adapter uses Meta's CPU
connected-components implementation. The neural model still runs on CUDA, but
this post-processing operation is slower.

Unload closes the active session, requests predictor shutdown, moves available
model objects to CPU, runs garbage collection, and clears the CUDA allocator.

## End-to-End Runtime Flow

1. Open an extracted-frame folder through **Video > Open Frame Folder**.
2. Add or select a welding class.
3. Draw a polygon around an object on a starting frame.
4. Initialize SAM 3 with **Load Video Frames to SAM 3**.
5. Select an annotation and choose **Track Selected Forward**, or track all
   valid polygons on the current frame.
6. The application converts each source polygon into normalized foreground and
   background point prompts.
7. SAM 3 propagates object masks through later frames.
8. Worker-side filtering retains only a droplet-sized main component, rejects
   small spatter and implausible drift, then contour conversion produces one
   compact polygon per tracked droplet.
9. The application maps polygons back to filenames/classes and autosaves.

The prompt frame is not overwritten. Repeating the same source-frame/source-ID
run replaces its prior generated annotations rather than appending duplicates.

## Verification Performed

Automated and integration verification completed during implementation:

- Full pytest suite: 90 tests passed after the tracking/filtering changes.
- Focused SAM 3 tracker suite: 15 tests passed after the source-overlap gate.
- Python `compileall` passed.
- The real local SAM 3 checkpoint loaded on an NVIDIA RTX 3060 Laptop GPU.
- A real 99-frame welding directory initialized successfully.
- Prompt experiments confirmed that unnormalized image coordinates and
  ambiguous single-point prompts are unsuitable for these welding frames.
- A real large-droplet polygon on `001154.jpg` caused SAM 3 to select a
  different bright feature. The source-overlap gate rejected it on the first
  frame and saved zero false droplet/spatter annotations.

## Manual Validation Still Required

Before calling the research workflow fully validated, perform and record a
human-reviewed tracking-quality test using representative welding classes.
Measure where tracking first drifts, follows a reflection, merges with another
bright region, or loses the object.

The current verification proves integration compatibility and execution. It
does not establish segmentation accuracy across glare, occlusion, rapid
motion, or substantial shape changes.

## Suggested Mentor Summary

> I adapted an existing PyQt6 image annotator for welding-video frames and
> integrated Meta's official SAM 3 session predictor. Existing labeled
> polygons become normalized foreground/background point prompts, SAM 3
> propagates masks forward, and the masks are converted back into the
> application's polygon format. To match our annotation criteria, I added
> connected-component and relative-area filtering so small spatter is not
> counted as a droplet. The main integration risks were frame-index
> correctness, persistent source identity, GUI reentrancy, project lifecycle
> safety, and Windows GPU compatibility. Automated and GPU smoke tests pass;
> the remaining task is a human-reviewed tracking-quality evaluation on
> representative welding data.
