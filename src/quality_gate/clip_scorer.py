"""Clip scorer — score individual video clips for batch selection."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ClipScore:
    """Score for a single video clip candidate."""
    path: str
    score: float  # 0.0 – 1.0 composite
    details: dict  # per-check breakdown
    passed: bool


def score_clip(video_path: str, prompt: str = "") -> ClipScore:
    """Score a single clip using L1 + L2 checks.

    Returns a composite score (0.0-1.0) suitable for ranking candidates.
    Fast enough to score N candidates per scene.
    """
    from src.quality_gate.layer1_programmatic import ProgrammaticChecker
    from src.quality_gate.layer2_ml import MLChecker

    details = {}
    scores = []
    weights = []

    # L1: programmatic checks (fast, ~0.5s)
    try:
        l1 = ProgrammaticChecker()
        l1_result = l1.run_all(video_path)
        l1_passed = sum(1 for c in l1_result.checks if c.passed)
        l1_total = max(len(l1_result.checks), 1)
        l1_score = l1_passed / l1_total
        details["l1"] = {
            "score": l1_score,
            "passed": l1_passed,
            "total": l1_total,
        }
        scores.append(l1_score)
        weights.append(0.3)
    except Exception as e:
        logger.warning("L1 scoring failed for %s: %s", video_path, e)
        details["l1"] = {"score": 0.0, "error": str(e)}
        scores.append(0.0)
        weights.append(0.3)

    # L2: ML checks (slower, ~5s, gracefully skips missing deps)
    try:
        l2 = MLChecker()
        l2_result = l2.run_all(video_path, prompt=prompt)
        l2_scores = [c.score for c in l2_result.checks if c.score > 0]
        l2_score = sum(l2_scores) / max(len(l2_scores), 1) if l2_scores else 0.5
        details["l2"] = {
            "score": l2_score,
            "checks": {c.name: c.score for c in l2_result.checks},
        }
        scores.append(l2_score)
        weights.append(0.7)
    except Exception as e:
        logger.warning("L2 scoring failed for %s: %s", video_path, e)
        details["l2"] = {"score": 0.5, "error": str(e)}
        scores.append(0.5)
        weights.append(0.7)

    # Weighted composite
    total_weight = sum(weights)
    composite = sum(s * w for s, w in zip(scores, weights)) / total_weight

    return ClipScore(
        path=video_path,
        score=composite,
        details=details,
        passed=composite >= 0.5,
    )


def pick_best(candidates: list[str], prompt: str = "") -> tuple[str, ClipScore]:
    """Score multiple candidate clips and return the best one.

    Args:
        candidates: list of video file paths
        prompt: generation prompt (for text-alignment scoring)

    Returns:
        (best_path, best_score)
    """
    if len(candidates) == 1:
        sc = score_clip(candidates[0], prompt)
        return candidates[0], sc

    results = []
    for path in candidates:
        sc = score_clip(path, prompt)
        results.append(sc)
        logger.info("  Candidate %s: %.3f", Path(path).name, sc.score)

    best = max(results, key=lambda s: s.score)
    return best.path, best
