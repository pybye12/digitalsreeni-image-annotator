from pathlib import Path

import pytest

from digitalsreeni_image_annotator.video_sequence import FrameSequence


def test_frame_sequence_matches_sam3_numeric_stem_sort(tmp_path):
    for name in ["10.png", "2.png", "1.png"]:
        (tmp_path / name).touch()

    sequence = FrameSequence.from_folder(tmp_path)

    assert [frame.name for frame in sequence.frames] == ["1.png", "2.png", "10.png"]
    assert [frame.source_index for frame in sequence.frames] == [1, 2, 10]
    assert sequence.index_for_name("2.png") == 1
    assert sequence.name_for_index(2) == "10.png"


def test_frame_sequence_matches_sam3_lexical_fallback(tmp_path):
    for name in ["frame2.png", "frame10.png", "frame1.png"]:
        (tmp_path / name).touch()

    sequence = FrameSequence.from_folder(tmp_path)

    assert [frame.name for frame in sequence.frames] == [
        "frame1.png",
        "frame10.png",
        "frame2.png",
    ]

def test_frame_sequence_lexical_fallback_is_case_sensitive_like_sam3(tmp_path):
    for name in ["a.png", "B.png", "c.png"]:
        (tmp_path / name).touch()

    sequence = FrameSequence.from_folder(tmp_path)

    assert [frame.name for frame in sequence.frames] == ["B.png", "a.png", "c.png"]


def test_frame_sequence_rejects_empty_folder(tmp_path):
    with pytest.raises(ValueError, match="No supported image frames"):
        FrameSequence.from_folder(tmp_path)


def test_frame_sequence_from_paths_preserves_clip_order_and_source_indices(tmp_path):
    paths = [tmp_path / "frame_10.jpg", tmp_path / "frame_20.jpg"]

    sequence = FrameSequence.from_paths(tmp_path, paths, [10, 20])

    assert [frame.name for frame in sequence.frames] == [
        "frame_10.jpg",
        "frame_20.jpg",
    ]
    assert sequence.frame_for_name("frame_20.jpg").source_index == 20


def test_frame_sequence_from_paths_rejects_mismatched_source_indices(tmp_path):
    with pytest.raises(ValueError, match="equal lengths"):
        FrameSequence.from_paths(tmp_path, [tmp_path / "one.jpg"], [])
