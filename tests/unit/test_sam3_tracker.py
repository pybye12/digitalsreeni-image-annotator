import numpy as np
from types import SimpleNamespace

import digitalsreeni_image_annotator.sam3_tracker as sam3_tracker_module
from digitalsreeni_image_annotator.sam3_tracker import SAM3Tracker


class FakePredictor:
    def __init__(self):
        self.requests = []
        self.shutdown_called = False

    def handle_request(self, request):
        self.requests.append(request)
        if request["type"] == "start_session":
            return {"session_id": "session-1"}
        return {"is_success": True}

    def handle_stream_request(self, request):
        self.requests.append(request)
        yield {
            "frame_index": 3,
            "outputs": {
                "out_obj_ids": np.array([7]),
                "out_binary_masks": np.ones((1, 4, 5), dtype=bool),
            },
        }

    def shutdown(self):
        self.shutdown_called = True


def test_tracker_uses_supported_session_and_point_prompt_api(tmp_path):
    predictor = FakePredictor()
    tracker = SAM3Tracker("unused.pt", predictor=predictor)

    assert tracker.init_state(str(tmp_path)) == "session-1"
    results = tracker.track_points(2, [(7, (12.5, 24.0))])

    assert results[0][0] == 3
    assert 7 in results[0][1]
    assert [request["type"] for request in predictor.requests] == [
        "start_session",
        "reset_session",
        "add_prompt",
        "propagate_in_video",
    ]
    prompt = predictor.requests[2]
    assert prompt["obj_id"] == 7
    assert prompt["points"] == [[12.5, 24.0]]
    assert prompt["point_labels"] == [1]
    assert prompt["rel_coordinates"] is False


def test_extract_masks_and_convert_to_annotator_segmentation():
    mask = np.zeros((20, 20), dtype=bool)
    mask[3:12, 5:15] = True
    outputs = {
        "out_obj_ids": np.array([4]),
        "out_binary_masks": mask[None, ...],
    }

    masks = SAM3Tracker.extract_masks_from_outputs(outputs)
    segmentations = SAM3Tracker.mask_to_segmentations(masks[4])

    assert masks[4].dtype == np.uint8
    assert len(segmentations) == 1
    assert len(segmentations[0]) >= 6
    assert all(isinstance(value, int) for value in segmentations[0])


def test_unload_closes_session_and_shuts_down(tmp_path):
    predictor = FakePredictor()
    tracker = SAM3Tracker("unused.pt", predictor=predictor)
    tracker.init_state(str(tmp_path))

    tracker.unload()

    assert predictor.requests[-1]["type"] == "close_session"
    assert predictor.shutdown_called
    assert tracker.predictor is None
    assert not tracker.is_initialized


def test_configures_cpu_connected_components_fallback(monkeypatch):
    cpu_fallback = object()
    module = SimpleNamespace(
        connected_components=object(),
        connected_components_cpu=cpu_fallback,
    )
    monkeypatch.setattr(
        sam3_tracker_module.importlib.util, "find_spec", lambda name: None
    )
    monkeypatch.setattr(
        sam3_tracker_module.importlib, "import_module", lambda name: module
    )

    SAM3Tracker._configure_connected_components_fallback()

    assert module.connected_components is cpu_fallback
