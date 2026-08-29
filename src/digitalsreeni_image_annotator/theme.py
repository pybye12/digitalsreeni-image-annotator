"""Design tokens and stylesheet loading for Annotation Studio."""

from pathlib import Path


COLORS = {
    "bg_canvas": "#101318",
    "bg_surface": "#171B22",
    "bg_elevated": "#202631",
    "bg_hover": "#293140",
    "border": "#303947",
    "border_strong": "#465266",
    "text": "#F4F7FB",
    "text_muted": "#9BA7B8",
    "text_subtle": "#6E7A8C",
    "accent": "#5B8CFF",
    "accent_hover": "#76A0FF",
    "accent_pressed": "#3F72E5",
    "success": "#42C792",
    "warning": "#F2B84B",
    "danger": "#F06A78",
    "shadow": "#090B0F",
    "transparent": "transparent",
}

SPACING = (4, 8, 12, 16, 24, 32)
RADII = (4, 6, 8, 12)
TOP_BAR_HEIGHT = 44
TOOL_RAIL_WIDTH = 56
CLASS_PANEL_WIDTH = 260
FILMSTRIP_HEIGHT = 104


def studio_stylesheet(font_size_pt=10):
    """Return the tokenized application stylesheet."""
    template = Path(__file__).with_name("app.qss").read_text(encoding="utf-8")
    values = {**COLORS, "font_size": int(font_size_pt)}
    return template.format_map(values)
