import pytest
from PyQt6.QtGui import QColor, QImage, QPixmap

from digitalsreeni_image_annotator.display_adjustments import adjust_qimage
from digitalsreeni_image_annotator.image_label import ImageLabel


def _solid_image(red, green, blue):
    image = QImage(2, 2, QImage.Format.Format_RGBA8888)
    image.fill(QColor(red, green, blue, 255))
    return image


def test_neutral_adjustment_preserves_pixels():
    source = _solid_image(40, 80, 120)

    adjusted = adjust_qimage(source, 0, 0)

    assert adjusted.pixelColor(0, 0).getRgb() == (40, 80, 120, 255)


def test_brightness_and_contrast_adjust_preview_pixels():
    dark = _solid_image(64, 64, 64)
    light = _solid_image(192, 192, 192)

    brighter = adjust_qimage(dark, 25, 0)
    contrasted_dark = adjust_qimage(dark, 0, 50)
    contrasted_light = adjust_qimage(light, 0, 50)

    assert brighter.pixelColor(0, 0).red() > 64
    assert contrasted_dark.pixelColor(0, 0).red() < 64
    assert contrasted_light.pixelColor(0, 0).red() > 192


def test_image_label_keeps_raw_pixmap_for_inference(qt_application):
    label = ImageLabel()
    source = _solid_image(50, 100, 150)
    label.setPixmap(QPixmap.fromImage(source))

    label.set_display_adjustments(40, 30)

    assert label.original_pixmap.toImage().pixelColor(0, 0).getRgb() == (
        50,
        100,
        150,
        255,
    )
    assert label.display_pixmap.toImage().pixelColor(0, 0).getRgb() != (
        50,
        100,
        150,
        255,
    )


@pytest.mark.parametrize("brightness,contrast", [(-101, 0), (101, 0), (0, -101), (0, 101)])
def test_adjustment_ranges_are_validated(brightness, contrast):
    with pytest.raises(ValueError):
        adjust_qimage(_solid_image(0, 0, 0), brightness, contrast)
