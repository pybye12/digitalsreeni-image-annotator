soft_dark_stylesheet = """
QWidget {
    background-color: #0D1520;
    color: #E8EEF7;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
}

QMainWindow {
    background-color: #08111C;
}

QWidget#controlPanel,
QWidget#framesPanel {
    background-color: #111C2A;
    border: 1px solid #223247;
    border-radius: 12px;
}

QWidget#productIdentity,
QWidget#canvasHeader,
QWidget#canvasFooter {
    background-color: transparent;
}

QWidget#canvasPanel {
    background-color: #0A121D;
    border: 1px solid #223247;
    border-radius: 12px;
}

QScrollArea#canvasViewport {
    background-color: #060B12;
    border: none;
    border-radius: 8px;
}

QScrollArea#canvasViewport > QWidget > QWidget {
    background-color: #060B12;
}

QLabel {
    color: #E8EEF7;
    background-color: transparent;
}

QLabel.product-title {
    color: #F7FAFF;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel.product-subtitle,
QLabel.muted {
    color: #8292A8;
}

QLabel.eyebrow {
    color: #8FA3BD;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel.canvas-file {
    color: #F7FAFF;
    font-weight: 600;
    padding-left: 8px;
}

QLabel.panel-count {
    color: #78A7FF;
    background-color: #172A46;
    border: 1px solid #28466D;
    border-radius: 10px;
    padding: 3px 8px;
    font-weight: 600;
}

QLabel.shortcut-pill {
    color: #AEBBD0;
    background-color: #172231;
    border: 1px solid #2A3A50;
    border-radius: 10px;
    padding: 4px 9px;
    font-size: 10px;
}

QLabel.section-header,
QLabel.dialog-title {
    color: #F7FAFF;
    font-size: 15px;
    font-weight: 700;
    padding: 4px 0;
}

QLabel.help-text {
    color: #91A0B5;
    font-size: 10px;
    line-height: 1.35;
}

QLabel.workflow-hint {
    background-color: #14243A;
    border: 1px solid #29476D;
    border-radius: 10px;
    padding: 12px;
    color: #DDEBFF;
    font-weight: 600;
}

QLabel[cardRole="notice"] {
    background-color: #14243A;
    border: 1px solid #315986;
    border-radius: 10px;
    padding: 12px;
    color: #E5F0FF;
    font-weight: 700;
}

QLabel[cardRole="info"] {
    background-color: #142131;
    border-left: 3px solid #5B8CFF;
    border-radius: 8px;
    padding: 10px;
    color: #C9DAF3;
}

QGroupBox {
    background-color: #131F2E;
    color: #F1F5FB;
    border: 1px solid #26384E;
    border-radius: 10px;
    margin-top: 13px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #DCE6F3;
}

QPushButton {
    min-height: 30px;
    background-color: #1A293A;
    color: #DCE6F3;
    border: 1px solid #30435A;
    border-radius: 8px;
    padding: 6px 11px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #22354A;
    border-color: #48617D;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #142131;
}

QPushButton:disabled {
    background-color: #131D29;
    border-color: #202E40;
    color: #59687B;
}

QPushButton:checked,
QPushButton[buttonRole="tool"]:checked {
    background-color: #183A61;
    border: 1px solid #62A8FF;
    color: #FFFFFF;
    font-weight: 700;
}

QPushButton[buttonRole="primary"] {
    background-color: #4F7DFF;
    border: 1px solid #6A92FF;
    color: #FFFFFF;
    font-weight: 700;
}

QPushButton[buttonRole="primary"]:hover {
    background-color: #638CFF;
    border-color: #8EAAFF;
}

QPushButton[buttonRole="primary"]:pressed {
    background-color: #3E68DF;
}

QPushButton[buttonRole="accent"] {
    background-color: #0E706C;
    border: 1px solid #21A39A;
    color: #F2FFFD;
    font-weight: 700;
}

QPushButton[buttonRole="accent"]:hover {
    background-color: #12827D;
    border-color: #45C0B6;
}

QPushButton[buttonRole="quiet"] {
    background-color: transparent;
    border-color: #2A3A50;
    color: #AEBBD0;
}

QPushButton[buttonRole="danger"] {
    background-color: transparent;
    border-color: #5B3038;
    color: #F19AA6;
}

QPushButton[buttonRole="danger"]:hover {
    background-color: #3A1F27;
    border-color: #A94C5C;
    color: #FFD5DA;
}

QTabWidget::pane {
    background-color: transparent;
    border: none;
    top: -1px;
}

QTabBar::tab {
    min-width: 105px;
    background-color: transparent;
    color: #7F90A8;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 16px;
    font-weight: 600;
}

QTabBar::tab:hover {
    color: #C7D4E6;
}

QTabBar::tab:selected {
    color: #FFFFFF;
    border-bottom: 2px solid #5B8CFF;
}

QListWidget,
QTreeWidget,
QTableWidget {
    background-color: #0D1723;
    color: #DCE6F3;
    border: 1px solid #26384E;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item,
QTreeWidget::item {
    color: #DCE6F3;
    border-radius: 6px;
    padding: 6px 7px;
    margin: 1px 0;
}

QListWidget::item:hover,
QTreeWidget::item:hover {
    background-color: #18283A;
}

QListWidget::item:selected,
QTreeWidget::item:selected,
QTableWidget::item:selected {
    background-color: #234A78;
    color: #FFFFFF;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    min-height: 28px;
    background-color: #0E1926;
    border: 1px solid #2A3D54;
    color: #E4EBF5;
    padding: 4px 8px;
    border-radius: 7px;
    selection-background-color: #315F9A;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-color: #5B8CFF;
}

QComboBox:hover {
    border-color: #48617D;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background-color: #111C2A;
    color: #E4EBF5;
    border: 1px solid #30435A;
    selection-background-color: #234A78;
    selection-color: #FFFFFF;
    outline: none;
}

QHeaderView::section {
    background-color: #172536;
    color: #C7D4E6;
    border: none;
    border-right: 1px solid #2A3D54;
    border-bottom: 1px solid #2A3D54;
    padding: 7px;
    font-weight: 600;
}

QSlider::groove:horizontal {
    height: 5px;
    background: #243449;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #5B8CFF;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #F0F5FF;
    border: 2px solid #5B8CFF;
    width: 15px;
    height: 15px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #FFFFFF;
    border-color: #84A7FF;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #33465E;
    border-radius: 5px;
    min-height: 26px;
    min-width: 26px;
}

QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background: #48617D;
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    background: transparent;
    border: none;
}

QMenuBar {
    background-color: #0B1420;
    color: #C7D4E6;
    border-bottom: 1px solid #1F2E41;
}

QMenuBar::item {
    padding: 7px 10px;
    background-color: transparent;
    border-radius: 5px;
}

QMenuBar::item:selected {
    background-color: #18283A;
    color: #FFFFFF;
}

QMenu {
    background-color: #111C2A;
    border: 1px solid #2A3D54;
    border-radius: 8px;
    padding: 5px;
}

QMenu::item {
    padding: 7px 24px 7px 12px;
    border-radius: 5px;
}

QMenu::item:selected {
    background-color: #234A78;
    color: #FFFFFF;
}

QToolTip {
    background-color: #182536;
    color: #F1F5FB;
    border: 1px solid #3A506B;
    border-radius: 6px;
    padding: 6px;
}

QStatusBar {
    background-color: #0B1420;
    color: #8292A8;
    border-top: 1px solid #1F2E41;
}

QProgressBar {
    background-color: #111C2A;
    border: 1px solid #2A3D54;
    border-radius: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #4F7DFF;
    border-radius: 5px;
}

QCheckBox,
QRadioButton {
    color: #DCE6F3;
    spacing: 7px;
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 15px;
    height: 15px;
    background-color: #0E1926;
    border: 1px solid #48617D;
}

QCheckBox::indicator {
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: #5B8CFF;
    border: 2px solid #B6CBFF;
}

QDialog {
    background-color: #0D1622;
}
"""
