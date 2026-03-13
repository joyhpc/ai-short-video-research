"""Frame sampling utilities — extract frames from video files.

Provides uniform and scene-based frame sampling for downstream
quality checks and VLM review.
"""

from __future__ import annotations

from typing import Any, Literal

try:
    import numpy as np
    from numpy import ndarray
except ImportError:  # pragma: no cover
    ndarray = Any  # type: ignore[assignment,misc]
    np = None  # type: ignore[assignment]

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment,misc]


def sample_frames(
    video_path: str,
    n: int = 16,
    method: Literal["uniform", "scene"] = "uniform",
) -> list[ndarray]:
    """Sample *n* frames from a video file.

    Args:
        video_path: Path to the video file.
        n: Number of frames to extract.
        method: Sampling strategy.
            - ``"uniform"``: evenly-spaced frames across the full duration.
            - ``"scene"``: sample near detected scene boundaries (requires
              PySceneDetect).

    Returns:
        List of NumPy arrays (H x W x 3, BGR uint8) — one per sampled
        frame.

    Raises:
        FileNotFoundError: If the video file does not exist.
        ImportError: If OpenCV (cv2) is not installed.
    """
    try:
        import cv2
    except ImportError as exc:
        raise ImportError(
            "opencv-python is required for frame sampling. "
            "Install it with: pip install opencv-python"
        ) from exc

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        raise ValueError(f"Video has 0 frames: {video_path}")

    if method == "uniform":
        indices = _uniform_indices(total_frames, n)
    elif method == "scene":
        # TODO: implement scene-based sampling with PySceneDetect
        indices = _uniform_indices(total_frames, n)
    else:
        raise ValueError(f"Unknown sampling method: {method}")

    frames: list[ndarray] = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)

    cap.release()
    return frames


def _uniform_indices(total: int, n: int) -> list[int]:
    """Compute *n* uniformly-spaced frame indices within [0, total)."""
    if n >= total:
        return list(range(total))
    step = total / n
    return [int(step * i) for i in range(n)]


def frames_to_pil(frames: list[ndarray]) -> list[Any]:
    """Convert a list of BGR NumPy frames to PIL Image objects.

    Args:
        frames: List of NumPy arrays (H x W x 3, BGR).

    Returns:
        List of PIL.Image.Image objects (RGB).

    Raises:
        ImportError: If Pillow or OpenCV is not installed.
    """
    if Image is None:
        raise ImportError(
            "Pillow is required to convert frames to PIL Images. "
            "Install it with: pip install Pillow"
        )

    try:
        import cv2
    except ImportError as exc:
        raise ImportError(
            "opencv-python is required for color space conversion."
        ) from exc

    pil_frames = []
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frames.append(Image.fromarray(rgb))

    return pil_frames
