from pathlib import Path
from types import SimpleNamespace

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator
from digitalsreeni_image_annotator.video_sequence import FrameInfo, FrameSequence


def test_active_video_session_restores_sequence_from_project_image_paths(tmp_path):
    frame_paths = [tmp_path / "clip_frame_00000010.jpg", tmp_path / "clip_frame_00000012.jpg"]
    for path in frame_paths:
        path.touch()
    window = SimpleNamespace(
        frame_sequence=None,
        image_paths={path.name: str(path) for path in frame_paths},
        active_video_session_id="clip-a",
        video_sessions={
            "clip-a": {
                "source_type": "video",
                "source_path": "original.mp4",
                "frames": [
                    {"name": frame_paths[0].name, "source_index": 10},
                    {"name": frame_paths[1].name, "source_index": 12},
                ],
            }
        },
    )
    window._rebuild_video_session_frame_index = lambda: (
        ImageAnnotator._rebuild_video_session_frame_index(window)
    )

    ImageAnnotator._restore_active_frame_sequence(window)

    assert [frame.source_index for frame in window.frame_sequence.frames] == [10, 12]
    assert window.frame_sequence.folder == tmp_path


def test_video_session_restore_drops_missing_frames(tmp_path):
    existing = tmp_path / "frame_1.jpg"
    existing.touch()
    window = SimpleNamespace(
        frame_sequence=None,
        image_paths={existing.name: str(existing)},
        active_video_session_id="clip-a",
        video_sessions={
            "clip-a": {
                "frames": [
                    {"name": existing.name, "source_index": 1},
                    {"name": "missing.jpg", "source_index": 2},
                ]
            }
        },
    )
    window._rebuild_video_session_frame_index = lambda: (
        ImageAnnotator._rebuild_video_session_frame_index(window)
    )

    ImageAnnotator._restore_active_frame_sequence(window)

    assert [frame.name for frame in window.frame_sequence.frames] == [existing.name]
    assert window.video_sessions["clip-a"]["frames"] == [
        {"name": existing.name, "source_index": 1}
    ]
    assert window._video_session_by_frame == {existing.name: "clip-a"}


def test_video_sessions_save_all_clips_and_remove_cache_paths(tmp_path):
    frame_path = tmp_path / "frame.jpg"
    frame_path.touch()
    sequence = FrameSequence(
        tmp_path,
        [FrameInfo(0, frame_path, frame_path.name, source_index=45)],
    )
    window = SimpleNamespace(
        frame_sequence=sequence,
        image_paths={frame_path.name: str(frame_path)},
        video_sessions={
            "clip-a": {
                "source_type": "video",
                "cache_dir": "temporary-cache",
                "frames": [
                    {"name": frame_path.name, "source_index": 45},
                ],
            },
            "clip-b": {
                "source_type": "video",
                "frames": [{"name": "missing.jpg", "source_index": 90}],
            },
        },
    )

    saved = ImageAnnotator._video_sessions_for_save(window)

    assert list(saved) == ["clip-a"]
    assert saved["clip-a"]["frames"] == [
        {"name": frame_path.name, "source_index": 45}
    ]
    assert "cache_dir" not in saved["clip-a"]


def test_video_sessions_do_not_save_missing_paths_still_present_in_mapping(tmp_path):
    missing_path = tmp_path / "missing.jpg"
    window = SimpleNamespace(
        image_paths={missing_path.name: str(missing_path)},
        video_sessions={
            "inactive-clip": {
                "frames": [{"name": missing_path.name, "source_index": 90}],
            }
        },
    )

    assert ImageAnnotator._video_sessions_for_save(window) == {}


def test_save_project_does_nothing_while_project_is_loading():
    window = SimpleNamespace(is_loading_project=True)

    assert ImageAnnotator.save_project(window) is False


def test_session_index_keeps_only_one_owner_for_each_frame_name():
    window = SimpleNamespace(
        video_sessions={
            "first": {"frames": [{"name": "shared.jpg", "source_index": 1}]},
            "second": {"frames": [{"name": "shared.jpg", "source_index": 9}]},
        },
        _video_session_by_frame={},
    )

    ImageAnnotator._rebuild_video_session_frame_index(window)

    assert window._video_session_by_frame == {"shared.jpg": "first"}
    assert list(window.video_sessions) == ["first"]


def test_session_index_treats_case_variants_as_one_frame():
    window = SimpleNamespace(
        video_sessions={
            "first": {"frames": [{"name": "Shared.JPG", "source_index": 1}]},
            "second": {"frames": [{"name": "shared.jpg", "source_index": 2}]},
        },
        _video_session_by_frame={},
    )

    ImageAnnotator._rebuild_video_session_frame_index(window)

    assert window._video_session_by_frame == {"shared.jpg": "first"}
    assert list(window.video_sessions) == ["first"]


def test_restore_removes_empty_session_and_revalidates_active_id(tmp_path):
    other_frame = tmp_path / "other.jpg"
    other_frame.touch()
    window = SimpleNamespace(
        frame_sequence=None,
        image_paths={other_frame.name: str(other_frame)},
        active_video_session_id="missing-clip",
        video_sessions={
            "missing-clip": {
                "frames": [{"name": "missing.jpg", "source_index": 1}]
            },
            "remaining-clip": {
                "frames": [{"name": other_frame.name, "source_index": 2}]
            },
        },
    )
    window._rebuild_video_session_frame_index = lambda: (
        ImageAnnotator._rebuild_video_session_frame_index(window)
    )
    window._restore_active_frame_sequence = lambda: (
        ImageAnnotator._restore_active_frame_sequence(window)
    )

    ImageAnnotator._restore_active_frame_sequence(window)

    assert list(window.video_sessions) == ["remaining-clip"]
    assert window.active_video_session_id == "remaining-clip"
    assert window.frame_sequence.frames[0].name == other_frame.name
    assert window._video_session_by_frame == {
        other_frame.name: "remaining-clip"
    }


def test_prune_removes_missing_frames_from_inactive_sessions(tmp_path):
    active_frame = tmp_path / "active.jpg"
    active_frame.touch()
    window = SimpleNamespace(
        image_paths={active_frame.name: str(active_frame)},
        active_video_session_id="active-clip",
        video_sessions={
            "active-clip": {
                "frames": [{"name": active_frame.name, "source_index": 1}]
            },
            "inactive-clip": {
                "frames": [{"name": "missing.jpg", "source_index": 2}]
            },
        },
        _video_session_by_frame={},
    )
    window._rebuild_video_session_frame_index = lambda: (
        ImageAnnotator._rebuild_video_session_frame_index(window)
    )

    ImageAnnotator._prune_video_sessions_to_project_images(window)

    assert list(window.video_sessions) == ["active-clip"]
    assert window._video_session_by_frame == {
        active_frame.name: "active-clip"
    }
