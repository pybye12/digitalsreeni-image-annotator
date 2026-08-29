"""Small session metrics used for progress and workflow benchmarking."""

from dataclasses import dataclass, field
from math import hypot
from time import monotonic


@dataclass
class FrameMetric:
    started_at: float
    actions: int = 0
    mouse_distance: float = 0.0
    committed_at: float | None = None

    @property
    def seconds(self):
        end = self.committed_at if self.committed_at is not None else monotonic()
        return max(0.0, end - self.started_at)


@dataclass
class WorkflowMetrics:
    frames: dict[str, FrameMetric] = field(default_factory=dict)
    current_frame: str | None = None
    _last_mouse: tuple[float, float] | None = None

    def enter_frame(self, frame_name, now=None):
        if not frame_name:
            return
        self.current_frame = str(frame_name)
        self.frames.setdefault(
            self.current_frame,
            FrameMetric(monotonic() if now is None else now),
        )
        self._last_mouse = None

    def action(self, count=1):
        metric = self.frames.get(self.current_frame)
        if metric:
            metric.actions += max(0, int(count))

    def mouse_move(self, x, y):
        metric = self.frames.get(self.current_frame)
        point = (float(x), float(y))
        if metric and self._last_mouse is not None:
            metric.mouse_distance += hypot(
                point[0] - self._last_mouse[0], point[1] - self._last_mouse[1]
            )
        self._last_mouse = point

    def commit(self, now=None):
        metric = self.frames.get(self.current_frame)
        if metric:
            metric.committed_at = monotonic() if now is None else now

    @property
    def completed(self):
        return [metric for metric in self.frames.values() if metric.committed_at is not None]

    @property
    def average_seconds(self):
        completed = self.completed
        return sum(item.seconds for item in completed) / len(completed) if completed else 0.0

    def eta_seconds(self, remaining_frames):
        return self.average_seconds * max(0, int(remaining_frames))

    def summary(self):
        completed = self.completed
        return {
            "frames": len(completed),
            "seconds_per_frame": self.average_seconds,
            "actions_per_frame": (
                sum(item.actions for item in completed) / len(completed)
                if completed
                else 0.0
            ),
            "mouse_distance_per_frame": (
                sum(item.mouse_distance for item in completed) / len(completed)
                if completed
                else 0.0
            ),
        }
