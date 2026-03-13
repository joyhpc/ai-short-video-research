"""Prompt rewriting — transform a generation prompt based on quality diagnosis.

Uses diagnosis information and optional VLM critique to produce a
corrected prompt that avoids previously-observed quality problems.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .diagnosis import Diagnosis, ProblemType

logger = logging.getLogger(__name__)


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
            "Keep all described elements on-screen and recognisable.",
            "Anchor the composition on the primary subject described in the prompt.",
        ],
        ProblemType.AESTHETIC: [
            "Use cinematic lighting and vivid colors.",
            "High production quality, 4K aesthetic.",
            "Apply professional color grading with balanced contrast.",
            "Avoid overexposure and crushed blacks; maintain a wide dynamic range.",
            "Use shallow depth-of-field to separate subject from background.",
        ],
        ProblemType.COHERENCE: [
            "Smooth continuous camera motion, no abrupt cuts.",
            "Maintain consistent scene throughout the clip.",
            "Preserve spatial consistency: objects must not teleport between frames.",
            "Use gradual transitions rather than jump cuts.",
            "Keep character appearance and clothing consistent across the clip.",
        ],
        ProblemType.TECHNICAL: [
            "Output format: H.264, 1080x1920, 30fps.",
            "Ensure stable frame rate with no dropped frames.",
            "Avoid compression artefacts and banding in gradients.",
        ],
        ProblemType.TIMING: [
            "Align narration pacing with visual transitions.",
            "Synchronise text overlays to appear for at least 2 seconds each.",
            "Match scene duration to audio beats when music is present.",
        ],
    }

    def __init__(self, vlm_reviewer=None):
        """Initialise the rewriter.

        Args:
            vlm_reviewer: Optional VLMReviewer instance.  When provided (and
                a VLM critique string is passed to *rewrite*), the rewriter
                will delegate to ``VLMReviewer.reprompt()`` for higher-quality
                rewrites before falling back to rule-based logic.
        """
        self._vlm_reviewer = vlm_reviewer

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rewrite(
        self,
        original_prompt: str,
        diagnosis: Diagnosis,
        vlm_critique: str | None = None,
    ) -> RewriteResult:
        """Produce a corrected generation prompt.

        When a *vlm_reviewer* was provided at construction time **and**
        *vlm_critique* is not ``None``, the method first attempts a
        VLM-assisted rewrite (higher confidence).  If VLM rewriting is
        unavailable or raises, it falls back to deterministic rule-based
        logic.

        Args:
            original_prompt: The prompt used to generate the failed video.
            diagnosis: Structured diagnosis from ProblemDiagnoser.
            vlm_critique: Optional free-text critique from the VLM reviewer.

        Returns:
            RewriteResult with the rewritten prompt and a summary of changes.
        """
        # Try VLM-assisted rewriting first
        if self._vlm_reviewer and vlm_critique:
            try:
                return self.rewrite_with_vlm(original_prompt, vlm_critique)
            except Exception as exc:
                logger.warning("VLM rewrite failed, falling back to rules: %s", exc)

        # Fall back to rule-based rewriting
        return self._rewrite_rule_based(original_prompt, diagnosis, vlm_critique)

    def rewrite_with_vlm(
        self, original_prompt: str, critique: str
    ) -> RewriteResult:
        """Use VLM to rewrite the prompt based on critique.

        Delegates to ``VLMReviewer.reprompt()`` and wraps the result in a
        :class:`RewriteResult` with confidence 0.8.

        Args:
            original_prompt: The prompt that produced the unsatisfactory video.
            critique: Free-text critique describing what went wrong.

        Returns:
            RewriteResult with the VLM-generated corrected prompt.

        Raises:
            Exception: Propagated from the underlying VLM call.
        """
        result = self._vlm_reviewer.reprompt(critique, original_prompt)
        return RewriteResult(
            original_prompt=original_prompt,
            rewritten_prompt=result.corrected,
            changes=result.changes,
            confidence=0.8,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rewrite_rule_based(
        self,
        original_prompt: str,
        diagnosis: Diagnosis,
        vlm_critique: str | None = None,
    ) -> RewriteResult:
        """Deterministic rule-based rewrite (fallback path)."""
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
        confidence = 0.5

        return RewriteResult(
            original_prompt=original_prompt,
            rewritten_prompt=rewritten,
            changes=changes,
            confidence=confidence,
        )
