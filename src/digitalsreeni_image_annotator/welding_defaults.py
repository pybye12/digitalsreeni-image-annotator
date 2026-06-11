from PyQt6.QtGui import QColor

WELDING_CLASSES = [
    ("internal_arc",       QColor(255, 255,   0)),   # yellow
    ("external_arc",       QColor(255, 128,   0)),   # orange
    ("droplet",            QColor(  0, 255, 255)),   # cyan
    ("molten_consumable",  QColor(255,   0, 255)),   # magenta
]
