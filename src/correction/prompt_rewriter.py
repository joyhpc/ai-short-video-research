"""Prompt rewriting — transform a generation prompt based on quality diagnosis.

Uses diagnosis information and optional VLM critique to produce a
corrected prompt that avoids previously-observed quality problems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .diagnosis import Diagnosis, ProblemType


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RewriteResult:
    """Result of a prompt rewrite operation."""

    original_prompt: str
    rewritten_prompt: str
    changes: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 – 1.0


# ---------------------------------------------------------------------------
# Rewriter
# ---------------------------------------------------------------------------

class PromptRewriter:
    """Rewrite generation prompts to correct diagnosed quality issues.

    Strategy varies by ProblemType:
    - ALIGNMENT: rephrase for clarity, add explicit subject/action keywords.
    - AESTHETIC: inject style modifiers (e.g. "cinematic lighting").
    - COHERENCE: add temporal guidance ("smooth camera motion", "no cuts").
    - TECHNICAL: adjust format directives.
    - TIMING: modify pacing / subtitle cues.
    """

    # Modifier templates per problem type
    _MODIFIERS: dict[ProblemType, list[str]] = {
        ProblemType.ALIGNMENT: [
            "Ensure the video clearly depicts: {subject}.",
            "The main subject must be visible throughout the clip.",
        ],
        ProblemType.AESTHETIC: [
            "Use cinematic lighting and vivid colors.",
            "High production quality, 4K aesthetic.",
        ],
        ProblemType.COHERENCE: [
            "Smooth continuous camera motion, no abrupt cuts.",
            "Maintain consistent scene throughout the clip.",
        ],
        ProblemType.TECHNICAL: [
            "Output format: H.264, 1080x1920, 30fps.",
        ],
        ProblemType.TIMING: [
            "Align narration pacing with visual transitions.",
        ],
    }

    def rewrite(
        self,
        original_prompt: str,
        diagnosis: Diagnosis,
        vlm_critique: str | None = None,
    ) -> RewriteResult:
        """Produce a corrected generation prompt.

        The rewriting logic is intentionally rule-based in this skeleton;
        Phase 2 will add LLM-assisted rewriting.

        Args:
            original_prompt: The prompt used to generate the failed video.
            diagnosis: Structured diagnosis from ProblemDiagnoser.
            vlm_critique: Optional free-text critique from the VLM reviewer.

        Returns:
            RewriteResult with the rewritten prompt and a summary of changes.
        """
        # TODO: replace rule-based logic with LLM-assisted rewriting
        changes: list[str] = []
        parts = [original_prompt.rstrip(".")]

        # Append problem-specific modifiers
        modifiers = self._MODIFIERS.get(diagnosis.problem_type, [])
        for mod in modifiers:
            formatted = mod.format(subject=original_prompt[:60])
            parts.append(formatted)
            changes.append(f"Added modifier for {diagnosis.problem_type.name}: {formatted}")

        # Incorporate VLM critique if available
        if vlm_critique:
            parts.append(f"Address reviewer feedback: {vlm_critique[:200]}")
            changes.append("Incorporated VLM critique feedback.")

        rewritten = ". ".join(parts) + "."
        confidence = 0.5 if not vlm_critique else 0.7

        return RewriteResult(
            original_prompt=original_prompt,
            rewritten_prompt=rewritten,
            changes=changes,
            confidence=confidence,
        )
