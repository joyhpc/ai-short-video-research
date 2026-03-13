"""Pipeline orchestrator — generate -> evaluate -> correct loop.

Supports two modes:
- Evaluate-only: assess an existing video file
- Full pipeline: generate -> evaluate -> correct -> retry
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional

from src.quality_gate import QualityResult, evaluate as qa_evaluate
from src.quality_gate.aggregator import Decision
from src.correction.diagnosis import Diagnosis, ProblemDiagnoser
from src.correction.prompt_rewriter import PromptRewriter, RewriteResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VideoState:
    """Mutable state carried through the orchestration loop."""

    video_path: str = ""
    prompt: str = ""
    retry_count: int = 0
    max_retries: int = 3
    quality_result: Optional[QualityResult] = None
    diagnosis: Optional[Diagnosis] = None
    quality_scores: dict[str, float] = field(default_factory=dict)
    critique: str = ""
    corrected_prompt: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)
    _generator: Optional[Callable] = field(default=None, repr=False)


@dataclass
class OrchestratorResult:
    """Final result returned by the orchestrator."""

    video_path: str
    prompt: str
    quality_result: Optional[QualityResult] = None
    diagnosis: Optional[Diagnosis] = None
    decision: Optional[Decision] = None
    retries_used: int = 0
    success: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_report(self) -> dict[str, Any]:
        """Generate a JSON-serializable quality report."""
        report: dict[str, Any] = {
            "video_path": self.video_path,
            "prompt": self.prompt,
            "success": self.success,
            "retries_used": self.retries_used,
        }

        if self.decision:
            report["decision"] = {
                "verdict": self.decision.verdict,
                "confidence": self.decision.confidence,
                "reasons": self.decision.reasons,
                "suggested_action": self.decision.suggested_action,
            }

        if self.quality_result:
            qr = self.quality_result
            report["layers_run"] = qr.layers_run

            if qr.l1_result:
                report["l1"] = {
                    "passed": qr.l1_result.passed,
                    "score": qr.l1_result.score,
                    "checks": [
                        {"name": c.name, "passed": c.passed, "score": c.score, "details": c.details}
                        for c in qr.l1_result.checks
                    ],
                }
            if qr.l2_result:
                report["l2"] = {
                    "passed": qr.l2_result.passed,
                    "score": qr.l2_result.score,
                    "checks": [
                        {"name": c.name, "passed": c.passed, "score": c.score, "details": c.details}
                        for c in qr.l2_result.checks
                    ],
                }
            if qr.l3_result:
                report["l3"] = {
                    "label": qr.l3_result.label,
                    "reasoning": qr.l3_result.reasoning,
                    "scores": qr.l3_result.scores,
                    "critique": qr.l3_result.critique,
                }

        if self.diagnosis:
            report["diagnosis"] = {
                "problem_type": self.diagnosis.problem_type.name,
                "severity": self.diagnosis.severity,
                "description": self.diagnosis.description,
                "suggested_fix_strategy": self.diagnosis.suggested_fix_strategy,
                "details": self.diagnosis.details,
            }

        if self.history:
            report["retry_history"] = self.history

        return report


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class VideoOrchestrator:
    """Main orchestrator: generate -> evaluate -> correct loop.

    Supports:
    - evaluate_video(): assess an existing video (no generation)
    - run(): full generate -> evaluate -> correct -> retry pipeline
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        quality_layers: list[int] | None = None,
    ) -> None:
        self.config_path = str(config_path) if config_path else None
        self.quality_layers = quality_layers or [1, 2]
        self.diagnoser = ProblemDiagnoser()
        self.rewriter = PromptRewriter()

    # -- public API: evaluate-only -------------------------------------------

    @classmethod
    def evaluate_video(
        cls,
        video_path: str | Path,
        prompt: str = "",
        config_path: str | Path | None = None,
        layers: list[int] | None = None,
    ) -> OrchestratorResult:
        """Evaluate an existing video without generation.

        This is the primary entry point for quality assessment of
        pre-existing video files.

        Args:
            video_path: Path to the video file.
            prompt: Original generation prompt (for text-alignment checks).
            config_path: Optional YAML config path.
            layers: Quality layers to run (default [1, 2]).

        Returns:
            OrchestratorResult with quality assessment and diagnosis.
        """
        orch = cls(config_path=config_path, quality_layers=layers or [1, 2])
        state = VideoState(
            video_path=str(video_path),
            prompt=prompt,
            max_retries=0,  # no retries in evaluate-only mode
        )

        # Evaluate
        quality_result = qa_evaluate(
            state.video_path,
            prompt=state.prompt,
            config_path=orch.config_path,
            layers=orch.quality_layers,
        )
        state.quality_result = quality_result

        # Diagnose if not passing
        diagnosis = None
        if not quality_result.passed:
            diagnosis = orch.diagnoser.diagnose(quality_result)

        return OrchestratorResult(
            video_path=state.video_path,
            prompt=state.prompt,
            quality_result=quality_result,
            diagnosis=diagnosis,
            decision=quality_result.decision,
            retries_used=0,
            success=quality_result.passed,
        )

    # -- public API: full pipeline -------------------------------------------

    def run(
        self,
        prompt: str,
        generator: Callable[[str, dict], str] | None = None,
        video_path: str | None = None,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> OrchestratorResult:
        """Execute the full generate -> evaluate -> correct loop.

        Either provide a `generator` callable or a `video_path` for
        evaluate-only mode.

        Args:
            prompt: The video generation prompt.
            generator: A callable(prompt, params) -> video_path.
                If None, video_path must be provided (evaluate-only).
            video_path: Pre-existing video to evaluate (no generation).
            max_retries: Maximum correction+retry cycles.
            **kwargs: Forwarded to the generator.

        Returns:
            OrchestratorResult with the final video, quality result,
            and retry history.
        """
        state = VideoState(
            prompt=prompt,
            video_path=video_path or "",
            max_retries=max_retries,
            _generator=generator,
        )

        while state.retry_count <= state.max_retries:
            t0 = time.time()

            # Step 1: Generate (or use existing video)
            state = self._generate(state, **kwargs)
            if not state.video_path:
                logger.error("No video path after generation step.")
                break

            # Step 2: Evaluate
            routing = self._evaluate(state)
            elapsed = round(time.time() - t0, 2)

            # Record iteration
            iteration_record = {
                "iteration": state.retry_count,
                "video_path": state.video_path,
                "routing": routing,
                "prompt": state.prompt,
                "elapsed_s": elapsed,
            }
            if state.quality_result and state.quality_result.decision:
                iteration_record["verdict"] = state.quality_result.decision.verdict
                iteration_record["confidence"] = state.quality_result.decision.confidence
            state.history.append(iteration_record)

            logger.info(
                "Iteration %d: routing=%s elapsed=%.1fs",
                state.retry_count, routing, elapsed,
            )

            if routing == "pass":
                return OrchestratorResult(
                    video_path=state.video_path,
                    prompt=state.prompt,
                    quality_result=state.quality_result,
                    decision=state.quality_result.decision if state.quality_result else None,
                    retries_used=state.retry_count,
                    success=True,
                    history=state.history,
                )

            if routing == "escalate":
                state.history[-1]["escalated"] = True
                break

            # Step 3: Correct
            state = self._correct(state)
            state.retry_count += 1

        # Exhausted retries or escalated — diagnose and return best effort
        diagnosis = None
        if state.quality_result and not state.quality_result.passed:
            diagnosis = self.diagnoser.diagnose(state.quality_result)

        return OrchestratorResult(
            video_path=state.video_path,
            prompt=state.prompt,
            quality_result=state.quality_result,
            diagnosis=diagnosis,
            decision=state.quality_result.decision if state.quality_result else None,
            retries_used=state.retry_count,
            success=False,
            history=state.history,
        )

    # -- private steps -------------------------------------------------------

    def _generate(self, state: VideoState, **kwargs: Any) -> VideoState:
        """Generate a video or use existing video_path."""
        if state._generator is not None:
            try:
                params = {"seed": kwargs.get("seed"), **kwargs}
                state.video_path = state._generator(state.prompt, params)
                logger.info("Generated video: %s", state.video_path)
            except Exception as exc:
                logger.error("Generation failed: %s", exc)
                state.video_path = ""
        # If no generator, video_path should already be set
        return state

    def _evaluate(self, state: VideoState) -> str:
        """Evaluate the video and return a routing decision.

        Returns one of: pass, retry_cheap, vlm_review, retry_with_correction, escalate
        """
        quality_result = qa_evaluate(
            state.video_path,
            prompt=state.prompt,
            config_path=self.config_path,
            layers=self.quality_layers,
        )
        state.quality_result = quality_result

        decision = quality_result.decision
        if decision is None:
            return "escalate"

        verdict = decision.verdict

        if verdict == "pass":
            return "pass"

        if verdict == "escalate":
            return "escalate"

        if verdict == "fail":
            # Determine if it's an L1 failure (cheap retry) or deeper issue
            if quality_result.l1_result and not quality_result.l1_result.passed:
                return "retry_cheap"
            # L2 failure with low score — cheap retry first
            if quality_result.l2_result and quality_result.l2_result.score < 0.5:
                return "retry_cheap"
            # L2 failure with moderate score — needs correction
            return "retry_with_correction"

        if verdict == "review":
            # Borderline — check if L3 was already run
            if quality_result.l3_result is not None:
                label = quality_result.l3_result.label
                if label in ("EXCELLENT", "GOOD"):
                    return "pass"
                else:
                    state.critique = quality_result.l3_result.critique
                    return "retry_with_correction"
            # L3 not yet run — trigger VLM review
            return "vlm_review"

        return "escalate"

    def _correct(self, state: VideoState) -> VideoState:
        """Diagnose failures and rewrite the prompt."""
        if state.quality_result is None:
            return state

        # Diagnose
        diagnosis = self.diagnoser.diagnose(state.quality_result)
        state.diagnosis = diagnosis

        logger.info(
            "Diagnosis: %s (%s) — %s",
            diagnosis.problem_type.name,
            diagnosis.severity,
            diagnosis.description,
        )

        # Try VLM-assisted reprompt if critique available
        vlm_critique = state.critique
        if not vlm_critique and state.quality_result.l3_result:
            vlm_critique = state.quality_result.l3_result.critique

        # Use rule-based rewriter (enhanced with VLM critique if available)
        rewrite = self.rewriter.rewrite(
            original_prompt=state.prompt,
            diagnosis=diagnosis,
            vlm_critique=vlm_critique or None,
        )

        state.corrected_prompt = rewrite.rewritten_prompt
        state.prompt = rewrite.rewritten_prompt

        logger.info(
            "Prompt rewritten (confidence=%.2f): %s",
            rewrite.confidence,
            rewrite.changes,
        )

        return state
