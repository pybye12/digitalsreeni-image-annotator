from digitalsreeni_image_annotator.annotation_history import AnnotationHistory


def test_history_undo_redo_uses_independent_snapshots():
    history = AnnotationHistory(limit=2)
    original = {"frame.jpg": {"droplet": [{"segmentation": [0, 0, 2, 0, 2, 2]}]}}
    history.record(original, "draw")
    original["frame.jpg"]["droplet"][0]["segmentation"][0] = 99

    current = {"frame.jpg": {"droplet": []}}
    label, restored = history.undo(current)
    assert label == "draw"
    assert restored["frame.jpg"]["droplet"][0]["segmentation"][0] == 0

    _, redone = history.redo(restored)
    assert redone == current


def test_history_is_bounded_and_ignores_duplicate_state():
    history = AnnotationHistory(limit=2)
    assert history.record({"value": 1}, "one")
    assert not history.record({"value": 1}, "duplicate")
    history.record({"value": 2}, "two")
    history.record({"value": 3}, "three")

    assert history.undo({"value": 4})[1] == {"value": 3}
    assert history.undo({"value": 3})[1] == {"value": 2}
    assert history.undo({"value": 2}) is None
