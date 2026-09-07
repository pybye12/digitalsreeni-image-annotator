from PyQt6.QtGui import QColor


ER70S6_CLASSES = [
    ("molten_consumable", QColor(255, 128, 0)),
    ("droplet", QColor(255, 0, 0)),
    ("external_arc", QColor(0, 0, 255)),
    ("internal_arc", QColor(255, 255, 0)),
    ("weld_pool", QColor(255, 0, 255)),
    ("spatter", QColor(0, 255, 255)),
]

ER70S6_CAVITAR_CLASSES = ER70S6_CLASSES[:2]

# Backward-compatible name used by older projects and integrations.
WELDING_CLASSES = ER70S6_CLASSES

ER70S6_PROTOCOL = """ER70S-6 multiclass protocol

Every pixel belongs to one class. Unlabeled pixels remain background (black).

Molten consumable (orange): from the solidus line through detachment while
the molten region is still attached to the wire.

Droplet (red): only after it detaches from the wire. It must not overlap the
molten consumable.

External arc (blue): the full silhouette of the largest arc, from its contact
with the wire to its contact with the workpiece.

Internal arc (yellow): the inner metal-vapor arc, whether or not it currently
touches the molten consumable.

Weld pool (magenta): the liquid weld pool on the workpiece.

Spatter (cyan): any expelled droplets and spatter separate from the main droplet.
"""
