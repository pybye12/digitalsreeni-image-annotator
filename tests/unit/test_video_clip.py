from pathlib import Path

import numpy as np
import pytest

from digitalsreeni_image_annotator import video_clip
from digitalsreeni_image_annotator.video_clip import (
    TRACKER_WORKSPACE_MARKER,
    VideoClipError,
    VideoExtractionCancelled,
    VideoFrameSelection,
    VideoMetadata,
    cleanup_managed_video_directory,
    copy_extracted_clip_to_directory,
    create_tracker_frame_workspace,
    extract_video_frames,
    probe_video,
    video_clip_cache_directory,
)


class FakeCapture:
    def __init__(self, frames, properties=None, opened=True, seekable=True):
        self.frames = frames
        self.properties = properties or {}
        self.opened = opened
        self.seekable = seekable
        self.position = 0
        self.released = False

    def isOpened(self):
        return self.opened

    def get(self, prop):
        if prop == video_clip.cv2.CAP_PROP_POS_FRAMES:
            return self.position
        return self.properties.get(prop, 0)

    def set(self, prop, value):
        if prop == video_clip.cv2.CAP_PROP_POS_FRAMES:
            if not self.seekable:
                return False
            self.position = int(value)
            return True
        return False

    def read(self):
        if self.position >= len(self.frames):
            return False, None
        frame = self.frames[self.position]
        self.position += 1
        return True, frame.copy()

    def release(self):
        self.released = True


def test_video_frame_selection_is_inclusive_and_strided():
    selection = VideoFrameSelection(start_frame=2, end_frame=8, stride=3)

    assert list(selection.source_indices(10)) == [2, 5, 8]
    assert selection.output_frame_count(10) == 3


@pytest.mark.parametrize(
    "selection, message",
    [
        (VideoFrameSelection(-1, 2), "negative"),
        (VideoFrameSelection(4, 2), "at or after"),
        (VideoFrameSelection(0, 10), "outside"),
        (VideoFrameSelection(0, 2, 0), "at least 1"),
    ],
)
def test_video_frame_selection_rejects_invalid_ranges(selection, message):
    with pytest.raises(ValueError, match=message):
        selection.validate(10)


def test_probe_video_returns_metadata_and_releases_capture(tmp_path, monkeypatch):
    video_path = tmp_path / "sample.avi"
    video_path.touch()
    properties = {
        video_clip.cv2.CAP_PROP_FRAME_COUNT: 120,
        video_clip.cv2.CAP_PROP_FPS: 40.0,
        video_clip.cv2.CAP_PROP_FRAME_WIDTH: 800,
        video_clip.cv2.CAP_PROP_FRAME_HEIGHT: 504,
    }
    capture = FakeCapture([], properties=properties)
    monkeypatch.setattr(video_clip.cv2, "VideoCapture", lambda _: capture)

    metadata = probe_video(video_path)

    assert metadata.frame_count == 120
    assert metadata.fps == 40.0
    assert metadata.duration_seconds == 3.0
    assert (metadata.width, metadata.height) == (800, 504)
    assert capture.released


def test_probe_video_rejects_unreadable_video(tmp_path, monkeypatch):
    video_path = tmp_path / "broken.mp4"
    video_path.touch()
    capture = FakeCapture([], opened=False)
    monkeypatch.setattr(video_clip.cv2, "VideoCapture", lambda _: capture)

    with pytest.raises(VideoClipError, match="could not open"):
        probe_video(video_path)

    assert capture.released


def test_probe_video_normalizes_invalid_fps(tmp_path, monkeypatch):
    video_path = tmp_path / "sample.avi"
    video_path.touch()
    properties = {
        video_clip.cv2.CAP_PROP_FRAME_COUNT: 10,
        video_clip.cv2.CAP_PROP_FPS: float("nan"),
        video_clip.cv2.CAP_PROP_FRAME_WIDTH: 320,
        video_clip.cv2.CAP_PROP_FRAME_HEIGHT: 240,
    }
    monkeypatch.setattr(
        video_clip.cv2,
        "VideoCapture",
        lambda _: FakeCapture([], properties=properties),
    )

    assert probe_video(video_path).fps == 0.0


def test_extract_video_frames_streams_only_selected_frames(tmp_path, monkeypatch):
    frames = [np.full((3, 4, 3), index, dtype=np.uint8) for index in range(8)]
    capture = FakeCapture(frames)
    monkeypatch.setattr(video_clip.cv2, "VideoCapture", lambda _: capture)

    written_values = []

    def fake_imwrite(path, frame, _options):
        Path(path).write_bytes(b"frame")
        written_values.append(int(frame[0, 0, 0]))
        return True

    monkeypatch.setattr(video_clip.cv2, "imwrite", fake_imwrite)
    metadata = VideoMetadata(tmp_path / "source.avi", 8, 20.0, 4, 3)
    selection = VideoFrameSelection(2, 7, 2)
    progress = []

    result = extract_video_frames(
        metadata,
        selection,
        tmp_path / "clip",
        progress_callback=lambda completed, total: progress.append((completed, total)),
    )

    assert written_values == [2, 4, 6]
    assert [frame.source_index for frame in result.frames] == [2, 4, 6]
    assert all(frame.path.suffix == ".png" for frame in result.frames)
    assert all(frame.name.endswith(".png") for frame in result.frames)
    assert progress == [(1, 3), (2, 3), (3, 3)]
    assert capture.released


def test_extract_video_frames_releases_capture_when_cancelled(tmp_path, monkeypatch):
    frames = [np.zeros((2, 2, 3), dtype=np.uint8) for _ in range(4)]
    capture = FakeCapture(frames)
    monkeypatch.setattr(video_clip.cv2, "VideoCapture", lambda _: capture)

    with pytest.raises(VideoExtractionCancelled):
        extract_video_frames(
            VideoMetadata(tmp_path / "source.avi", 4, 10.0, 2, 2),
            VideoFrameSelection(0, 3),
            tmp_path / "clip",
            cancel_check=lambda: True,
        )

    assert capture.released


def test_extract_video_frames_falls_back_when_random_seek_is_unavailable(
    tmp_path, monkeypatch
):
    frames = [np.full((2, 2, 3), index, dtype=np.uint8) for index in range(6)]
    captures = []

    def capture_factory(_):
        capture = FakeCapture(frames, seekable=False)
        captures.append(capture)
        return capture

    monkeypatch.setattr(video_clip.cv2, "VideoCapture", capture_factory)
    written_values = []

    def fake_imwrite(path, frame, _options):
        Path(path).write_bytes(b"frame")
        written_values.append(int(frame[0, 0, 0]))
        return True

    monkeypatch.setattr(video_clip.cv2, "imwrite", fake_imwrite)

    extract_video_frames(
        VideoMetadata(tmp_path / "source.avi", 6, 10.0, 2, 2),
        VideoFrameSelection(3, 5),
        tmp_path / "clip",
    )

    assert len(captures) == 2
    assert all(capture.released for capture in captures)
    assert written_values == [3, 4, 5]


def test_extract_video_frames_can_request_jpeg_output(tmp_path, monkeypatch):
    capture = FakeCapture([np.zeros((2, 2, 3), dtype=np.uint8)])
    monkeypatch.setattr(video_clip.cv2, "VideoCapture", lambda _: capture)
    options = []

    def fake_imwrite(path, _frame, write_options):
        Path(path).write_bytes(b"frame")
        options.append(write_options)
        return True

    monkeypatch.setattr(video_clip.cv2, "imwrite", fake_imwrite)
    clip = extract_video_frames(
        VideoMetadata(tmp_path / "source.avi", 1, 10.0, 2, 2),
        VideoFrameSelection(0, 0),
        tmp_path / "jpeg_clip",
        image_format="jpg",
        jpeg_quality=91,
    )

    assert clip.frames[0].path.suffix == ".jpg"
    assert options == [[video_clip.cv2.IMWRITE_JPEG_QUALITY, 91]]


def test_video_cache_directory_changes_with_selection(tmp_path):
    video_path = tmp_path / "same name.mp4"
    video_path.write_bytes(b"video")

    first = video_clip_cache_directory(
        video_path, VideoFrameSelection(0, 9), tmp_path / "cache"
    )
    second = video_clip_cache_directory(
        video_path, VideoFrameSelection(10, 19), tmp_path / "cache"
    )

    assert first != second
    assert first.parent == tmp_path / "cache"
    assert "same_name" in first.name


def test_video_cache_directory_retains_digest_after_a_long_stem(tmp_path):
    video_path = tmp_path / (("long" * 30) + ".mp4")
    video_path.write_bytes(b"video")

    cache_dir = video_clip_cache_directory(
        video_path,
        VideoFrameSelection(0, 1),
        tmp_path / "cache",
    )

    assert len(cache_dir.name.rsplit("_", 1)[-1]) == 12
    assert len(cache_dir.name) <= 61


def test_tracker_workspace_contains_only_ordered_numeric_frames(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    frame_paths = []
    for name in ("z-last.jpg", "a-first.jpg"):
        path = source_dir / name
        path.write_bytes(name.encode("ascii"))
        frame_paths.append(path)
    unrelated = source_dir / "unrelated.jpg"
    unrelated.write_bytes(b"unrelated")

    workspace = create_tracker_frame_workspace(
        frame_paths,
        tmp_path / "tracker-cache",
    )

    tracker_frames = sorted(
        path for path in workspace.iterdir() if path.suffix.lower() == ".jpg"
    )
    assert [path.name for path in tracker_frames] == [
        "000000000000.jpg",
        "000000000001.jpg",
    ]
    assert [path.read_bytes() for path in tracker_frames] == [
        b"z-last.jpg",
        b"a-first.jpg",
    ]
    assert unrelated.name not in {path.name for path in tracker_frames}
    assert cleanup_managed_video_directory(
        workspace,
        tmp_path / "tracker-cache",
        TRACKER_WORKSPACE_MARKER,
    )
    assert not workspace.exists()


def test_cleanup_refuses_unmarked_or_out_of_root_directories(tmp_path):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()

    unmarked = allowed_root / "unmarked"
    unmarked.mkdir()
    assert not cleanup_managed_video_directory(unmarked, allowed_root)
    assert unmarked.is_dir()

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / video_clip.VIDEO_CACHE_MARKER).touch()
    assert not cleanup_managed_video_directory(outside, allowed_root)
    assert outside.is_dir()

    (allowed_root / video_clip.VIDEO_CACHE_MARKER).touch()
    assert not cleanup_managed_video_directory(allowed_root, allowed_root)
    assert allowed_root.is_dir()


def test_cleanup_refuses_a_symlink_even_when_target_is_below_root(tmp_path):
    allowed_root = tmp_path / "allowed"
    target = allowed_root / "target"
    target.mkdir(parents=True)
    (target / video_clip.VIDEO_CACHE_MARKER).touch()
    link = allowed_root / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are unavailable in this environment")

    assert not cleanup_managed_video_directory(link, allowed_root)
    assert target.is_dir()


def test_copy_extracted_clip_rolls_back_when_cancelled_during_final_copy(tmp_path):
    metadata = VideoMetadata(tmp_path / "source.avi", 1, 20.0, 8, 8)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    source_paths = []
    for position in range(1):
        path = cache_dir / f"frame_{position}.jpg"
        path.write_bytes(bytes([position]))
        source_paths.append(path)
    clip = video_clip.ExtractedVideoClip(
        metadata=metadata,
        selection=VideoFrameSelection(0, 0),
        output_dir=cache_dir,
        frames=tuple(
            video_clip.ExtractedFrame(index, path, path.name, index / 20.0)
            for index, path in enumerate(source_paths)
        ),
    )
    cancel_calls = iter((False, True))
    project_images = tmp_path / "project" / "images"

    with pytest.raises(VideoExtractionCancelled):
        copy_extracted_clip_to_directory(
            clip,
            project_images,
            cancel_check=lambda: next(cancel_calls),
        )

    assert not list(project_images.glob("*.jpg"))


def test_copy_extracted_clip_removes_partial_file_after_copy_error(
    tmp_path, monkeypatch
):
    metadata = VideoMetadata(tmp_path / "source.avi", 1, 20.0, 8, 8)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    source_path = cache_dir / "frame.jpg"
    source_path.write_bytes(b"complete-source")
    clip = video_clip.ExtractedVideoClip(
        metadata=metadata,
        selection=VideoFrameSelection(0, 0),
        output_dir=cache_dir,
        frames=(
            video_clip.ExtractedFrame(0, source_path, source_path.name, 0.0),
        ),
    )
    project_images = tmp_path / "project" / "images"

    def partial_copy(_source, destination):
        Path(destination).write_bytes(b"partial")
        raise OSError("simulated disk failure")

    monkeypatch.setattr(video_clip.shutil, "copy2", partial_copy)

    with pytest.raises(OSError, match="disk failure"):
        copy_extracted_clip_to_directory(clip, project_images)

    assert not (project_images / source_path.name).exists()


def test_real_opencv_video_range_roundtrip(tmp_path):
    video_path = tmp_path / "synthetic.avi"
    writer = video_clip.cv2.VideoWriter(
        str(video_path),
        video_clip.cv2.VideoWriter_fourcc(*"MJPG"),
        20.0,
        (64, 48),
    )
    if not writer.isOpened():
        pytest.skip("OpenCV MJPG writer is unavailable in this environment")
    try:
        for index in range(12):
            writer.write(np.full((48, 64, 3), index * 15, dtype=np.uint8))
    finally:
        writer.release()

    metadata = probe_video(video_path)
    clip = extract_video_frames(
        metadata,
        VideoFrameSelection(3, 9, 2),
        tmp_path / "real_clip",
    )

    assert metadata.frame_count == 12
    assert [frame.source_index for frame in clip.frames] == [3, 5, 7, 9]
    decoded_means = [
        float(video_clip.cv2.imread(str(frame.path)).mean())
        for frame in clip.frames
    ]
    assert decoded_means == pytest.approx([45, 75, 105, 135], abs=4)
