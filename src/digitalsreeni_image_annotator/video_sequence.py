from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


@dataclass(frozen=True)
class FrameInfo:
    index: int
    path: Path
    name: str
    source_index: int | None = None


@dataclass
class FrameSequence:
    folder: Path
    frames: list[FrameInfo]
    _frames_by_name: dict[str, FrameInfo] = field(init=False, repr=False)

    def __post_init__(self):
        self._frames_by_name = {frame.name: frame for frame in self.frames}
        if len(self._frames_by_name) != len(self.frames):
            raise ValueError("Frame names must be unique within a sequence.")

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

        numeric_stems = all(path.stem.isdigit() for path in paths)

        return cls(
            folder=folder,
            frames=[
                FrameInfo(
                    index=i,
                    path=p,
                    name=p.name,
                    source_index=int(p.stem) if numeric_stems else i,
                )
                for i, p in enumerate(paths)
            ]
        )

    @classmethod
    def from_paths(
        cls,
        folder: str | Path,
        paths,
        source_indices=None,
    ) -> "FrameSequence":
        paths = [Path(path) for path in paths]
        if not paths:
            raise ValueError("A frame sequence requires at least one frame.")
        if source_indices is None:
            source_indices = list(range(len(paths)))
        else:
            source_indices = list(source_indices)
        if len(source_indices) != len(paths):
            raise ValueError("Frame paths and source indices must have equal lengths.")

        return cls(
            folder=Path(folder),
            frames=[
                FrameInfo(
                    index=index,
                    path=path,
                    name=path.name,
                    source_index=source_index,
                )
                for index, (path, source_index) in enumerate(
                    zip(paths, source_indices)
                )
            ],
        )

    def index_for_name(self, name: str) -> int | None:
        frame = self._frames_by_name.get(name)
        return frame.index if frame else None

    def name_for_index(self, index: int) -> str | None:
        if 0 <= index < len(self.frames):
            return self.frames[index].name
        return None

    def frame_for_name(self, name: str) -> FrameInfo | None:
        return self._frames_by_name.get(name)
