from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import QLabel

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator


def test_er70s6_controls_and_presets_are_available(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    window.auto_save = lambda: None
    window.show_info = lambda *args: None

    action_labels = [action.text() for action in window.findChildren(QAction)]
    assert "Add ER70S-6 &Full Arc Classes" in action_labels
    assert "Add ER70S-6 &CAVITAR Classes" in action_labels
    assert "Show ER70S-6 Labeling &Protocol" in action_labels
    assert window.brightness_slider.minimum() == -100
    assert window.brightness_slider.maximum() == 100
    assert window.contrast_slider.minimum() == -100
    assert window.contrast_slider.maximum() == 100
    assert window.export_format_selector.findText("RGB Semantic Masks") >= 0

    window.add_class("droplet", QColor(0, 255, 255))
    window.add_cavitar_welding_classes()

    assert set(window.class_mapping) == {"droplet", "molten_consumable"}
    assert window.image_label.class_colors["droplet"].getRgb()[:3] == (255, 0, 0)
    assert window.image_label.class_colors["molten_consumable"].getRgb()[:3] == (
        255,
        128,
        0,
    )


def test_canvas_first_shell_keeps_advanced_tools_contextual(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()

    assert window.sidebar.isHidden()
    assert window.image_list_widget.isHidden()
    assert window.tool_rail.isAncestorOf(window.polygon_button)
    assert window.class_panel.isAncestorOf(window.annotation_list)
    assert window.top_bar.isAncestorOf(window.export_button)
    assert window.tracking_drawer.isAncestorOf(window.sam3_init_btn)
    assert window.ai_page.isAncestorOf(window.dino_model_selector)
    assert window.tracking_drawer.isHidden()


def test_studio_exposes_common_actions_without_a_scrolling_sidebar(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()

    assert window.open_video_button.text() == "Open Video Clip..."
    assert window.cavitar_preset_button.text() == "Droplets only"
    assert window.full_arc_preset_button.text() == "Droplets + arc"
    assert window.add_class_button.text() == "+"
    assert window.class_list.maximumHeight() == 16777215
    assert window.annotation_list.maximumHeight() == 16777215
    assert "on-screen preview" in window.brightness_slider.toolTip()
    assert "exported mask" in window.brightness_slider.toolTip()
    assert "Polygon (P)" in window.polygon_button.toolTip()
    assert "active class" in window.eraser_button.toolTip()
    assert window.export_button.text() == "Export"
    assert window.review_package_button.text() == "Review sample"
    assert window.delete_button.property("buttonRole") == "danger"
    assert window.windowTitle() == "Annotation Studio"
    assert window.image_widget.objectName() == "canvasPanel"
    assert window.frame_count_label.text() == "0 loaded"
    assert window.canvas_stack.currentWidget() is window.empty_drop_zone
