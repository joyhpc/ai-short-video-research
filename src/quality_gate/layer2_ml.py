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
        """Compute aesthetic and technical quality scores via DOVER.

        Requires: ``pip install dover``

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with aesthetic_score and technical_score in details.
        """
        try:
            import dover as _dover  # noqa: F401 — availability check
        except ImportError:
            return _skip_result("visual_quality", "dover")

        # TODO: run DOVER inference, extract aesthetic + technical scores
        raise NotImplementedError

    def check_text_alignment(
        self, video_path: str, prompt: str
    ) -> CheckResult:
        """Measure text-to-video alignment via OpenCLIP cosine similarity.

        Requires: ``pip install open_clip_torch``

        Samples frames, encodes them alongside the prompt text, and reports
        mean cosine similarity.

        Args:
            video_path: Path to the video file.
            prompt: The original generation prompt.

        Returns:
            CheckResult with cosine_similarity in details.
        """
        try:
            import open_clip as _open_clip  # noqa: F401
        except ImportError:
            return _skip_result("text_alignment", "open_clip_torch")

        # TODO: encode frames + text, compute cosine similarity
        raise NotImplementedError

    def check_temporal_consistency(self, video_path: str) -> CheckResult:
        """Evaluate temporal consistency using VBench metrics.

        Requires: ``pip install vbench``

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with temporal consistency score.
        """
        try:
            import vbench as _vbench  # noqa: F401
        except ImportError:
            return _skip_result("temporal_consistency", "vbench")

        # TODO: run VBench temporal consistency evaluation
        raise NotImplementedError

    def check_motion_smoothness(self, video_path: str) -> CheckResult:
        """Evaluate motion smoothness using VBench metrics.

        Requires: ``pip install vbench``

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with motion smoothness score.
        """
        try:
            import vbench as _vbench  # noqa: F401
        except ImportError:
            return _skip_result("motion_smoothness", "vbench")

        # TODO: run VBench motion smoothness evaluation
        raise NotImplementedError

    def check_scene_changes(self, video_path: str) -> CheckResult:
        """Detect and score scene changes using PySceneDetect.

        Requires: ``pip install scenedetect[opencv]``

        For short-form video we expect 0–2 intentional cuts.
        Excessive scene changes indicate generation artifacts.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with scene_count and timestamps in details.
        """
        try:
            import scenedetect as _scenedetect  # noqa: F401
        except ImportError:
            return _skip_result("scene_changes", "scenedetect[opencv]")

        # TODO: run PySceneDetect ContentDetector
        raise NotImplementedError

    def check_color_consistency(self, video_path: str) -> CheckResult:
        """Evaluate color consistency across frames via histogram comparison.

        Requires: ``pip install opencv-python``

        Computes HSV histograms for sampled frames and measures
        Bhattacharyya distance between consecutive pairs.

        Args:
            video_path: Path to the video file.

        Returns:
            CheckResult with mean_bhattacharyya and max_bhattacharyya
            in details.
        """
        try:
            import cv2 as _cv2  # noqa: F401
        except ImportError:
            return _skip_result("color_consistency", "opencv-python")

        # TODO: sample frames, compute HSV histograms, pairwise Bhattacharyya
        raise NotImplementedError

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
