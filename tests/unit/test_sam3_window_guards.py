from pathlib import Path
from types import SimpleNamespace

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator
from digitalsreeni_image_annotator.video_sequence import FrameInfo, FrameSequence


class BusyWindow:
    _sam3_inference_in_flight = True

    def __init__(self):
        self.warnings = []

    def show_warning(self, title, message):
        self.warnings.append((title, message))


def test_open_specific_project_is_blocked_during_sam3_tracking():
    window = BusyWindow()

    ImageAnnotator.open_specific_project(window, "other-project.iap")

    assert window.warnings


def test_switch_image_is_blocked_during_sam3_tracking():
    window = BusyWindow()

    assert ImageAnnotator.switch_image(window, object()) is None


def test_annotation_delete_is_blocked_during_sam3_tracking():
    window = BusyWindow()
    window._reject_while_sam3_busy = lambda: ImageAnnotator._reject_while_sam3_busy(
        window
    )

    assert ImageAnnotator.delete_selected_annotations(window) is None
    assert window.warnings


def test_remove_image_is_blocked_during_sam3_tracking():
    window = BusyWindow()
    window._reject_while_sam3_busy = lambda: ImageAnnotator._reject_while_sam3_busy(
        window
    )

    assert ImageAnnotator.remove_image(window) is None
    assert window.warnings


def test_frame_folder_allows_exact_project_copy_but_rejects_name_collision(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    source.mkdir()
    project.mkdir()
    (source / "001.png").write_bytes(b"same-frame")
    (project / "001.png").write_bytes(b"same-frame")
    sequence = FrameSequence(
        source, [FrameInfo(0, source / "001.png", "001.png")]
    )
    window = SimpleNamespace(image_paths={"001.png": str(project / "001.png")})

    assert ImageAnnotator._sam3_frame_name_conflicts(window, sequence) == []

    (project / "001.png").write_bytes(b"different-frame")
    assert ImageAnnotator._sam3_frame_name_conflicts(window, sequence) == ["001.png"]
