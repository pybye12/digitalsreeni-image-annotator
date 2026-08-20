from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from .video_clip import (
    VideoExtractionCancelled,
    VideoFrameSelection,
    cleanup_managed_video_directory,
    copy_extracted_clip_to_directory,
    extract_video_frames,
)


class VideoClipDialog(QDialog):
    def __init__(self, metadata, parent=None):
        super().__init__(parent)
        self.metadata = metadata
        self.setWindowTitle("Open Video Clip")

        layout = QVBoxLayout(self)
        details = QLabel(
            f"{metadata.width} x {metadata.height} | "
            f"{metadata.frame_count:,} frames | "
            f"{metadata.fps:.3f} fps | "
            f"{metadata.duration_seconds:.2f} seconds"
        )
        details.setWordWrap(True)
        layout.addWidget(details)

        form = QFormLayout()
        last_frame = metadata.frame_count - 1

        self.start_frame = QSpinBox()
        self.start_frame.setRange(0, last_frame)
        self.start_frame.setValue(0)
        form.addRow("Start frame (inclusive):", self.start_frame)

        self.end_frame = QSpinBox()
        self.end_frame.setRange(0, last_frame)
        self.end_frame.setValue(min(last_frame, 499))
        form.addRow("End frame (inclusive):", self.end_frame)

        self.stride = QSpinBox()
        self.stride.setRange(1, max(metadata.frame_count, 1))
        self.stride.setValue(1)
        form.addRow("Keep every Nth frame:", self.stride)

        layout.addLayout(form)

        self.selection_summary = QLabel()
        layout.addWidget(self.selection_summary)
        self.start_frame.valueChanged.connect(self._selection_changed)
        self.end_frame.valueChanged.connect(self._selection_changed)
        self.stride.valueChanged.connect(self._selection_changed)
        self._selection_changed()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selection(self):
        return VideoFrameSelection(
            start_frame=self.start_frame.value(),
            end_frame=self.end_frame.value(),
            stride=self.stride.value(),
        )

    def accept(self):
        selection = self.selection()
        try:
            selection.validate(self.metadata.frame_count)
        except ValueError:
            self.end_frame.setValue(max(self.end_frame.value(), self.start_frame.value()))
            return
        super().accept()

    def _selection_changed(self):
        selection = self.selection()
        if selection.end_frame < selection.start_frame:
            self.selection_summary.setText("End frame must be at or after start frame.")
            return
        count = selection.output_frame_count(self.metadata.frame_count)
        self.selection_summary.setText(
            f"This clip will contain {count:,} frame{'s' if count != 1 else ''}."
        )


class VideoExtractionThread(QThread):
    progress_changed = pyqtSignal(int, int)

    def __init__(
        self,
        metadata,
        selection,
        output_dir,
        project_images_dir=None,
        cache_root=None,
        parent=None,
    ):
        super().__init__(parent)
        self.metadata = metadata
        self.selection = selection
        self.output_dir = output_dir
        self.project_images_dir = project_images_dir
        self.cache_root = cache_root
        self.result = None
        self.error = None
        self.cancelled = False

    def run(self):
        selected_frame_count = self.selection.output_frame_count(
            self.metadata.frame_count
        )
        progress_total = (
            selected_frame_count * 2
            if self.project_images_dir is not None
            else selected_frame_count
        )

        def extraction_progress(completed, _total):
            self.progress_changed.emit(completed, progress_total)

        try:
            extracted_clip = extract_video_frames(
                self.metadata,
                self.selection,
                self.output_dir,
                progress_callback=extraction_progress,
                cancel_check=self.isInterruptionRequested,
            )
            if self.project_images_dir is None:
                self.result = extracted_clip
            else:
                self.result = copy_extracted_clip_to_directory(
                    extracted_clip,
                    self.project_images_dir,
                    progress_callback=self.progress_changed.emit,
                    cancel_check=self.isInterruptionRequested,
                    progress_offset=selected_frame_count,
                    progress_total=progress_total,
                )
        except VideoExtractionCancelled:
            self.cancelled = True
        except Exception as exc:
            self.error = exc
        finally:
            if self.cache_root is not None:
                cleanup_managed_video_directory(
                    self.output_dir,
                    self.cache_root,
                )
