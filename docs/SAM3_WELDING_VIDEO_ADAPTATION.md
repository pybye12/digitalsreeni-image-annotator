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
3's supported visual-point prompt API. When the installed official Meta SAM 3
build exposes its underlying tracker mask-prompt capability, the adapter then
replaces the approximate point result with the exact source polygon mask before
propagation. This keeps the track anchored to the exact object the user
selected instead of asking SAM 3 to choose among nearby image regions.

The public session request layer does not currently expose mask prompts, so
mask seeding is feature-detected against the official model object. Builds
without that capability retain the point prompt and source-overlap rejection
fallback instead of failing at startup.

### Stable source identity

SAM object IDs can change when the user selects a different subset or order.
Each source annotation therefore receives a persistent `sam3_source_id`.
Generated results store that identity so a repeated run replaces only results
belonging to the correct source object.

Droplet sources also store the same identity as `droplet_event_id`. Every mask
propagated from that source keeps the event ID, so one physical droplet is
counted once across its full tracked lifetime instead of once per frame. When
the droplet merges into the weld pool and is missing/rejected for two
consecutive frames, its track ends and its event remains in the cumulative
count. The ended identity cannot latch onto a later droplet. A newly formed
large droplet adds one when the user annotates it and starts a new track.

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
Disconnected small components are treated as tracking noise and are never
saved as additional object regions. The largest component is also rejected if
it is smaller than 15% of the manually selected source polygon or fewer than
50 pixels. These geometric gates are class-agnostic; in the droplet workflow
they also prevent small welding spatter from becoming droplet annotations.
Masks that grow implausibly large compared with the source polygon or video
frame are rejected as tracking drift.

The prompt-frame result must overlap the manually selected source polygon. If
it does not, propagation stops immediately and the UI reports that no tracking
annotations were saved. This prevents a plausible-sized but unrelated bright
feature from being mislabeled as the selected object.

### Threading and lifecycle safety

Model loading and propagation use the existing `_run_sync` worker-thread
pattern. Qt continues processing events during inference, so the main editing
window is disabled around each synchronous SAM 3 call. Queued project, frame,
class, image, import, and canvas-editing events therefore cannot mutate state
while model results are being produced. The application-wide DINO review filter
also consumes Enter/Escape during this interval without accepting or rejecting
pending predictions.

Selecting another persisted clip closes the active predictor session and its
temporary tracker workspace; it does not delete the saved clip session.
Clearing or opening another project unloads the tracker. A project image name
can belong to only one persisted clip session.

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
   background point prompts, then uses the exact polygon as a tracker mask seed
   when supported by the installed official SAM 3 build.
7. SAM 3 propagates object masks through later frames.
8. Worker-side filtering retains only the largest geometrically plausible main
   component and rejects implausible drift. Contour conversion produces one
   compact polygon per tracked object. For droplet labels, the same gate also
   rejects small spatter.
9. The application maps polygons back to filenames/classes and autosaves.

The prompt frame is not overwritten. Repeating the same source-frame/source-ID
run replaces its prior generated annotations rather than appending duplicates.

The Annotation Statistics window reports both **Droplet frame annotations**
and **Unique tracked droplet events**. The first measures generated mask volume;
the second is the cumulative large-droplet count. Brand-new droplets are not
automatically discovered by this visual-tracking workflow and must be marked
once before their new event can be counted and propagated. After a successful
droplet tracking run, the UI also reports the updated unique large-droplet
count immediately.

## Verification Performed

Automated and integration verification completed during implementation:

- The full pytest suite passed after the tracking/filtering changes.
- The focused SAM 3 tracker suite passed after the source-overlap gate.
- Python `compileall` passed.
- The real local SAM 3 checkpoint loaded on an NVIDIA RTX 3060 Laptop GPU.
- A real 99-frame welding directory initialized successfully.
- Prompt experiments confirmed that unnormalized image coordinates and
  ambiguous single-point prompts are unsuitable for these welding frames.
- A real large-droplet polygon on `001154.jpg` caused SAM 3 to select a
  different bright feature. The source-overlap gate rejected it on the first
  frame and saved zero false droplet/spatter annotations.
- Exact polygon mask seeding was then validated on the same source droplet
  across 11 frames. The accepted main-component areas ranged from about 1,238
  to 2,020 pixels, while disconnected small spatter was excluded.

## Manual Validation Still Required

Before calling the research workflow fully validated, perform and record a
human-reviewed tracking-quality test using representative welding classes.
Measure where tracking first drifts, follows a reflection, merges with another
bright region, or loses the object.

The current verification proves integration compatibility and execution. It
does not establish segmentation accuracy across glare, occlusion, rapid
motion, or substantial shape changes.
