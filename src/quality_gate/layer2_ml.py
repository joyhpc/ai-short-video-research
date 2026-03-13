"""Layer 2 — ML-based video quality checks.

Uses optional heavy dependencies (DOVER, OpenCLIP, VBench, PySceneDetect,
OpenCV) to compute perceptual and semantic quality metrics.  Every check
method gracefully degrades when its dependency is not installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# Re-use the same result data-classes for consistency with Layer 1.
# We duplicate the definitions here to keep each layer independently importable.


@dataclass
class CheckResult:
    """Result of a single quality check."""

    name: str
    passed: bool
    score: float  # 0.0 – 1.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerResult:
    """Aggregate result for the ML layer."""

    layer: str = "L2_ml"
    checks: list[CheckResult] = field(default_factory=list)
    passed: bool = False
    score: float = 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skip_result(name: str, dependency: str) -> CheckResult:
    """Return a 'skipped' CheckResult when an optional dependency is missing."""
    return CheckResult(
        name=name,
        passed=True,  # skipped checks do not block
        score=0.0,
        details={
            "status": "skipped",
            "reason": f"Optional dependency '{dependency}' is not installed. "
                      f"Install it to enable this check.",
        },
    )


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class MLChecker:
    """ML-powered quality checks — each method catches ImportError."""

    def check_visual_quality(self, video_path: str) -> CheckResult:
        """Compute visual quality scores via pyiqa NIQE (DOVER fallback).

        Prefers pyiqa with the NIQE metric as a lightweight alternative to
        DOVER (which requires a large model download + GPU).

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with per-frame NIQE scores and normalized average.
        """
        # Try pyiqa first (lightweight); skip if unavailable
        try:
            import pyiqa  # noqa: F811
        except ImportError:
            return _skip_result("visual_quality", "pyiqa or dover")

        try:
            import cv2
            import torch
            import numpy as np
        except ImportError:
            return _skip_result("visual_quality", "cv2/torch")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="visual_quality",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n_samples = min(8, max(1, total_frames))
        indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        niqe_metric = pyiqa.create_metric("niqe", device=device)

        niqe_scores: list[float] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue
            # Convert BGR -> RGB, HWC -> CHW, normalize to [0, 1]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            tensor = (
                torch.from_numpy(frame_rgb)
                .permute(2, 0, 1)
                .unsqueeze(0)
                .float()
                .div(255.0)
                .to(device)
            )
            niqe_val = niqe_metric(tensor).item()
            niqe_scores.append(niqe_val)
        cap.release()

        if not niqe_scores:
            return CheckResult(
                name="visual_quality",
                passed=False,
                score=0.0,
                details={"error": "No frames could be read from video."},
            )

        mean_niqe = float(np.mean(niqe_scores))
        # Normalize: NIQE lower is better, typical range 2-10
        score = max(0.0, 1.0 - (mean_niqe - 2.0) / 8.0)
        score = min(1.0, score)

        return CheckResult(
            name="visual_quality",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "metric": "niqe",
                "mean_niqe": round(mean_niqe, 4),
                "per_frame_niqe": [round(s, 4) for s in niqe_scores],
                "frames_sampled": len(niqe_scores),
            },
        )

    def check_text_alignment(
        self, video_path: str, prompt: str
    ) -> CheckResult:
        """Measure text-to-video alignment via OpenCLIP cosine similarity.

        Requires: ``pip install open_clip_torch``

        Samples 8 frames, encodes them alongside the prompt text using
        ViT-B-32, and reports mean cosine similarity.

        Args:
            video_path: Path to the video file.
            prompt: The original generation prompt.

        Returns:
            CheckResult with cosine_similarity in details.
        """
        try:
            import open_clip
            import torch
        except ImportError:
            return _skip_result("text_alignment", "open_clip_torch")

        try:
            import cv2
            import numpy as np
            from PIL import Image
        except ImportError:
            return _skip_result("text_alignment", "cv2/Pillow")

        if not prompt or not prompt.strip():
            return CheckResult(
                name="text_alignment",
                passed=True,
                score=0.0,
                details={"status": "skipped", "reason": "No prompt provided."},
            )

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="text_alignment",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n_samples = min(8, max(1, total_frames))
        indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, _, preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k"
        )
        model = model.to(device).eval()
        tokenizer = open_clip.get_tokenizer("ViT-B-32")

        # Encode text
        text_tokens = tokenizer([prompt]).to(device)
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        # Encode frames and compute per-frame cosine similarity
        similarities: list[float] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            img_tensor = preprocess(pil_img).unsqueeze(0).to(device)

            with torch.no_grad():
                img_features = model.encode_image(img_tensor)
                img_features = img_features / img_features.norm(dim=-1, keepdim=True)
                cos_sim = (img_features @ text_features.T).squeeze().item()

            similarities.append(cos_sim)
        cap.release()

        if not similarities:
            return CheckResult(
                name="text_alignment",
                passed=False,
                score=0.0,
                details={"error": "No frames could be read from video."},
            )

        mean_sim = float(np.mean(similarities))
        # Normalize: typical CLIP cosine similarity range 0.15-0.35
        score = min(1.0, max(0.0, (mean_sim - 0.15) / 0.20))

        return CheckResult(
            name="text_alignment",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "model": "ViT-B-32/laion2b_s34b_b79k",
                "mean_cosine_similarity": round(mean_sim, 4),
                "per_frame_similarity": [round(s, 4) for s in similarities],
                "frames_sampled": len(similarities),
                "prompt": prompt,
            },
        )

    def check_temporal_consistency(self, video_path: str) -> CheckResult:
        """Evaluate temporal consistency using frame-to-frame pixel difference.

        Lightweight fallback for VBench temporal consistency — compares
        consecutive sampled frames using mean absolute difference.
        High consistency (low difference) yields a high score.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with temporal consistency score.
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            return _skip_result("temporal_consistency", "opencv-python")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="temporal_consistency",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n_samples = min(16, max(2, total_frames))
        indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

        frames: list[np.ndarray] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue
            # Convert to grayscale and resize for speed
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (256, 256))
            frames.append(gray.astype(np.float32))
        cap.release()

        if len(frames) < 2:
            return CheckResult(
                name="temporal_consistency",
                passed=False,
                score=0.0,
                details={"error": "Not enough frames to compare."},
            )

        # Compute mean absolute difference between consecutive frames
        diffs: list[float] = []
        for i in range(len(frames) - 1):
            mad = float(np.mean(np.abs(frames[i + 1] - frames[i])))
            diffs.append(mad)

        mean_diff = float(np.mean(diffs))
        max_diff = float(np.max(diffs))

        # Normalize: low diff = high consistency; threshold at 50.0
        score = 1.0 - min(1.0, mean_diff / 50.0)
        score = max(0.0, score)

        return CheckResult(
            name="temporal_consistency",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "method": "frame_mad",
                "mean_abs_diff": round(mean_diff, 4),
                "max_abs_diff": round(max_diff, 4),
                "per_pair_diffs": [round(d, 4) for d in diffs],
                "frames_sampled": len(frames),
            },
        )

    def check_motion_smoothness(self, video_path: str) -> CheckResult:
        """Evaluate motion smoothness using optical flow variance.

        Uses Farneback optical flow between consecutive sampled frames.
        Smooth motion produces consistent flow magnitudes (low variance);
        erratic motion produces high variance.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with motion smoothness score.
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            return _skip_result("motion_smoothness", "opencv-python")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="motion_smoothness",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n_samples = min(16, max(2, total_frames))
        indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

        frames: list[np.ndarray] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (256, 256))
            frames.append(gray)
        cap.release()

        if len(frames) < 2:
            return CheckResult(
                name="motion_smoothness",
                passed=False,
                score=0.0,
                details={"error": "Not enough frames for optical flow."},
            )

        # Compute optical flow magnitudes between consecutive pairs
        flow_magnitudes: list[float] = []
        for i in range(len(frames) - 1):
            flow = cv2.calcOpticalFlowFarneback(
                frames[i],
                frames[i + 1],
                None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0,
            )
            magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
            flow_magnitudes.append(float(np.mean(magnitude)))

        mean_magnitude = float(np.mean(flow_magnitudes))
        flow_variance = float(np.var(flow_magnitudes))

        # Lower variance in flow magnitudes = smoother motion
        # Threshold: variance of 100 is very erratic
        score = 1.0 - min(1.0, flow_variance / 100.0)
        score = max(0.0, score)

        return CheckResult(
            name="motion_smoothness",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "method": "optical_flow_farneback",
                "mean_flow_magnitude": round(mean_magnitude, 4),
                "flow_magnitude_variance": round(flow_variance, 4),
                "per_pair_magnitudes": [round(m, 4) for m in flow_magnitudes],
                "frames_sampled": len(frames),
            },
        )

    def check_scene_changes(self, video_path: str) -> CheckResult:
        """Detect and score scene changes using PySceneDetect.

        Requires: ``pip install scenedetect[opencv]``

        For short-form video (< 60 s) we expect at most 5 intentional cuts.
        Excessive scene changes indicate generation artifacts.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with scene_count and timestamps in details.
        """
        try:
            from scenedetect import detect, ContentDetector
        except ImportError:
            return _skip_result("scene_changes", "scenedetect[opencv]")

        try:
            import cv2
        except ImportError:
            return _skip_result("scene_changes", "opencv-python")

        # Get video duration to determine expected scene count
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="scene_changes",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        cap.release()

        scene_list = detect(video_path, ContentDetector(threshold=27.0))
        scene_count = len(scene_list)

        # Determine expected scenes based on duration
        if duration <= 10:
            expected_scenes = 2
        elif duration <= 30:
            expected_scenes = 3
        elif duration <= 60:
            expected_scenes = 5
        else:
            expected_scenes = max(5, int(duration / 10))

        # Score: perfect if within expected, decay for each extra scene
        if scene_count <= expected_scenes:
            score = 1.0
        else:
            excess = scene_count - expected_scenes
            score = max(0.0, 1.0 - excess * 0.15)

        # Build timestamps list
        timestamps: list[dict[str, float]] = []
        for start, end in scene_list:
            timestamps.append({
                "start_s": round(start.get_seconds(), 2),
                "end_s": round(end.get_seconds(), 2),
            })

        return CheckResult(
            name="scene_changes",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "scene_count": scene_count,
                "expected_scenes": expected_scenes,
                "duration_s": round(duration, 2),
                "scenes": timestamps,
            },
        )

    def check_color_consistency(self, video_path: str) -> CheckResult:
        """Evaluate color consistency across frames via histogram comparison.

        Requires: ``pip install opencv-python``

        Computes HSV histograms (H and S channels) for sampled frames and
        measures Bhattacharyya distance between consecutive pairs.  Lower
        distance indicates more consistent colour grading.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with mean_bhattacharyya and max_bhattacharyya
            in details.
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            return _skip_result("color_consistency", "opencv-python")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return CheckResult(
                name="color_consistency",
                passed=False,
                score=0.0,
                details={"error": f"Cannot open video: {video_path}"},
            )

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n_samples = min(16, max(2, total_frames))
        indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

        histograms: list[np.ndarray] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Compute 2D histogram on H (180 bins) and S (256 bins) channels
            hist = cv2.calcHist(
                [hsv], [0, 1], None, [50, 60], [0, 180, 0, 256]
            )
            cv2.normalize(hist, hist)
            histograms.append(hist)
        cap.release()

        if len(histograms) < 2:
            return CheckResult(
                name="color_consistency",
                passed=False,
                score=0.0,
                details={"error": "Not enough frames to compare histograms."},
            )

        # Bhattacharyya distance between consecutive histogram pairs
        distances: list[float] = []
        for i in range(len(histograms) - 1):
            dist = cv2.compareHist(
                histograms[i], histograms[i + 1], cv2.HISTCMP_BHATTACHARYYA
            )
            distances.append(float(dist))

        mean_dist = float(np.mean(distances))
        max_dist = float(np.max(distances))

        # Bhattacharyya distance is in [0, 1]; lower = more consistent
        score = max(0.0, 1.0 - mean_dist)

        return CheckResult(
            name="color_consistency",
            passed=score >= 0.5,
            score=round(score, 4),
            details={
                "method": "hsv_histogram_bhattacharyya",
                "mean_bhattacharyya": round(mean_dist, 4),
                "max_bhattacharyya": round(max_dist, 4),
                "per_pair_distances": [round(d, 4) for d in distances],
                "frames_sampled": len(histograms),
            },
        )

    # -- aggregate -----------------------------------------------------------

    def run_all(
        self, video_path: str, prompt: str = "", **kwargs: Any
    ) -> LayerResult:
        """Run all ML checks and return an aggregate LayerResult.

        Skipped checks (missing dependencies) do not count as failures.
        """
        checks: list[CheckResult] = []

        for method, args in [
            (self.check_visual_quality, (video_path,)),
            (self.check_text_alignment, (video_path, prompt)),
            (self.check_temporal_consistency, (video_path,)),
            (self.check_motion_smoothness, (video_path,)),
            (self.check_scene_changes, (video_path,)),
            (self.check_color_consistency, (video_path,)),
        ]:
            try:
                checks.append(method(*args))
            except NotImplementedError:
                checks.append(CheckResult(
                    name=method.__name__.replace("check_", ""),
                    passed=True,
                    score=0.0,
                    details={"status": "not_implemented"},
                ))
            except Exception as exc:
                checks.append(CheckResult(
                    name=method.__name__.replace("check_", ""),
                    passed=False,
                    score=0.0,
                    details={"error": str(exc)},
                ))

        active = [c for c in checks if c.details.get("status") not in ("skipped", "not_implemented")]
        all_passed = all(c.passed for c in checks)
        avg_score = (
            sum(c.score for c in active) / len(active) if active else 0.0
        )

        return LayerResult(
            layer="L2_ml",
            checks=checks,
            passed=all_passed,
            score=round(avg_score, 4),
        )
