from digitalsreeni_image_annotator.annotation_statistics import summarize_annotations


def test_droplet_event_count_is_not_inflated_across_frames():
    annotations = {
        "001.png": {
            "droplet": [
                {"droplet_event_id": "drop-a"},
                {"droplet_event_id": "drop-b"},
            ]
        },
        "002.png": {
            "droplet": [
                {"droplet_event_id": "drop-a"},
                {"droplet_event_id": "drop-b"},
            ]
        },
        "003.png": {"droplet": [{"droplet_event_id": "drop-b"}]},
    }

    summary = summarize_annotations(annotations)

    assert summary["droplet_frame_annotations"] == 5
    assert summary["unique_droplet_events"] == 2


def test_new_large_droplet_source_increments_event_count_once():
    annotations = {
        "001.png": {"droplet": [{"sam3_source_id": "old-drop"}]},
        "010.png": {"droplet": [{"sam3_source_id": "new-drop"}]},
        "011.png": {"droplet": [{"sam3_source_id": "new-drop"}]},
        "012.png": {"internal_arc": [{}]},
    }

    summary = summarize_annotations(annotations)

    assert summary["unique_droplet_events"] == 2
    assert summary["droplet_frame_annotations"] == 3
