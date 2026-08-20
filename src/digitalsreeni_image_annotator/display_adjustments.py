"""Non-destructive display adjustments for annotation images."""

import numpy as np
from PyQt6.QtGui import QImage


def adjust_qimage(image, brightness=0, contrast=0):
    """Return a display-adjusted copy without modifying ``image``.

    Brightness and contrast use a user-facing range of -100 to 100. Contrast
    is exponential so equal slider movements feel balanced above and below
    the neutral value.
    """
    if not isinstance(image, QImage) or image.isNull():
        return QImage()
    if not -100 <= brightness <= 100:
        raise ValueError("brightness must be between -100 and 100")
    if not -100 <= contrast <= 100:
        raise ValueError("contrast must be between -100 and 100")

    rgba_image = image.convertToFormat(QImage.Format.Format_RGBA8888)
    if brightness == 0 and contrast == 0:
        return rgba_image.copy()

    buffer = rgba_image.constBits()
    buffer.setsize(rgba_image.sizeInBytes())
    pixels = np.frombuffer(
        buffer,
        dtype=np.uint8,
        count=rgba_image.sizeInBytes(),
    ).reshape(rgba_image.height(), rgba_image.bytesPerLine())
    pixels = pixels[:, : rgba_image.width() * 4].reshape(
        rgba_image.height(), rgba_image.width(), 4
    ).copy()

    rgb = pixels[:, :, :3].astype(np.float32)
    contrast_factor = 2.0 ** (contrast / 100.0)
    brightness_offset = brightness * 2.55
    rgb = (rgb - 127.5) * contrast_factor + 127.5 + brightness_offset
    pixels[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)

    adjusted = QImage(
        pixels.data,
        rgba_image.width(),
        rgba_image.height(),
        pixels.strides[0],
        QImage.Format.Format_RGBA8888,
    )
    return adjusted.copy()
