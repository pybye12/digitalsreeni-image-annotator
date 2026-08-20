# DigitalSreeni Image Annotator and Toolkit

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI version](https://img.shields.io/pypi/v/digitalsreeni-image-annotator.svg?style=flat-square)

A powerful and user-friendly tool for annotating images with polygons and rectangles, built with PyQt6. Now with additional supporting tools for comprehensive image processing and dataset management.

## Support the Project

If you find this project helpful, consider supporting it:

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?business=FGQL3CNJGJP9C&no_recurring=0&item_name=If+you+find+this+Image+Annotator+project+helpful%2C+consider+supporting+it%3A&currency_code=USD)

![DigitalSreeni Image Annotator Demo](screenshots/digitalsreeni-image-annotator-demo.gif)

## Watch the demo (of v0.8.0):

[![Watch the demo video](https://img.youtube.com/vi/aArn1f1YIQk/maxresdefault.jpg)](https://youtu.be/aArn1f1YIQk)

@DigitalSreeni
Dr. Sreenivas Bhattiprolu

## Features

- Semi-automated annotations with SAM-2 assistance (Segment Anything Model) — Because who doesn't love a helpful AI sidekick?
- Manual annotations with polygons and rectangles — For when you want to show SAM-2 who's really in charge.
- Paint brush and Eraser tools with adjustable pen sizes (use - and = on your keyboard)
- Merge annotations - For when SAM-2's guesswork needs a little human touch.
- Save and load projects for continued work.
- Save As... and Autosave functionality.
- A secret game, for when you are bored.
- Import existing COCO JSON annotations with images.
- Export annotations to COCO JSON, YOLO v8/v11, labeled images, class-ID semantic labels, RGB semantic masks, and Pascal VOC.
- Handle multi-dimensional images (TIFF stacks and CZI files).
- Zoom and pan for detailed annotations.
- Support for multiple classes with customizable colors.
- Non-destructive brightness and contrast controls for revealing faint boundaries.
- User-friendly interface with intuitive controls.
- Change the application font size on the fly — Make your annotations as big or small as your caffeine level requires.
- Dark mode for those late-night annotation marathons — Who needs sleep when you have dark mode?
- Pick appropriate pre-trained SAM2 model for flexible and improved semi-automated annotations.
- Track user-labeled objects forward through extracted video frames with the optional SAM 3 integration.
- Change the class of an annotation to a different class.
- Turn visibility of a class ON and OFF.
- YOLO (beta) training using current annotations and loading trained model to segment images.
- Area measurements for annotations displayed next to the Annotation name.
- Sort annotations by name/number or area.
- Additional supporting tools:
  - Annotation statistics for current annotations
  - COCO JSON combiner
  - Dataset splitter
  - Stack to slices converter
  - Image patcher
  - Image augmenter
- Project Details: View and edit project metadata, including creation date, last modified date, image information, and custom notes.
- Advanced Project Search: Search through multiple projects using complex queries with logical operators (AND, OR) and parentheses.
- Slice Registration
  - Align image slices in a stack with multiple registration methods
  - Support for various reference frames and transformation types
  - Stack Interpolation
    - Adjust Z-spacing in image stacks
    - Multiple interpolation methods with memory-efficient processing
  - DICOM Converter
    - Convert DICOM files to TIFF format (single stack or individual slices)
    - Preserve metadata and physical dimensions
    - Export metadata to JSON for reference

## Operating System Requirements

This application is built using PyQt6 and runs on macOS, Windows and Linux. On Linux you'll need the standard Qt 6 runtime libraries (notably `libxcb-cursor0`, `libegl1`, `libgl1`, and the XCB plugin set) — `sudo apt install libxcb-cursor0 libegl1 libgl1 libxcb-xinerama0 libxkbcommon-x11-0` covers the common ones on Debian/Ubuntu.

## Installation

### Install this video-labeling fork from source

To use the large-video, SAM 3 tracking, ER70S-6 preset, display adjustment,
and RGB-mask export changes from Abdul's development branch:

```bash
git clone --branch abdul/welding-video-extension --single-branch https://github.com/pybye12/digitalsreeni-image-annotator.git
cd digitalsreeni-image-annotator
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .
sreeni
```

On Linux or macOS, activate with `source .venv/bin/activate`. On PowerShell,
use `.venv\Scripts\Activate.ps1`.
The PyPI release described below does not include this branch's additions yet.

### Watch the installation walkthough video:

[![Watch the installation video](https://img.youtube.com/vi/VI6V95eUUpY/maxresdefault.jpg)](https://youtu.be/VI6V95eUUpY)

You can install the DigitalSreeni Image Annotator directly from PyPI:

```bash
pip install digitalsreeni-image-annotator
```

The application uses the Ultralytics library, so there's no need to separately install SAM2 or PyTorch, or download SAM2 models manually.

### GPU acceleration (NVIDIA)

The PyTorch wheel installed by default from PyPI is **CPU-only** on Windows. If you have an NVIDIA GPU, SAM and Grounding DINO will run dramatically faster on CUDA — reinstall PyTorch from the CUDA index:

```bash
pip uninstall -y torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

If `cu128` errors as "no matching distribution", try `cu124` instead. Verify the install picked up your GPU:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

You should see `True` and your GPU name. For other platforms or driver combinations, use the official selector at <https://pytorch.org/get-started/locally/>.

## Usage

1. Run the DigitalSreeni Image Annotator application:

   ```bash
   digitalsreeni-image-annotator
   ```

   or

   ```bash
   sreeni
   ```

   or

   ```bash
   python -m digitalsreeni_image_annotator.main
   ```

2. Using the application:

   - Click "New Project" or use Ctrl+N to start a new project.
   - Use "Add New Images" to import images, including TIFF stacks and CZI files.
   - Add classes using the "Add Classes" button. Welding projects can use the ER70S-6 presets under the **Welding** menu.
   - Adjust brightness and contrast when boundaries are faint. These controls affect only the preview, not source images or exports.
   - Select a class and use the Polygon or Rectangle or Paint Brush tool to create manual annotations.
   - To use SAM2-assisted annotation:
     - Select a model from the "Pick a SAM Model" dropdown. It's recommended to use smaller models like SAM2 tiny or SAM2 small. SAM2 large is not recommended as it may crash the application on systems with limited resources.
     - Note: When you select a model for the first time, the application needs to download it. This process may take a few seconds to a minute, depending on your internet connection speed. Subsequent uses of the same model will be faster as it will already be cached locally, in your working directory.
     - Click the "SAM-Assisted" button to activate the tool.
     - Draw a rectangle around objects of interest to allow SAM2 to automatically detect objects.
     - Note that SAM2 provides various outputs with different scores, and only the top-scoring region will be displayed. If the desired result isn't achieved on the first try, draw again.
     - For low-quality images where SAM2 may not auto-detect objects, manual tools may be necessary.
     - When SAM2 auto-detect partial objects, use polygon or paint brush tools to manually define the remaining region and use the Merge tool to combine both annotations into one.
     - When SAM2 over-annotates objects, extending the annotation beyond object's boundaries, use the Eraser tool to clean up the edges.
     - Both paint brush and eraser tools can be adjusted for pen size by using - or = keys on your keyboard.
   - Edit existing annotations by double-clicking on them.
   - Edit existing annotations using the Eraser tool. Adjust the eraser size by using - or = keys on your keyboard.
   - Merge connected annotations by selecting them from the Annotations list and clicking the Merge button.
   - Change the class of an annotation to a different class.
   - Turn visibility of a class ON and OFF.
   - Use YOLO (beta) training with current annotations and load the trained model to segment images and convert segmentations to annotations. (Currently not implemented for slices or stacks, just single images.)
   - Accept/reject one or select class predictions at a time to add them as annotations.
   - View area measurements for annotations displayed next to the Annotation name.
   - Sort annotations by name/number or area.
   - Save your project using "Save Project" or Ctrl+S. Alternatively, you can use Save As... to save the project with a different name.
   - Use "Open Project" or Ctrl+O to load a previously saved project.
   - Click "Import Annotations with Images" to load existing COCO JSON annotations along with their images.
   - Use "Export Annotations" to save annotations in various formats (COCO JSON, YOLO v8/v11, labeled images, class-ID semantic labels, RGB semantic masks, and Pascal VOC).
     - Note: YOLO export (and import) is now compatible with YOLOv11 structure. (Project directory includes data.yaml, train, and valid directories, with train and valid both having images and labels subdirectories.)
   - Project Details:
     - Access project details by selecting "Project Details" from the Project menu.
     - View project metadata such as creation date, last modified date, and image information.
     - Add or edit custom project notes.
     - Project details are automatically saved when you make changes to the notes.
   - Advanced Project Search:
     - Access the search functionality by selecting "Search Projects" from the Project menu.
     - Search through multiple projects using complex queries.
     - Use logical operators (AND, OR) and parentheses for advanced search criteria.
     - Search covers project name, class names, image names, and project notes.
     - Example queries:
       - "cells AND dog": Find projects containing both "cells" and "dog"
       - "cells OR bacteria": Find projects containing either "cells" or "bacteria"
       - "cells AND (dog OR monkey)": Find projects containing "cells" and either "dog" or "monkey"
       - "(project1 OR project2) AND (cells OR bacteria)": More complex nested queries
     - Double-click on search results to open the corresponding project.
   - Access additional tools under the Tools menu bar:
     - Annotation Statistics
     - COCO JSON Combiner
     - Dataset Splitter
     - Stack to Slices Converter
     - Image Patcher
     - Image Augmenter
   - Each tool opens a separate UI to guide you through the respective task.
   - Access the help documentation by clicking the "Help" button or pressing F1.
   - Explore the interface – you might stumble upon some hidden gems and secret features!

3. Keyboard shortcuts:
   - Ctrl + N: Create a new project
   - Ctrl + O: Open an existing project
   - Ctrl + S: Save the current project
   - Ctrl + W: Close the current project
   - Ctrl + Shift + S: Open Annotation Statistics
   - F1: Open the help window
   - Ctrl + Wheel: Zoom in/out
   - Hold Ctrl and drag: Pan the image
   - Esc: Cancel current annotation, exit edit mode, or exit SAM-assisted annotation
   - Enter: Finish current annotation, exit edit mode, or accept SAM-generated mask
   - Up/Down Arrow Keys: Navigate through slices in multi-dimensional images
   - - and =: Adjust pen size for paint brush and eraser tools

## SAM 3 Welding Video Tracking

This fork adds an optional SAM 3 workflow for propagating a manually labeled
object through extracted video frames. SAM 3 does not decide whether a region
is an `internal_arc`, `external_arc`, `droplet`, or `molten_consumable`. The
user chooses the class and draws the starting polygon; SAM 3 then attempts to
follow that same visual region in later frames. The tracker applies the same
minimum-area, relative-size, and drift checks to every class; very small
polygons may be rejected as tracking noise.

### Open a large video as a manageable clip

Use **Video > Open Video Clip...** to work directly from MP4, AVI, MOV, MKV,
M4V, or WMV files. The clip dialog reports the video's size, frame count, FPS,
and duration. Choose an inclusive start frame, inclusive end frame, and stride
(`1` keeps every frame, `5` keeps every fifth frame).

The application decodes the selected range on a background thread and writes
one frame at a time to a temporary cache. The same worker copies those frames
into the project's `images/` directory before the clip appears, so a large
import does not freeze the interface during save. It never keeps the full video
in RAM. Press **Cancel** to roll back extraction and copying. The extracted
frames use collision-resistant names, appear in the normal image list, and
retain their original source-frame numbers in the status bar.

Use **A** and **D** to move backward and forward, **C** to copy a selected
annotation to the next frame, and the existing Polygon, Paint Brush, and Eraser
tools to correct masks. Saving the `.iap` commits the clip order and
source-frame mapping for the next session. Multiple imported clips retain
separate source mappings; selecting a
frame activates its clip for A/D navigation and tracking. The class list
remains fully user-defined.
Extracted project frames use lossless PNG by default so faint scientific image
boundaries are not changed by a second lossy encoding step.

### Install and launch on Windows with Git Bash

Run these commands from Git Bash. Python 3.11 is recommended for the current
SAM 3 environment.

```bash
git clone --branch abdul/welding-video-extension --single-branch https://github.com/pybye12/digitalsreeni-image-annotator.git
cd digitalsreeni-image-annotator

py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .

python -m digitalsreeni_image_annotator.main
```

Video tracking also requires [Meta's official SAM 3 package](https://github.com/facebookresearch/sam3)
installed in the same virtual environment, a compatible SAM 3 checkpoint, and
a CUDA-capable NVIDIA GPU. Put the checkpoint at
`sam3-001.pt` in the repository root, or select the `.pt`/`.pth` file when the
application asks for it. The regular manual tools and SAM 2 features do not
require this checkpoint.

### Track an annotation forward

1. Select **Video > Open Video Clip...** and choose a frame range, or select
   **Video > Open Frame Folder...** for an already extracted image sequence.
2. Select **Welding > Add ER70S-6 Full Arc Classes**, or choose the CAVITAR preset when labeling only molten consumable and droplets.
3. Choose the class you want to label.
4. Use **Polygon** to outline the object on a clear starting frame, then press
   **Enter** to finish the polygon.
5. Click the finished polygon's row in the **Annotations** panel. Selecting the
   class or clicking only on the canvas is not enough.
6. Click **Load Video Frames to SAM 3** and wait for the success message.
7. Click **Track Selected Forward**. Use **Track All Objects** only when every
   polygon on the current frame should be propagated.
8. Move through the image list and review the generated masks. Correct errors
   with **Polygon**, **Paint Brush**, and **Eraser**.
9. Save the `.iap` project, then choose an export format and click
   **Export Annotations** when the reviewed labels are ready to share.

If the application reports **No valid polygon annotations selected**, return
to step 5 and select the polygon in the Annotations panel. Only annotations
containing a valid segmentation polygon can be tracked; a rectangle alone is
not a tracking prompt.

### Validate internal and external arc tracking

Do not conclude that arc tracking works or fails from setup problems or a
single frame. Use the same controlled check for both `internal_arc` and
`external_arc`:

1. Choose a continuous sequence where the arc boundary is visible for at least
   20 frames.
2. Draw a careful source polygon on a clear frame and track it forward.
3. Review the source frame, early frames, the middle of the sequence, and the
   final frames. Record the first frame where the mask leaves the intended arc,
   follows glare or a reflection, merges with another bright region, or loses
   a meaningful part of the boundary.
4. Repeat on at least three different sequences for each arc class. Include
   stable footage and difficult examples with glare or shape changes.
5. Save the project and record a short screen capture showing the source
   polygon, propagated masks, frame names, corrections, and export result.

A successful run proves that the integration can propagate an arc prompt. It
does not by itself prove segmentation accuracy. Arc suitability should be
decided from the reviewed sequences and the agreed labeling protocol. If SAM 3
drifts, the manual drawing tools remain available for producing ground-truth
arc labels.

For the team palette and boundary rules, see the [ER70S-6 Labeling Protocol](docs/ER70S6_LABELING_PROTOCOL.md). For implementation details, limitations, and completed engineering checks, see [SAM 3 Welding Video Annotator Adaptation](docs/SAM3_WELDING_VIDEO_ADAPTATION.md).

## Known Issues and Bug Fixes

- The application may not work correctly on Linux systems. Extensive testing has not been done yet.
- When loading a YOLO model trained on different classes compared to the loaded YAML file, the application now gives a message to the user about the mismatch instead of crashing.
- Various other bugs have been addressed to improve overall stability and performance.

## Development

For development purposes, you can clone the repository and install it in editable mode:

1. Clone the repository:

   ```bash
   git clone https://github.com/bnsreenu/digitalsreeni-image-annotator.git
   cd digitalsreeni-image-annotator
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package and its dependencies in editable mode:

   ```bash
   pip install -e .
   ```

4. Start the application:
   ```bash
   python -m src.digitalsreeni_image_annotator.main
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all my [YouTube](http://www.youtube.com/c/DigitalSreeni) subscribers who inspired me to work on this project
- Inspired by the need for efficient image annotation in computer vision tasks

## Contact

Dr. Sreenivas Bhattiprolu - [@DigitalSreeni](https://twitter.com/DigitalSreeni)

Project Link: [https://github.com/bnsreenu/digitalsreeni-image-annotator](https://github.com/bnsreenu/digitalsreeni-image-annotator)

## Citing

If you use this software in your research, please cite it as follows:

Bhattiprolu, S. (2024). DigitalSreeni Image Annotator [Computer software].
https://github.com/bnsreenu/digitalsreeni-image-annotator

```bibtex
@software{digitalsreeni_image_annotator,
  author = {Bhattiprolu, Sreenivas},
  title = {DigitalSreeni Image Annotator},
  year = {2024},
  url = {https://github.com/bnsreenu/digitalsreeni-image-annotator}
}
```
