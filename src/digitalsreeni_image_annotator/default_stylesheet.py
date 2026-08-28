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

QListWidget::item {
    color: none;
}
"""
