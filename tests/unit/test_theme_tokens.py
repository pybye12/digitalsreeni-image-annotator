import re
from pathlib import Path

from digitalsreeni_image_annotator.theme import COLORS, studio_stylesheet


def test_qss_source_uses_theme_tokens_instead_of_literal_hex_colors():
    qss_source = Path(__file__).parents[2] / "src" / "digitalsreeni_image_annotator" / "app.qss"
    template = qss_source.read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,8}", template)

    stylesheet = studio_stylesheet()
    assert COLORS["accent"] in stylesheet
    assert "QWidget#toolRail" in stylesheet
