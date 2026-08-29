from digitalsreeni_image_annotator.workflow_metrics import WorkflowMetrics


def test_workflow_metrics_reports_per_frame_baseline_and_eta():
    metrics = WorkflowMetrics()
    metrics.enter_frame("001.jpg", now=10.0)
    metrics.action(3)
    metrics.mouse_move(0, 0)
    metrics.mouse_move(3, 4)
    metrics.commit(now=20.0)

    summary = metrics.summary()
    assert summary == {
        "frames": 1,
        "seconds_per_frame": 10.0,
        "actions_per_frame": 3.0,
        "mouse_distance_per_frame": 5.0,
    }
    assert metrics.eta_seconds(50) == 500.0
