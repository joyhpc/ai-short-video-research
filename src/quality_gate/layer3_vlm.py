"""Layer 3 — VLM (Vision-Language Model) review.

Sends sampled frames (and optionally the full video) to a multimodal LLM
for subjective quality assessment, script-alignment grading, and — when
quality is low — a corrected generation prompt.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VLMResult:
    """Result of a VLM-based video review."""

    label: str  # EXCELLENT | GOOD | FAIR | POOR
    reasoning: str
    scores: dict[str, float] = field(default_factory=dict)
    critique: str = ""
    corrected_prompt: Optional[CorrectedPrompt] = None  # noqa: F821 — forward ref


@dataclass
class CorrectedPrompt:
    """A VLM-suggested rewrite of the original generation prompt."""

    original: str
    corrected: str
    changes: list[str] = field(default_factory=list)
    parameter_adjustments: dict[str, Any] = field(default_factory=dict)


# Patch forward reference now that CorrectedPrompt is defined.
VLMResult.__annotations__["corrected_prompt"] = Optional[CorrectedPrompt]


# ---------------------------------------------------------------------------
# Reviewer
# ---------------------------------------------------------------------------

class VLMReviewer:
    """Multi-modal LLM reviewer for video quality assessment.

    Supports pluggable providers; the default is Google Gemini.

    Args:
        provider: LLM provider name (``"gemini"`` | ``"openai"``).
        model: Model identifier (e.g. ``"gemini-2.5-flash"``).
        api_key: Optional API key.  Falls back to the ``GEMINI_API_KEY``
            or ``OPENAI_API_KEY`` environment variable.
    """

    SUPPORTED_PROVIDERS = ("gemini", "openai")

    def __init__(
        self,
        provider: str = "gemini",
        model: str = "gemini-2.5-flash",
        api_key: str | None = None,
    ) -> None:
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Choose from {self.SUPPORTED_PROVIDERS}."
            )
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.environ.get(
            "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY", ""
        )

    # -- frame sampling ------------------------------------------------------

    @staticmethod
    def sample_frames(
        video_path: str, n_frames: int = 16
    ) -> list[Any]:
        """Sample *n_frames* uniformly from the video.

        Returns a list of PIL Image objects.

        Args:
            video_path: Path to the video file.
            n_frames: Number of frames to sample.

        Returns:
            List of PIL.Image.Image instances.
        """
        # TODO: implement uniform frame sampling using cv2 / decord
        raise NotImplementedError

    # -- prompt construction -------------------------------------------------

    @staticmethod
    def build_review_prompt(
        script: str,
        criteria: dict[str, str] | None = None,
    ) -> str:
        """Construct the system + user prompt sent to the VLM.

        Args:
            script: The original video generation script / prompt.
            criteria: Optional mapping of criterion-name to description
                (e.g. ``{"visual_quality": "Rate 1-5 ..."}``)

        Returns:
            Fully-formatted prompt string.
        """
        default_criteria = {
            "visual_quality": "Rate overall visual quality (1-5).",
            "text_alignment": "How well does the video match the script? (1-5)",
            "temporal_coherence": "Are transitions and motion smooth? (1-5)",
            "aesthetic_appeal": "Is the video aesthetically pleasing? (1-5)",
            "technical_quality": "Any artifacts, glitches, or encoding issues? (1-5)",
        }
        criteria = criteria or default_criteria

        criteria_block = "\n".join(
            f"- **{k}**: {v}" for k, v in criteria.items()
        )

        prompt = (
            "You are a professional video quality reviewer.\n\n"
            f"## Original Script\n{script}\n\n"
            f"## Evaluation Criteria\n{criteria_block}\n\n"
            "## Instructions\n"
            "1. Review the provided video frames.\n"
            "2. Score each criterion on a 1-5 scale.\n"
            "3. Assign an overall label: EXCELLENT / GOOD / FAIR / POOR.\n"
            "4. If the label is FAIR or POOR, provide a specific critique and "
            "suggest a corrected generation prompt.\n"
            "5. Return your response as JSON with keys: label, scores, "
            "reasoning, critique, corrected_prompt."
        )
        return prompt

    # -- main review entry point ---------------------------------------------

    def review(
        self,
        video_path: str,
        script: str,
        criteria: dict[str, str] | None = None,
    ) -> VLMResult:
        """Run the full VLM review pipeline.

        1. Sample frames from the video.
        2. Build the evaluation prompt.
        3. Send to the VLM provider.
        4. Parse the response into a VLMResult.

        Args:
            video_path: Path to the video file.
            script: The original generation script / prompt.
            criteria: Optional custom evaluation criteria.

        Returns:
            VLMResult with label, scores, reasoning, and optional
            corrected prompt.
        """
        # TODO: implement end-to-end VLM review
        # frames = self.sample_frames(video_path)
        # prompt = self.build_review_prompt(script, criteria)
        # response = self._call_provider(frames, prompt)
        # return self._parse_response(response)
        raise NotImplementedError

    # -- re-prompting --------------------------------------------------------

    def reprompt(
        self, critique: str, original_prompt: str
    ) -> CorrectedPrompt:
        """Generate a corrected generation prompt based on VLM critique.

        Uses the VLM to rewrite the original prompt, incorporating the
        critique feedback to avoid previously-observed quality issues.

        Args:
            critique: The VLM's textual critique of the video.
            original_prompt: The original generation prompt.

        Returns:
            CorrectedPrompt with the rewritten prompt and change summary.
        """
        # TODO: implement VLM-based prompt correction
        raise NotImplementedError

    # -- private helpers -----------------------------------------------------

    def _call_provider(
        self, frames: list[Any], prompt: str
    ) -> dict[str, Any]:
        """Send frames + prompt to the configured VLM provider.

        Returns the raw parsed JSON response dict.
        """
        # TODO: implement provider-specific API call (Gemini / OpenAI)
        raise NotImplementedError

    @staticmethod
    def _parse_response(response: dict[str, Any]) -> VLMResult:
        """Parse raw VLM JSON response into a VLMResult."""
        # TODO: implement response parsing with validation
        raise NotImplementedError
