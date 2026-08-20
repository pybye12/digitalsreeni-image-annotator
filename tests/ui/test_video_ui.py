from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QAction, QKeyEvent
from PyQt6.QtWidgets import QApplication, QDialog

from digitalsreeni_image_annotator.annotator_window import ImageAnnotator


def test_video_menu_and_sam_controls_render(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()

    action_labels = [action.text() for action in window.findChildren(QAction)]

    assert "Open Video &Clip..." in action_labels
    assert window.sam3_init_btn.text() == "Load Video Frames to SAM 3"
    assert window.sam3_track_forward_btn.text() == "Track Selected Forward"


def test_dino_review_shortcuts_are_consumed_while_sam3_is_busy(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    accepted = []
    rejected = []
    window.accept_dino_results = lambda: accepted.append(True)
    window.reject_dino_results = lambda: rejected.append(True)
    window.image_label.temp_annotations = [{"source": "dino"}]
    window._sam3_inference_in_flight = True

    enter = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier,
    )
    escape = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Escape,
        Qt.KeyboardModifier.NoModifier,
    )

    assert window._dino_review_filter.eventFilter(window, enter)
    assert window._dino_review_filter.eventFilter(window, escape)
    assert not accepted
    assert not rejected


def test_dino_review_shortcuts_are_left_to_modal_dialog_while_sam3_is_busy(qtbot):
    window = ImageAnnotator()
    qtbot.addWidget(window)
    window.hide()
    window._sam3_inference_in_flight = True

    dialog = QDialog(window)
    qtbot.addWidget(dialog)
    dialog.setModal(True)
    dialog.show()
    qtbot.waitUntil(lambda: QApplication.activeModalWidget() is dialog)
    enter = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier,
    )

    assert not window._dino_review_filter.eventFilter(dialog, enter)
