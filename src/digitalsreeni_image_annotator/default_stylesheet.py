default_stylesheet = """
QWidget {
    background-color: #F0F0F0;
    color: #333333;
    font-family: Arial, sans-serif;
}

QMainWindow {
    background-color: #FFFFFF;
}

QPushButton {
    background-color: #E0E0E0;
    border: 1px solid #BBBBBB;
    padding: 5px 10px;
    border-radius: 3px;
    color: #333333;
}

QPushButton:hover {
    background-color: #D0D0D0;
}

QPushButton:pressed {
    background-color: #C0C0C0;
}

QPushButton:checked {
    background-color: #A0A0A0;
    border: 2px solid #808080;
    color: #FFFFFF;
}

QPushButton[buttonRole="primary"] {
    background-color: #2563EB;
    border: 1px solid #1D4ED8;
    color: #FFFFFF;
    font-weight: bold;
    padding: 7px 10px;
}

QPushButton[buttonRole="primary"]:hover {
    background-color: #3B82F6;
    border-color: #2563EB;
}

QPushButton[buttonRole="primary"]:pressed {
    background-color: #1D4ED8;
}

QLabel[cardRole="notice"] {
    background-color: #EAF2FF;
    border: 1px solid #9CC2F5;
    border-radius: 6px;
    padding: 10px;
    color: #17365D;
    font-weight: bold;
}

QLabel[cardRole="info"] {
    background-color: #F1F6FD;
    border-left: 3px solid #2563EB;
    border-radius: 4px;
    padding: 8px;
    color: #263746;
}


QListWidget, QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 3px;
}


QListWidget::item:selected {
    background-color: #E0E0E0;
    color: #333333;
}


QLabel {
    color: #333333;
}

QLabel.section-header {
    font-weight: bold;
    font-size: 14px;
    padding: 5px 0;
    color: #333333;  /* Dark color for visibility in light mode */
}

QLabel.help-text {
    color: #666666;
    font-size: 11px;
}

QLabel.workflow-hint {
    background-color: #E8EEF5;
    border: 1px solid #C2CFDC;
    border-radius: 4px;
    padding: 8px;
    color: #263746;
    font-weight: bold;
}

QGroupBox {
    border: 1px solid #C8C8C8;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 8px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 9px;
    padding: 0 4px;
    color: #333333;
}

QTabWidget::pane {
    border: 1px solid #C8C8C8;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #E4E4E4;
    border: 1px solid #C8C8C8;
    padding: 7px 14px;
    min-width: 90px;
}

QTabBar::tab:selected {
    background-color: #EAF2FF;
    color: #222222;
    border-bottom: 2px solid #2563EB;
}


QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    color: #333333;
    padding: 2px;
    border-radius: 3px;
}

QSlider::groove:horizontal {
    background: #CCCCCC;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #888888;
    width: 18px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #666666;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #F0F0F0;
    width: 12px;
    height: 12px;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #CCCCCC;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background-color: #BBBBBB;
}

QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
}

QMenuBar {
    background-color: #F0F0F0;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #E0E0E0;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
}

QMenu::item {
    padding: 5px 20px 5px 20px;
}

QMenu::item:selected {
    background-color: #E0E0E0;
}

QToolTip {
    background-color: #FFFFFF;
    color: #333333;
    border: 1px solid #CCCCCC;
}

QStatusBar {
    background-color: #F0F0F0;
    color: #666666;
}

QWidget#controlPanel,
QWidget#framesPanel {
    background-color: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-radius: 12px;
}

QWidget#productIdentity,
QWidget#canvasHeader,
QWidget#canvasFooter {
    background-color: transparent;
}

QWidget#canvasPanel {
    background-color: #F7F9FC;
    border: 1px solid #D8E1EC;
    border-radius: 12px;
}

QScrollArea#canvasViewport,
QScrollArea#canvasViewport > QWidget > QWidget {
    background-color: #E9EEF5;
    border: none;
}

QLabel.product-title {
    color: #142033;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel.product-subtitle,
QLabel.muted {
    color: #64748B;
}

QLabel.eyebrow {
    color: #607089;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel.canvas-file {
    color: #142033;
    font-weight: 600;
    padding-left: 8px;
}

QLabel.panel-count,
QLabel.shortcut-pill {
    color: #2856A8;
    background-color: #EAF1FF;
    border: 1px solid #C4D7FF;
    border-radius: 10px;
    padding: 4px 9px;
}

QLabel.dialog-title {
    color: #142033;
    font-size: 15px;
    font-weight: 700;
}

QGroupBox {
    background-color: #FAFCFF;
    border: 1px solid #D8E1EC;
    border-radius: 10px;
    margin-top: 13px;
    padding: 12px 10px 10px 10px;
}

QPushButton {
    min-height: 30px;
    border-radius: 8px;
    padding: 6px 11px;
}

QPushButton[buttonRole="tool"]:checked {
    background-color: #DDEAFF;
    border: 1px solid #4F7DFF;
    color: #173E7A;
    font-weight: 700;
}

QPushButton[buttonRole="accent"] {
    background-color: #0E8078;
    border: 1px solid #0C6F69;
    color: #FFFFFF;
    font-weight: 700;
}

QPushButton[buttonRole="accent"]:hover {
    background-color: #12958C;
}

QPushButton[buttonRole="quiet"] {
    background-color: transparent;
    border-color: #D3DDE9;
    color: #52647A;
}

QPushButton[buttonRole="danger"] {
    background-color: transparent;
    border-color: #E7B5BC;
    color: #B23D4D;
}

QPushButton[buttonRole="danger"]:hover {
    background-color: #FFF0F2;
    border-color: #D66C7A;
}

QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background-color: transparent;
    color: #6B7C91;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 16px;
    min-width: 105px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: transparent;
    color: #173E7A;
    border-bottom: 2px solid #4F7DFF;
}

QListWidget,
QTreeWidget {
    border-radius: 8px;
    border-color: #D3DDE9;
}

QListWidget::item {
    border-radius: 6px;
    padding: 6px 7px;
    margin: 1px 0;
}

QListWidget::item:selected {
    background-color: #DDEAFF;
    color: #173E7A;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    min-height: 28px;
    border-radius: 7px;
    padding: 4px 8px;
}

QListWidget::item {
    color: none;
}
"""
