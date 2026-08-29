import cv2
import numpy as np
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QListView

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator
from digitalsreeni_image_annotator.video_sequence import FrameSequence
from digitalsreeni_image_annotator.theme import (
    CLASS_PANEL_WIDTH,
    FILMSTRIP_HEIGHT,
    TOOL_RAIL_WIDTH,
    TOP_BAR_HEIGHT,
)


def test_studio_shell_has_canvas_first_regions_and_empty_state(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()

    assert [action.text().replace("&", "") for action in window.menuBar().actions()] == [
        "File",
        "Edit",
        "View",
        "Help",
    ]
    assert window.top_bar.height() == TOP_BAR_HEIGHT
    assert window.tool_rail.width() == TOOL_RAIL_WIDTH
    assert window.class_panel.width() == CLASS_PANEL_WIDTH
    assert window.filmstrip_panel.height() == FILMSTRIP_HEIGHT
    assert window.canvas_stack.currentWidget() is window.empty_drop_zone
    assert not window.tool_rail.isEnabled()
    assert not window.export_button.isEnabled()
    assert window.image_list.viewMode() == QListView.ViewMode.IconMode
    assert window.image_list.iconSize() == QSize(88, 50)


def test_studio_shell_enables_workspace_after_loading_frame(qtbot, tmp_path):
    from PyQt6.QtGui import QImage

    image_path = tmp_path / "frame.jpg"
    image = QImage(80, 60, QImage.Format.Format_RGB32)
    image.fill(0)
    assert image.save(str(image_path))

    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    window.add_images_to_list([str(image_path)], auto_save=False)

    assert window.canvas_stack.currentWidget() is window.scroll_area
    assert window.tool_rail.isEnabled()
    assert window.class_panel.isEnabled()
    assert window.export_button.isEnabled()
    assert window.image_list.count() == 1
    assert not window.image_list.item(0).icon().isNull()


def test_accept_and_advance_suggests_mask_on_next_frame(qtbot, tmp_path):
    paths = []
    for index, center_x in enumerate((30, 34)):
        frame = np.zeros((80, 100, 3), dtype=np.uint8)
        cv2.circle(frame, (center_x, 40), 10, (230, 230, 230), -1)
        path = tmp_path / f"{index:06d}.jpg"
        assert cv2.imwrite(str(path), frame)
        paths.append(str(path))

    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    window.auto_save = lambda: None
    window.class_mapping = {"droplet": 1}
    window.image_label.class_colors["droplet"] = QColor(255, 0, 0)
    window.image_label.class_visibility["droplet"] = True
    window.add_images_to_list(paths, auto_save=False)
    window.frame_sequence = FrameSequence.from_paths(tmp_path, paths)
    window.image_label.annotations = {
        "droplet": [
            {
                "category_id": 1,
                "category_name": "droplet",
                "segmentation": [20, 30, 40, 30, 40, 50, 20, 50],
            }
        ]
    }

    window.accept_and_go_to_next_frame()

    assert window.image_file_name == "000001.jpg"
    suggestion = window.all_annotations["000001.jpg"]["droplet"][0]
    assert suggestion["source"] == "propagated_candidate"
    assert 0.0 <= suggestion["confidence"] <= 1.0
