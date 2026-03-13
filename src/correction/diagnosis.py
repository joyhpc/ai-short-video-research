"""Problem diagnosis — classify quality failures and suggest fix strategies.

Takes a QualityResult and distills it into a structured Diagnosis that
downstream correctors (prompt rewriter, parameter adjuster) can act on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

# We import at runtime to avoid circular deps during skeleton phase.
from src.quality_gate import QualityResult


# ---------------------------------------------------------------------------
# Enums & data classes
# ---------------------------------------------------------------------------

class ProblemType(Enum):
    """High-level classification of a video quality problem."""

    TECHNICAL = auto()    # encoding / format / sync issues (L1 failures)
    ALIGNMENT = auto()    # video does not match the prompt (L2 text_alignment)
    AESTHETIC = auto()    # poor visual / color quality (L2 visual_quality)
    COHERENCE = auto()    # temporal artifacts, flicker, scene jumps (L2 temporal)
    TIMING = auto()       # subtitle / audio timing problems (L1 subtitles, av_sync)


@dataclass
class Diagnosis:
    """Structured diagnosis of a video quality failure."""

    problem_type: ProblemType
    severity: str  # "critical" | "major" | "minor"
    description: str
    suggested_fix_strategy: str
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Diagnoser
# ---------------------------------------------------------------------------

class ProblemDiagnoser:
    """Analyze a QualityResult and produce a prioritized Diagnosis."""

    # Maps check names to problem types
    _CHECK_TYPE_MAP: dict[str, ProblemType] = {
        "file_integrity": ProblemType.TECHNICAL,
        "resolution_duration": ProblemType.TECHNICAL,
        "av_sync": ProblemType.TIMING,
        "audio_loudness": ProblemType.TECHNICAL,
        "subtitles": ProblemType.TIMING,
        "frame_consistency": ProblemType.COHERENCE,
        "visual_quality": ProblemType.AESTHETIC,
        "text_alignment": ProblemType.ALIGNMENT,
        "temporal_consistency": ProblemType.COHERENCE,
        "motion_smoothness": ProblemType.COHERENCE,
        "scene_changes": ProblemType.COHERENCE,
        "color_consistency": ProblemType.AESTHETIC,
    }

    _FIX_STRATEGIES: dict[ProblemType, str] = {
        ProblemType.TECHNICAL: "Re-encode or re-generate with corrected format settings.",
        ProblemType.ALIGNMENT: "Rewrite the generation prompt to improve text-video alignment.",
        ProblemType.AESTHETIC: "Adjust visual style parameters or use a different model checkpoint.",
        ProblemType.COHERENCE: "Increase temporal consistency CFG or reduce motion parameters.",
        ProblemType.TIMING: "Re-generate subtitles / re-align audio track.",
    }

    def diagnose(self, quality_result: QualityResult) -> Diagnosis:
        """Classify the dominant problem from a QualityResult.

        Examines failed checks across L1 and L2, picks the most severe
        failure, and returns a Diagnosis.

        Args:
            quality_result: The aggregate quality evaluation result.

        Returns:
            A Diagnosis describing the primary problem and recommended
            fix strategy.
        """
        failed_checks: list[tuple[str, float, ProblemType]] = []

        # Collect L1 failures
        if quality_result.l1_result:
            for check in quality_result.l1_result.checks:
                if not check.passed:
                    ptype = self._CHECK_TYPE_MAP.get(
                        check.name, ProblemType.TECHNICAL
                    )
                    failed_checks.append((check.name, check.score, ptype))

        # Collect L2 failures (score below threshold)
        if quality_result.l2_result:
            for check in quality_result.l2_result.checks:
                if not check.passed:
                    ptype = self._CHECK_TYPE_MAP.get(
                        check.name, ProblemType.AESTHETIC
                    )
                    failed_checks.append((check.name, check.score, ptype))

        if not failed_checks:
            return Diagnosis(
                problem_type=ProblemType.TECHNICAL,
                severity="minor",
                description="No clear failures detected; quality is borderline.",
                suggested_fix_strategy="Re-generate with a different random seed.",
            )

        # Prioritize: lowest-scoring failure first
        failed_checks.sort(key=lambda x: x[1])
        worst_name, worst_score, worst_type = failed_checks[0]

        severity = "critical" if worst_score < 0.3 else (
            "major" if worst_score < 0.6 else "minor"
        )

        return Diagnosis(
            problem_type=worst_type,
            severity=severity,
            description=(
                f"Primary failure: '{worst_name}' scored {worst_score:.2f}. "
                f"Problem category: {worst_type.name}."
            ),
            suggested_fix_strategy=self._FIX_STRATEGIES.get(
                worst_type, "Re-generate with adjusted parameters."
            ),
            details={
                "worst_check": worst_name,
                "worst_score": worst_score,
                "total_failures": len(failed_checks),
                "failure_types": list({fc[2].name for fc in failed_checks}),
            },
        )
