"""Small presentation-only widgets used by the canvas-first studio shell."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class DropZone(QWidget):
    browse_requested = pyqtSignal()
    import_requested = pyqtSignal()
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("emptyDropZone")
        self.setAcceptDrops(True)
        self.setMinimumSize(420, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(10)
        layout.addStretch(1)
        title = QLabel("Drop images or a video here")
        title.setObjectName("emptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel("Start with source frames, or reopen an existing labeled project.")
        hint.setObjectName("emptyHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions = QHBoxLayout()
        actions.addStretch(1)
        browse = QPushButton("Browse files")
        browse.setProperty("buttonRole", "primary")
        browse.clicked.connect(self.browse_requested)
        import_labels = QPushButton("Import labels")
        import_labels.clicked.connect(self.import_requested)
        actions.addWidget(browse)
        actions.addWidget(import_labels)
        actions.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(8)
        layout.addLayout(actions)
        layout.addStretch(1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        paths = [path for path in paths if path]
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()


class ShortcutOverlay(QWidget):
    """A compact, non-modal shortcut reference."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setObjectName("trackingDrawer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)
        title = QLabel("Keyboard shortcuts")
        title.setProperty("uiRole", "section")
        layout.addWidget(title)
        for keys, action in (
            ("A / D", "Previous / accept and next frame"),
            ("1-9", "Choose class"),
            ("P / B / E", "Polygon / brush / eraser"),
            ("C", "Copy selected mask to next frame"),
            ("Ctrl+Z / Ctrl+Shift+Z", "Undo / redo"),
            ("Space + drag", "Pan canvas"),
            ("[ / ]", "Decrease / increase overlay opacity"),
            ("?", "Show this guide"),
        ):
            row = QHBoxLayout()
            key_label = QLabel(keys)
            key_label.setMinimumWidth(120)
            action_label = QLabel(action)
            action_label.setProperty("uiRole", "muted")
            row.addWidget(key_label)
            row.addWidget(action_label)
            layout.addLayout(row)
