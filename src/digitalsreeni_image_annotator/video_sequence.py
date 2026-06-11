from dataclasses import dataclass
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

@dataclass(frozen=True)
class FrameInfo:
    index: int
    path: Path
    name: str

@dataclass
class FrameSequence:
    folder: Path
    frames: list[FrameInfo]

    @classmethod
    def from_folder(cls, folder: str | Path) -> "FrameSequence":
        folder = Path(folder)
        if not folder.exists():
            raise FileNotFoundError(f"Directory not found: {folder}")

        paths = [
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ]
        
        # Match Meta SAM 3's image-folder loader exactly: numeric stems are
        # sorted numerically; any other naming scheme falls back to lexical.
        try:
            paths.sort(key=lambda path: int(path.stem))
        except ValueError:
            paths.sort(key=lambda path: path.name)
        if not paths:
            raise ValueError(f"No supported image frames found in: {folder}")

        return cls(
            folder=folder,
            frames=[FrameInfo(index=i, path=p, name=p.name) for i, p in enumerate(paths)]
        )

    def index_for_name(self, name: str) -> int | None:
        for frame in self.frames:
            if frame.name == name:
                return frame.index
        return None

    def name_for_index(self, index: int) -> str | None:
        if 0 <= index < len(self.frames):
            return self.frames[index].name
        return None
