import hashlib
import math
import os
import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import cv2


VIDEO_CACHE_MARKER = ".digitalsreeni-video-cache"
TRACKER_WORKSPACE_MARKER = ".digitalsreeni-tracker-workspace"


class VideoClipError(RuntimeError):
    """Raised when a video cannot be inspected or decoded."""


class VideoExtractionCancelled(VideoClipError):
    """Raised when the user cancels frame extraction."""


@dataclass(frozen=True)
class VideoMetadata:
    path: Path
    frame_count: int
    fps: float
    width: int
    height: int
    size_bytes: int | None = None
    mtime_ns: int | None = None

    @property
    def duration_seconds(self):
        if self.fps <= 0:
            return 0.0
        return self.frame_count / self.fps


@dataclass(frozen=True)
class VideoFrameSelection:
    start_frame: int
    end_frame: int
    stride: int = 1

    def validate(self, frame_count):
        if frame_count <= 0:
            raise ValueError("Video must contain at least one frame.")
        if self.start_frame < 0:
            raise ValueError("Start frame cannot be negative.")
        if self.end_frame < self.start_frame:
            raise ValueError("End frame must be at or after the start frame.")
        if self.end_frame >= frame_count:
            raise ValueError(
                f"End frame {self.end_frame} is outside the video "
                f"(last frame: {frame_count - 1})."
            )
        if self.stride < 1:
            raise ValueError("Frame stride must be at least 1.")

    def source_indices(self, frame_count):
        self.validate(frame_count)
        return range(self.start_frame, self.end_frame + 1, self.stride)

    def output_frame_count(self, frame_count):
        return len(self.source_indices(frame_count))


@dataclass(frozen=True)
class ExtractedFrame:
    source_index: int
    path: Path
    name: str
    timestamp_seconds: float | None


@dataclass(frozen=True)
class ExtractedVideoClip:
    metadata: VideoMetadata
    selection: VideoFrameSelection
    output_dir: Path
    frames: tuple[ExtractedFrame, ...]


def probe_video(video_path):
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")

    stat_before = path.stat()

    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise VideoClipError(f"OpenCV could not open the video: {path}")

        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if frame_count <= 0 or width <= 0 or height <= 0:
            raise VideoClipError(
                "The video opened, but its frame count or dimensions could not "
                "be determined. Try converting it to MP4 or AVI first."
            )

        stat_after = path.stat()
        if (
            stat_after.st_size != stat_before.st_size
            or stat_after.st_mtime_ns != stat_before.st_mtime_ns
        ):
            raise VideoClipError(
                "The video changed while it was being inspected. Select it again."
            )

        return VideoMetadata(
            path=path.resolve(),
            frame_count=frame_count,
            fps=fps if math.isfinite(fps) and fps > 0 else 0.0,
            width=width,
            height=height,
            size_bytes=stat_after.st_size,
            mtime_ns=stat_after.st_mtime_ns,
        )
    finally:
        capture.release()


def validate_video_source(metadata):
    """Reject a source replaced after it was probed for the range dialog."""
    if metadata.size_bytes is None or metadata.mtime_ns is None:
        return
    try:
        current = metadata.path.stat()
    except OSError as exc:
        raise VideoClipError(
            f"The selected video is no longer available: {metadata.path}"
        ) from exc
    if (
        current.st_size != metadata.size_bytes
        or current.st_mtime_ns != metadata.mtime_ns
    ):
        raise VideoClipError(
            "The selected video changed after it was inspected. Select it again."
        )


def video_clip_cache_directory(video_path, selection, cache_root):
    path = Path(video_path).resolve()
    stat = path.stat()
    fingerprint = "|".join(
        (
            str(path),
            str(stat.st_size),
            str(stat.st_mtime_ns),
            str(selection.start_frame),
            str(selection.end_frame),
            str(selection.stride),
        )
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12]
    stem = _safe_name(path.stem, max_length=48)
    return Path(cache_root) / f"{stem}_{digest}"


def extract_video_frames(
    metadata,
    selection,
    output_dir,
    progress_callback=None,
    cancel_check=None,
    image_format="png",
    jpeg_quality=95,
    png_compression=3,
):
    selection.validate(metadata.frame_count)
    validate_video_source(metadata)
    image_format = str(image_format).lower().lstrip(".")
    if image_format not in {"png", "jpg", "jpeg"}:
        raise ValueError("image_format must be 'png', 'jpg', or 'jpeg'")
    suffix = ".png" if image_format == "png" else ".jpg"
    write_options = (
        [cv2.IMWRITE_PNG_COMPRESSION, int(png_compression)]
        if image_format == "png"
        else [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
    )
    output_dir = Path(output_dir)
    _create_marked_directory(output_dir, VIDEO_CACHE_MARKER, exist_ok=True)

    capture = cv2.VideoCapture(str(metadata.path))
    if not capture.isOpened():
        capture.release()
        raise VideoClipError(f"OpenCV could not open the video: {metadata.path}")

    total = selection.output_frame_count(metadata.frame_count)
    extracted = []
    frame_index = selection.start_frame
    next_output_index = selection.start_frame

    try:
        if selection.start_frame:
            seek_ok = capture.set(cv2.CAP_PROP_POS_FRAMES, selection.start_frame)
            reported_position = int(round(capture.get(cv2.CAP_PROP_POS_FRAMES)))
            if not seek_ok or reported_position != selection.start_frame:
                capture.release()
                capture = cv2.VideoCapture(str(metadata.path))
                if not capture.isOpened():
                    raise VideoClipError(
                        f"OpenCV could not reopen the video: {metadata.path}"
                    )
                for skipped_index in range(selection.start_frame):
                    if cancel_check and cancel_check():
                        raise VideoExtractionCancelled(
                            "Video frame extraction was cancelled."
                        )
                    ok, _ = capture.read()
                    if not ok:
                        raise VideoClipError(
                            f"Video decoding stopped while seeking to frame "
                            f"{selection.start_frame} (stopped at {skipped_index})."
                        )

        while frame_index <= selection.end_frame:
            if cancel_check and cancel_check():
                raise VideoExtractionCancelled("Video frame extraction was cancelled.")

            ok, frame = capture.read()
            if not ok:
                raise VideoClipError(
                    f"Video decoding stopped at frame {frame_index}; expected to "
                    f"reach frame {selection.end_frame}."
                )

            if frame_index == next_output_index:
                clip_position = len(extracted)
                name = f"{output_dir.name}_frame_{clip_position:012d}{suffix}"
                destination = output_dir / name
                wrote_frame = cv2.imwrite(
                    str(destination),
                    frame,
                    write_options,
                )
                if not wrote_frame:
                    raise VideoClipError(f"Failed to write extracted frame: {destination}")

                timestamp = (
                    frame_index / metadata.fps if metadata.fps > 0 else None
                )
                extracted.append(
                    ExtractedFrame(
                        source_index=frame_index,
                        path=destination,
                        name=name,
                        timestamp_seconds=timestamp,
                    )
                )
                if progress_callback:
                    progress_callback(len(extracted), total)
                next_output_index += selection.stride

            frame_index += 1
    finally:
        capture.release()

    if len(extracted) != total:
        raise VideoClipError(
            f"Extracted {len(extracted)} frames, but {total} were requested."
        )
    validate_video_source(metadata)

    return ExtractedVideoClip(
        metadata=metadata,
        selection=selection,
        output_dir=output_dir,
        frames=tuple(extracted),
    )


def create_tracker_frame_workspace(frame_paths, cache_root):
    frame_paths = [Path(path) for path in frame_paths]
    if not frame_paths:
        raise ValueError("A tracking workspace requires at least one frame.")

    workspace = Path(cache_root) / uuid.uuid4().hex
    _create_marked_directory(workspace, TRACKER_WORKSPACE_MARKER)
    try:
        for position, source in enumerate(frame_paths):
            if not source.is_file():
                raise FileNotFoundError(f"Tracking frame not found: {source}")
            suffix = source.suffix.lower() or ".jpg"
            destination = workspace / f"{position:012d}{suffix}"
            try:
                os.link(source, destination)
            except OSError:
                shutil.copy2(source, destination)
    except Exception:
        cleanup_managed_video_directory(
            workspace,
            cache_root,
            TRACKER_WORKSPACE_MARKER,
        )
        raise
    return workspace


def copy_extracted_clip_to_directory(
    clip,
    destination_dir,
    progress_callback=None,
    cancel_check=None,
    progress_offset=0,
    progress_total=None,
):
    """Copy an extracted clip without overwriting existing project images."""
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    copied_paths = []
    copied_frames = []
    total = progress_total or len(clip.frames)

    try:
        for position, frame in enumerate(clip.frames, start=1):
            if cancel_check and cancel_check():
                raise VideoExtractionCancelled("Video import was cancelled.")

            destination = destination_dir / frame.name
            if destination.exists():
                raise VideoClipError(
                    f"Project image already exists and was not overwritten: {destination}"
                )
            # Track the destination before copying so a failed copy that leaves
            # a partial file is included in rollback.
            copied_paths.append(destination)
            shutil.copy2(frame.path, destination)
            if cancel_check and cancel_check():
                raise VideoExtractionCancelled("Video import was cancelled.")
            copied_frames.append(
                ExtractedFrame(
                    source_index=frame.source_index,
                    path=destination,
                    name=frame.name,
                    timestamp_seconds=frame.timestamp_seconds,
                )
            )
            if progress_callback:
                progress_callback(progress_offset + position, total)
    except Exception:
        for path in copied_paths:
            try:
                path.unlink()
            except OSError as cleanup_error:
                print(f"Could not remove partial video frame {path}: {cleanup_error}")
        raise

    return ExtractedVideoClip(
        metadata=clip.metadata,
        selection=clip.selection,
        output_dir=destination_dir,
        frames=tuple(copied_frames),
    )


def cleanup_managed_video_directory(
    directory,
    allowed_root,
    marker_name=VIDEO_CACHE_MARKER,
):
    """Delete a marked cache directory only when it is below an allowed root."""
    if not directory or not allowed_root:
        return False

    directory = Path(directory)
    allowed_root = Path(allowed_root).resolve()
    try:
        resolved_directory = directory.resolve()
        relative_path = resolved_directory.relative_to(allowed_root)
    except (OSError, ValueError):
        return False

    if not relative_path.parts or directory.is_symlink():
        return False

    marker = resolved_directory / marker_name
    if (
        resolved_directory.is_dir()
        and marker.is_file()
        and not marker.is_symlink()
    ):
        shutil.rmtree(resolved_directory)
        return True
    return False


def _create_marked_directory(directory, marker_name, exist_ok=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=exist_ok)
    try:
        (directory / marker_name).touch(exist_ok=exist_ok)
    except Exception:
        try:
            directory.rmdir()
        except OSError:
            pass
        raise


def _safe_name(value, max_length=80):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned[:max_length] or "video"
