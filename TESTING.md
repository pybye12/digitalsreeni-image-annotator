# Testing Infrastructure

## Overview

This document describes the testing infrastructure for the DigitalSreeni Image Annotator project.

## Phase 1, Milestone 1.1: Testing Infrastructure ✓

### Completed Tasks

1. **Test Dependencies** ✓
   - Added pytest, pytest-qt, pytest-cov, pytest-mock to [requirements.txt](requirements.txt)
   - Using flexible version constraints (>=) instead of pinned versions

2. **Test Directory Structure** ✓
   ```
   tests/
   ├── __init__.py
   ├── conftest.py               # Pytest configuration and fixtures
   ├── unit/
   │   ├── __init__.py
   │   ├── test_utils.py         # Tests for utility functions
   │   └── test_conversions.py   # Tests for coordinate conversions
   ├── integration/
   │   ├── __init__.py
   │   └── test_export_formats.py # Tests for COCO, YOLO, Pascal VOC exports
   └── ui/
       ├── __init__.py
       └── test_video_ui.py       # Focused menu and event-routing tests
   ```

3. **Pytest Configuration** ✓
   - Created [pytest.ini](pytest.ini) with:
     - Test discovery patterns
     - Coverage settings
     - Custom markers (unit, integration, ui, slow)

4. **Unit Tests** ✓
   - **[tests/unit/test_utils.py](tests/unit/test_utils.py)**: 25+ test cases
     - `TestCalculateArea`: 10 tests for polygon and bbox area calculations
     - `TestCalculateBbox`: 9 tests for bounding box extraction from polygons
     - `TestNormalizeImage`: 11 tests for image normalization (8-bit, 16-bit, float)

   - **[tests/unit/test_conversions.py](tests/unit/test_conversions.py)**: 20+ test cases
     - `TestGetImageCoordinates`: Screen-to-image coordinate conversion tests
     - `TestCoordinateConversionProperties`: Property-based tests with various zoom/offset values
     - `TestEdgeCases`: Edge cases (zero zoom, negative coordinates, large values)

5. **Integration Tests** ✓
   - **[tests/integration/test_export_formats.py](tests/integration/test_export_formats.py)**: 20+ test cases
     - `TestCOCOExport`: Tests for COCO JSON format export
     - `TestYOLOExport`: Tests for YOLO format export
     - `TestPascalVOCExport`: Tests for Pascal VOC XML export
     - `TestExportWithSlices`: Tests for multi-dimensional image slice export
     - `TestExportEdgeCases`: Edge case handling

6. **CI/CD Pipeline** ✓
   - Created [.github/workflows/tests.yml](.github/workflows/tests.yml)
   - Multi-platform testing: Ubuntu, Windows, macOS
   - Multi-version testing: Python 3.10, 3.11, 3.12, 3.13
   - Automated coverage reporting (Codecov integration)
   - Coverage report artifacts

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-qt pytest-cov pytest-mock
```

Or install all dependencies including tests:
```bash
pip install -e .
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Focused UI tests only
pytest tests/ui -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src/digitalsreeni_image_annotator --cov-report=term-missing --cov-report=html

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### Run Specific Test Files

```bash
pytest tests/unit/test_utils.py -v
pytest tests/unit/test_conversions.py -v
pytest tests/integration/test_export_formats.py -v
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v
```

## Test Coverage Goals

- **Phase 1 Target**: 60% code coverage
- **Phase 2 Target**: 80% code coverage
- **Phase 3 Target**: 90% code coverage

## Headless Testing

All tests run under `QT_QPA_PLATFORM=offscreen` so they work in CI and SSH
sessions without a display. The Linux runner needs the Qt 6 platform-plugin
deps (`libxcb-cursor0`, `libegl1`, `libgl1`, etc. — see
[`.github/workflows/tests.yml`](.github/workflows/tests.yml) for the full list).

## Video Clip Manual Checklist

Run this checklist when changing `video_clip.py`, `video_clip_dialog.py`,
`video_sequence.py`, project persistence, or tracking initialization:

1. Launch the app and create a project in a new empty folder.
2. Use **Video > Open Video Clip...** on a normal MP4/AVI. Select frames
   100-149 with stride 2 and verify that 25 frames appear.
3. Verify the status bar shows clip position and the original source frame.
   Use A/D to navigate and C to copy a selected polygon forward.
4. Add a custom class, draw a polygon, correct it with Paint Brush/Eraser, and
   verify annotations stay attached to the correct frame.
5. Start a large extraction and press Cancel. Verify no partial clip appears
   in the image list or project `images/` directory and the app remains usable.
6. Import a second clip, then click frames from each clip. Verify A/D navigation
   stays inside the selected frame's clip.
7. Try to open another frame folder containing a filename already owned by the
   first clip. Verify the app rejects it without changing the active session.
   Repeat with a case-only variant such as `001.JPG` / `001.jpg`. An exact,
   unowned project copy should instead be adopted without a duplicate entry.
8. Add an unrelated ordinary image, initialize video tracking, and propagate a
   reviewed polygon. Verify masks land only on the active clip's ordered frames.
9. Save, close, and reopen the `.iap`. Repeat navigation for both clips and
   verify annotations and source-frame numbers survive.
10. Initialize tracking, remove a frame before the current frame, and initialize
   tracking again. Verify the removed frame is absent and propagated masks stay
   aligned with the remaining images. Repeat with the Delete key.
11. Toggle dark mode and check the clip dialog and progress dialog for readable
   text and native theme colors.
12. Export COCO or YOLO and confirm the video frames use the same export path as
    ordinary image annotations.
13. Move brightness and contrast through their full ranges. Verify faint image
    details change while annotation coordinates, source files, and SAM input do
    not change. Reset both controls to zero.
14. Apply both ER70S-6 presets. Verify the CAVITAR preset creates only molten
    consumable and droplet, while the full preset creates all four classes with
    the protocol RGB colors.
15. Export RGB Semantic Masks. Inspect a labeled frame and an unlabeled frame;
    verify exact palette values and an all-black background-only mask.
16. Confirm RGB export rejects polygons from different classes that overlap.
    Correct the overlap, select a fresh output directory, and export again.
17. Attempt a second RGB export into the same directory. Confirm it is rejected
    instead of mixing stale and current files.
18. Import a video clip and verify extracted project frames are PNG files.

## Future Testing Work

1. **Expand UI Tests** (pytest-qt)
   - Test annotation creation workflows
   - Test project save/load
   - Test SAM integration
   - Test progress-dialog cancellation timing with pytest-qt

2. **Add Performance Tests**
   - Benchmark critical operations
   - Video frame extraction speed
   - SAM inference latency
   - Batch processing throughput

3. **Increase Coverage**
   - Test error handling paths
   - Test edge cases in ImageLabel
   - Test multi-dimensional image handling
   - Test export format edge cases

4. **Add Regression Tests**
   - Test backward compatibility
   - Test project migration (v1 → v2)

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-qt documentation](https://pytest-qt.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)

## Contributing

When adding new features:
1. Write tests first (TDD approach preferred)
2. Ensure all tests pass: `pytest tests/ -v`
3. Check coverage: `pytest tests/ --cov=src/digitalsreeni_image_annotator`
4. Aim for 80%+ coverage on new code
5. Add docstrings to test functions

When fixing bugs:
1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test passes
4. Check that other tests still pass
