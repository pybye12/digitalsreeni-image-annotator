from pathlib import Path

from digitalsreeni_image_annotator.video_clip import VideoMetadata
from digitalsreeni_image_annotator.video_clip_dialog import VideoClipDialog


def test_video_clip_dialog_defaults_to_a_500_frame_clip(qtbot):
    dialog = VideoClipDialog(
        VideoMetadata(Path("large.mp4"), 10_000, 2_000.0, 800, 504)
    )
    qtbot.addWidget(dialog)

    selection = dialog.selection()

    assert selection.start_frame == 0
    assert selection.end_frame == 499
    assert selection.stride == 1
    assert "500 frames" in dialog.selection_summary.text()


def test_video_clip_dialog_updates_selected_frame_count(qtbot):
    dialog = VideoClipDialog(
        VideoMetadata(Path("video.mp4"), 100, 50.0, 640, 480)
    )
    qtbot.addWidget(dialog)

    dialog.start_frame.setValue(10)
    dialog.end_frame.setValue(20)
    dialog.stride.setValue(3)

    assert dialog.selection().output_frame_count(100) == 4
    assert "4 frames" in dialog.selection_summary.text()
