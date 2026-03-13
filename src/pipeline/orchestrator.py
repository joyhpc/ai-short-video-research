"""Pipeline orchestrator — generate -> evaluate -> correct loop.

Coordinates video generation, multi-layer quality assessment, diagnosis,
and prompt correction in a retry loop.  Designed for future integration
with LangGraph for stateful graph execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from src.quality_gate import QualityResult, evaluate as qa_evaluate
from src.quality_gate.aggregator import Decision
from src.correction.diagnosis import Diagnosis, ProblemDiagnoser
from src.correction.prompt_rewriter import PromptRewriter, RewriteResult


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
    quality_scores: dict[str, float] = field(default_factory=dict)
    critique: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class OrchestratorResult:
    """Final result returned by the orchestrator."""

    video_path: str
    prompt: str
    quality_result: Optional[QualityResult] = None
    retries_used: int = 0
    success: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class VideoOrchestrator:
    """Main orchestrator: generate -> evaluate -> correct loop.

    TODO: Integrate with LangGraph StateGraph for observable, resumable
    execution with conditional edges (pass / retry_cheap / vlm_review /
    retry_with_correction / escalate).

    Args:
        config_path: Optional YAML config for quality thresholds and
            pipeline settings.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = config_path
        self.diagnoser = ProblemDiagnoser()
        self.rewriter = PromptRewriter()

    # -- public API ----------------------------------------------------------

    def run(self, prompt: str, **kwargs: Any) -> OrchestratorResult:
        """Execute the full generate -> evaluate -> correct loop.

        Args:
            prompt: The video generation prompt.
            **kwargs: Forwarded to the generator (provider, seed, etc.).

        Returns:
            OrchestratorResult with the final video path, quality result,
            and retry history.
        """
        state = VideoState(
            prompt=prompt,
            max_retries=kwargs.pop("max_retries", 3),
        )

        while state.retry_count <= state.max_retries:
            # Step 1: Generate
            state = self._generate(state, **kwargs)

            # Step 2: Evaluate
            routing = self._evaluate(state)

            # Record iteration
            state.history.append({
                "iteration": state.retry_count,
                "video_path": state.video_path,
                "routing": routing,
                "scores": dict(state.quality_scores),
            })

            if routing == "pass":
                return OrchestratorResult(
                    video_path=state.video_path,
                    prompt=state.prompt,
                    quality_result=None,  # TODO: attach last QualityResult
                    retries_used=state.retry_count,
                    success=True,
                    history=state.history,
                )

            if routing == "escalate":
                break

            # Step 3: Correct
            state = self._correct(state)
            state.retry_count += 1

        # Exhausted retries or escalated
        return OrchestratorResult(
            video_path=state.video_path,
            prompt=state.prompt,
            retries_used=state.retry_count,
            success=False,
            history=state.history,
        )

    # -- private steps -------------------------------------------------------

    def _generate(self, state: VideoState, **kwargs: Any) -> VideoState:
        """Generate a video from the current prompt.

        TODO: Dispatch to the appropriate generator (AI video, stock
        footage, etc.) based on pipeline config.
        """
        # TODO: call generator and set state.video_path
        raise NotImplementedError("Video generation not yet implemented.")

    def _evaluate(self, state: VideoState) -> str:
        """Evaluate the generated video and return a routing decision.

        Routing decisions:
        - ``"pass"``:                Quality is acceptable.
        - ``"retry_cheap"``:         Stochastic failure — retry same prompt.
        - ``"vlm_review"``:          Borderline — send to VLM for review.
        - ``"retry_with_correction"``: Diagnosed failure — rewrite prompt.
        - ``"escalate"``:            Cannot auto-fix — needs human review.

        Returns:
            One of the routing decision strings listed above.
        """
        # TODO: run qa_evaluate, map Decision.verdict to routing string
        raise NotImplementedError("Evaluation routing not yet implemented.")

    def _correct(self, state: VideoState) -> VideoState:
        """Diagnose failures and rewrite the prompt for the next attempt.

        Updates ``state.prompt`` with the corrected version.
        """
        # TODO: run diagnoser + rewriter, update state.prompt
        raise NotImplementedError("Correction logic not yet implemented.")

    # -- LangGraph integration stub ------------------------------------------

    def _build_graph(self) -> Any:
        """Build a LangGraph StateGraph for the orchestration loop.

        TODO: Define nodes (generate, evaluate_l1, evaluate_l2,
        evaluate_l3, diagnose, correct) and conditional edges
        based on routing decisions.

        Returns:
            A compiled LangGraph StateGraph (placeholder).
        """
        # from langgraph.graph import StateGraph
        # graph = StateGraph(VideoState)
        # graph.add_node("generate", self._generate)
        # graph.add_node("evaluate", self._evaluate)
        # graph.add_node("correct", self._correct)
        # graph.add_conditional_edges("evaluate", self._route)
        # return graph.compile()
        raise NotImplementedError("LangGraph integration pending.")
