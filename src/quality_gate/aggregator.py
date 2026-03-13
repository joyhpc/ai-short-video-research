"""Quality score aggregation and pass/fail decision logic.

Combines results from L1, L2, and (optionally) L3 into a single
verdict with confidence and actionable reasons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from .layer1_programmatic import CheckResult, LayerResult as L1Result
from .layer2_ml import CheckResult as L2CheckResult, LayerResult as L2Result
from .layer3_vlm import VLMResult


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Decision:
    """Final quality-gate decision."""

    verdict: str  # "pass" | "fail" | "review" | "escalate"
    confidence: float  # 0.0 – 1.0
    reasons: list[str] = field(default_factory=list)
    suggested_action: str = ""


# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

_DEFAULT_L2_WEIGHTS: dict[str, float] = {
    "visual_quality": 0.25,
    "text_alignment": 0.25,
    "temporal_consistency": 0.15,
    "motion_smoothness": 0.15,
    "scene_changes": 0.10,
    "color_consistency": 0.10,
}

_DEFAULT_PASS_THRESHOLD: float = 0.70
_DEFAULT_REVIEW_THRESHOLD: float = 0.50


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------

class QualityAggregator:
    """Aggregate per-layer results into a gate decision.

    Args:
        config_path: Optional path to a YAML file that overrides default
            weights and thresholds.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.l2_weights = dict(_DEFAULT_L2_WEIGHTS)
        self.pass_threshold = _DEFAULT_PASS_THRESHOLD
        self.review_threshold = _DEFAULT_REVIEW_THRESHOLD

        if config_path is not None:
            self._load_config(config_path)

    # -- config loading ------------------------------------------------------

    def _load_config(self, config_path: str | Path) -> None:
        """Load weights and thresholds from a YAML config file."""
        if yaml is None:
            raise ImportError(
                "PyYAML is required to load config files. "
                "Install it with: pip install pyyaml"
            )

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}

        l2_cfg = cfg.get("l2", {})
        if "weights" in l2_cfg:
            self.l2_weights.update(l2_cfg["weights"])
        if "pass_threshold" in l2_cfg:
            self.pass_threshold = float(l2_cfg["pass_threshold"])
        if "review_threshold" in l2_cfg:
            self.review_threshold = float(l2_cfg["review_threshold"])

    # -- scoring -------------------------------------------------------------

    def aggregate_l2_scores(
        self, results: list[L2CheckResult]
    ) -> float:
        """Compute a weighted average of L2 check scores.

        Checks that were skipped (score == 0.0 with status 'skipped') are
        excluded from the denominator so they do not drag the average down.

        Args:
            results: List of L2 CheckResult objects.

        Returns:
            Weighted average score in [0.0, 1.0].
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for r in results:
            if r.details.get("status") in ("skipped", "not_implemented"):
                continue
            w = self.l2_weights.get(r.name, 0.0)
            weighted_sum += r.score * w
            total_weight += w

        if total_weight == 0.0:
            return 0.0
        return round(weighted_sum / total_weight, 4)

    # -- decision logic ------------------------------------------------------

    def decide(
        self,
        l1_result: Optional[L1Result],
        l2_result: Optional[L2Result],
        l3_result: Optional[VLMResult] = None,
    ) -> Decision:
        """Produce a pass / fail / review / escalate verdict.

        Decision rules (evaluated in order):
        1. If L1 hard-gate fails -> FAIL immediately.
        2. If L2 weighted score >= pass_threshold and L3 label in
           (EXCELLENT, GOOD) -> PASS.
        3. If L2 weighted score >= review_threshold -> REVIEW (needs human
           or VLM re-check).
        4. If L2 weighted score < review_threshold -> FAIL.
        5. Edge cases (missing layers) -> ESCALATE.

        Args:
            l1_result: Layer 1 (programmatic) result, or None if not run.
            l2_result: Layer 2 (ML) result, or None if not run.
            l3_result: Layer 3 (VLM) result, or None if not run.

        Returns:
            A Decision with verdict, confidence, reasons, and
            suggested_action.
        """
        reasons: list[str] = []

        # -- L1 hard gate ----------------------------------------------------
        if l1_result is not None and not l1_result.passed:
            failed_checks = [c.name for c in l1_result.checks if not c.passed]
            reasons.append(
                f"L1 hard-gate failed on: {', '.join(failed_checks)}"
            )
            return Decision(
                verdict="fail",
                confidence=0.95,
                reasons=reasons,
                suggested_action="Fix technical issues before re-evaluation.",
            )

        # -- L2 scoring ------------------------------------------------------
        l2_score = 0.0
        if l2_result is not None:
            l2_score = self.aggregate_l2_scores(l2_result.checks)
            reasons.append(f"L2 weighted score: {l2_score:.2f}")
        else:
            reasons.append("L2 layer was not run.")

        # -- L3 label --------------------------------------------------------
        l3_label = l3_result.label if l3_result else None
        if l3_label:
            reasons.append(f"L3 VLM label: {l3_label}")

        # -- Decision matrix -------------------------------------------------
        if l2_score >= self.pass_threshold:
            if l3_label in (None, "EXCELLENT", "GOOD"):
                return Decision(
                    verdict="pass",
                    confidence=min(l2_score, 1.0),
                    reasons=reasons,
                    suggested_action="Video is ready for publication.",
                )
            else:
                reasons.append("L3 VLM flagged quality concerns.")
                return Decision(
                    verdict="review",
                    confidence=l2_score * 0.8,
                    reasons=reasons,
                    suggested_action="Review VLM critique and consider corrections.",
                )

        if l2_score >= self.review_threshold:
            return Decision(
                verdict="review",
                confidence=l2_score,
                reasons=reasons,
                suggested_action="Borderline quality — manual review recommended.",
            )

        if l2_result is not None:
            return Decision(
                verdict="fail",
                confidence=1.0 - l2_score,
                reasons=reasons,
                suggested_action="Re-generate with corrected prompt.",
            )

        # -- Escalate: not enough data to decide ----------------------------
        reasons.append("Insufficient layer data to make a decision.")
        return Decision(
            verdict="escalate",
            confidence=0.0,
            reasons=reasons,
            suggested_action="Run more quality layers before deciding.",
        )
