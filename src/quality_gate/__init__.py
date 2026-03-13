"""Quality gate evaluation — three-layer video quality assessment.

Exports:
    evaluate     -- Run quality evaluation on a video file.
    QualityResult -- Aggregate result across all quality layers.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .layer1_programmatic import LayerResult as L1Result
from .layer2_ml import LayerResult as L2Result
from .layer3_vlm import VLMResult
from .aggregator import Decision, QualityAggregator


@dataclass
class QualityResult:
    """Aggregate quality evaluation result across all layers."""

    video_path: str
    l1_result: Optional[L1Result] = None
    l2_result: Optional[L2Result] = None
    l3_result: Optional[VLMResult] = None
    decision: Optional[Decision] = None
    layers_run: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Whether the video passed overall quality evaluation."""
        if self.decision is None:
            return False
        return self.decision.verdict == "pass"


def evaluate(
    video_path: str | Path,
    prompt: str = "",
    config_path: str | Path | None = None,
    layers: list[int] | None = None,
) -> QualityResult:
    """Run quality evaluation on a video file.

    Args:
        video_path: Path to the video file to evaluate.
        prompt: The original generation prompt for text-alignment checks.
        config_path: Optional path to a YAML configuration file.
        layers: Which layers to run (1, 2, 3). Defaults to all.

    Returns:
        QualityResult with per-layer results and an aggregate decision.
    """
    from .layer1_programmatic import ProgrammaticChecker
    from .layer2_ml import MLChecker
    from .layer3_vlm import VLMReviewer

    video_path = str(video_path)
    layers = layers or [1, 2, 3]
    result = QualityResult(video_path=video_path)

    # --- Layer 1: Programmatic checks ---
    if 1 in layers:
        checker = ProgrammaticChecker()
        result.l1_result = checker.run_all(video_path)
        result.layers_run.append("L1_programmatic")

    # --- Layer 2: ML-based checks ---
    if 2 in layers:
        ml_checker = MLChecker()
        result.l2_result = ml_checker.run_all(video_path, prompt=prompt)
        result.layers_run.append("L2_ml")

    # --- Layer 3: VLM review ---
    if 3 in layers:
        reviewer = VLMReviewer()
        result.l3_result = reviewer.review(video_path, script=prompt)
        result.layers_run.append("L3_vlm")

    # --- Aggregate decision ---
    aggregator = QualityAggregator(config_path=config_path)
    result.decision = aggregator.decide(
        result.l1_result, result.l2_result, result.l3_result
    )

    return result


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for quality gate evaluation.

    Usage:
        python -m src.quality_gate video.mp4 --prompt "A cat walking" --layers 1 2
    """
    parser = argparse.ArgumentParser(
        prog="quality-gate",
        description="Evaluate video quality across programmatic, ML, and VLM layers.",
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to the video file to evaluate.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="",
        help="Original generation prompt for text-alignment scoring.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML configuration file.",
    )
    parser.add_argument(
        "--layers",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        choices=[1, 2, 3],
        help="Which quality layers to run (default: 1 2 3).",
    )

    args = parser.parse_args(argv)

    result = evaluate(
        video_path=args.video_path,
        prompt=args.prompt,
        config_path=args.config,
        layers=args.layers,
    )

    # Print summary
    print(f"Video:    {result.video_path}")
    print(f"Layers:   {', '.join(result.layers_run)}")
    if result.decision:
        print(f"Verdict:  {result.decision.verdict.upper()}")
        print(f"Confidence: {result.decision.confidence:.2f}")
        for reason in result.decision.reasons:
            print(f"  - {reason}")
    else:
        print("Verdict:  N/A (no decision computed)")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
