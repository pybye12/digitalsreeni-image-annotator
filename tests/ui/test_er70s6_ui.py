from PyQt6.QtGui import QAction, QColor

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
