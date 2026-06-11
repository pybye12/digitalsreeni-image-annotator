"""SAM 3 video tracking adapter.

This module wraps Meta's supported session-based video predictor API. Existing
annotation polygons are converted to one positive point per object so SAM 3's
instance-interactive tracker can preserve a stable object ID during propagation.
"""

from __future__ import annotations

import importlib
import importlib.util
import os

import cv2
import numpy as np


class SAM3Tracker:
    """Small adapter around Meta's SAM 3 video predictor."""

    def __init__(self, checkpoint_path, predictor=None):
        self.checkpoint_path = checkpoint_path
        self.predictor = predictor
        self.session_id = None
        if self.predictor is None:
            self._load_predictor()

    @property
    def is_initialized(self):
        return self.session_id is not None

    def _load_predictor(self):
        if not os.path.isfile(self.checkpoint_path):
            raise FileNotFoundError(f"SAM 3 checkpoint not found: {self.checkpoint_path}")

        try:
            import torch
            from sam3.model_builder import build_sam3_video_predictor
        except ImportError as exc:
            raise RuntimeError(
                "SAM 3 is not installed. Install Meta's official sam3 package "
                "and its supported CUDA/PyTorch dependencies."
            ) from exc

        if not torch.cuda.is_available():
            raise RuntimeError("SAM 3 video tracking requires a CUDA-capable GPU.")

        self._configure_connected_components_fallback()
        try:
            self.predictor = build_sam3_video_predictor(
                checkpoint_path=self.checkpoint_path,
                gpus_to_use=[torch.cuda.current_device()],
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load SAM 3 predictor from {self.checkpoint_path}: {exc}"
            ) from exc

    @staticmethod
    def _configure_connected_components_fallback():
        """Use Meta's CPU implementation when CUDA CC backends are unavailable.

        The official SAM 3 connected-components dispatcher tries ``cc_torch``
        and then Triton for CUDA tensors. Standard Windows environments often
        have neither. Meta also ships a correct CPU implementation, so route
        through it instead of failing at the first interactive point prompt.
        """
        if (
            importlib.util.find_spec("cc_torch") is not None
            or importlib.util.find_spec("triton") is not None
        ):
            return
        module = importlib.import_module("sam3.perflib.connected_components")
        module.connected_components = module.connected_components_cpu
        print(
            "[SAM3] cc_torch/Triton unavailable; using the slower CPU "
            "connected-components fallback."
        )

    def init_state(self, video_folder_path):
        """Start a predictor session for a directory of ordered video frames."""
        if not os.path.isdir(video_folder_path):
            raise ValueError(
                f"Path must be a directory containing frames: {video_folder_path}"
            )
        if self.predictor is None:
            raise RuntimeError("SAM 3 predictor is not loaded.")

        self.close_session()
        response = self.predictor.handle_request(
            {
                "type": "start_session",
                "resource_path": video_folder_path,
                "offload_video_to_cpu": True,
            }
        )
        self.session_id = response["session_id"]
        return self.session_id

    def track_points(self, frame_idx, object_points):
        """Add per-object point prompts and propagate them forward.

        Args:
            frame_idx: Frame index in the SAM 3 session.
            object_points: Iterable of ``(object_id, (x, y))`` entries in
                absolute image coordinates.

        Returns:
            List of ``(frame_idx, segmentations_by_object_id)`` results.
            Full-resolution masks are converted while streaming so long videos
            do not retain every GPU/CPU mask until propagation finishes.
        """
        if not self.is_initialized:
            raise RuntimeError("Call init_state before tracking.")

        self.predictor.handle_request(
            {"type": "reset_session", "session_id": self.session_id}
        )
        for object_id, point in object_points:
            self.predictor.handle_request(
                {
                    "type": "add_prompt",
                    "session_id": self.session_id,
                    "frame_index": frame_idx,
                    "obj_id": object_id,
                    "points": [list(point)],
                    "point_labels": [1],
                    "rel_coordinates": False,
                }
            )

        request = {
            "type": "propagate_in_video",
            "session_id": self.session_id,
            "propagation_direction": "forward",
            "start_frame_index": frame_idx,
        }
        results = []
        for response in self.predictor.handle_stream_request(request):
            segmentations_by_object = {
                object_id: self.mask_to_segmentations(mask)
                for object_id, mask in self.extract_masks_from_outputs(
                    response["outputs"]
                ).items()
            }
            results.append((response["frame_index"], segmentations_by_object))
        return results

    def close_session(self):
        if self.predictor is None or self.session_id is None:
            self.session_id = None
            return
        try:
            self.predictor.handle_request(
                {"type": "close_session", "session_id": self.session_id}
            )
        finally:
            self.session_id = None

    def unload(self):
        self.close_session()
        predictor = self.predictor
        if predictor is not None:
            for candidate in (
                getattr(predictor, "model", None),
                getattr(getattr(predictor, "predictor", None), "model", None),
            ):
                try:
                    if candidate is not None and hasattr(candidate, "cpu"):
                        candidate.cpu()
                except Exception as exc:
                    print(f"[SAM3] unload: warning moving model to CPU: {exc}")
            if hasattr(predictor, "shutdown"):
                predictor.shutdown()
        self.predictor = None
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        except Exception:
            pass

    @staticmethod
    def extract_masks_from_outputs(outputs):
        """Return ``{object_id: uint8_mask}`` from a predictor output."""
        if not isinstance(outputs, dict):
            return {}
        out_obj_ids = outputs.get("out_obj_ids")
        out_masks = outputs.get("out_binary_masks")
        if out_obj_ids is None or out_masks is None:
            return {}

        if hasattr(out_obj_ids, "detach"):
            out_obj_ids = out_obj_ids.detach().cpu().numpy()
        else:
            out_obj_ids = np.asarray(out_obj_ids)
        if hasattr(out_masks, "detach"):
            out_masks = out_masks.detach().cpu().numpy()
        else:
            out_masks = np.asarray(out_masks)

        masks = {}
        for object_id, mask in zip(out_obj_ids, out_masks):
            mask = np.asarray(mask)
            if mask.ndim == 3:
                mask = mask[0]
            masks[int(object_id)] = (mask > 0).astype(np.uint8)
        return masks

    @staticmethod
    def mask_to_segmentations(mask, min_area=10):
        """Convert a binary mask to flattened polygons used by the annotator."""
        contours, _ = cv2.findContours(
            (np.asarray(mask) > 0).astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        return [
            contour.flatten().tolist()
            for contour in contours
            if len(contour) >= 3 and cv2.contourArea(contour) > min_area
        ]
