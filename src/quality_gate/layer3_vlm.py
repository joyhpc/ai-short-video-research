"""Layer 3 — VLM (Vision-Language Model) review.

Sends sampled frames (and optionally the full video) to a multimodal LLM
for subjective quality assessment, script-alignment grading, and — when
quality is low — a corrected generation prompt.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

_LABEL_SCORES: dict[str, float] = {
    "EXCELLENT": 1.0,
    "GOOD": 0.75,
    "FAIR": 0.45,
    "POOR": 0.0,
}

_VALID_LABELS = frozenset(_LABEL_SCORES.keys())


@dataclass
class VLMResult:
    """Result of a VLM-based video review."""

    label: str  # EXCELLENT | GOOD | FAIR | POOR
    reasoning: str
    scores: dict[str, float] = field(default_factory=dict)
    critique: str = ""
    corrected_prompt: Optional[CorrectedPrompt] = None  # noqa: F821 — forward ref

    @property
    def score(self) -> float:
        """Numeric score derived from the label."""
        return _LABEL_SCORES.get(self.label, 0.0)


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
        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise ImportError(
                "cv2 and numpy are required for frame sampling. "
                "Install them with: pip install opencv-python-headless numpy"
            ) from exc

        if Image is None:
            raise ImportError(
                "Pillow is required for frame sampling. "
                "Install it with: pip install Pillow"
            )

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file: {video_path}")

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            cap.release()
            raise ValueError(f"Video has no frames: {video_path}")

        n_frames = min(n_frames, total)
        indices = np.linspace(0, total - 1, n_frames, dtype=int)
        frames: list[Any] = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(rgb))
        cap.release()
        return frames

    # -- prompt construction -------------------------------------------------

    @staticmethod
    def build_review_prompt(
        script: str,
        criteria: dict[str, str] | None = None,
    ) -> str:
        """Construct the evaluation prompt sent to the VLM.

        Uses discrete labels (EXCELLENT/GOOD/FAIR/POOR) with chain-of-thought
        reasoning and structured JSON output.

        Args:
            script: The original video generation script / prompt.
            criteria: Optional mapping of criterion-name to description.
                Kept for API compatibility; the new protocol uses fixed
                dimensions.

        Returns:
            Fully-formatted prompt string.
        """
        prompt = (
            "You are a professional video quality reviewer.\n\n"
            "## Original Generation Prompt\n"
            f"{script}\n\n"
            "## Evaluation Dimensions\n"
            "Assess each dimension using EXACTLY one of these labels: "
            "EXCELLENT, GOOD, FAIR, POOR.\n\n"
            "- **visual_fidelity**: Sharpness, color accuracy, absence of "
            "artifacts, glitches, or encoding issues.\n"
            "- **content_alignment**: How faithfully the video matches the "
            "original generation prompt above.\n"
            "- **narrative_coherence**: Temporal flow — are transitions smooth, "
            "is motion natural, does the sequence make sense?\n"
            "- **overall_feel**: Aesthetic appeal, production quality, and "
            "viewer engagement.\n\n"
            "## Instructions\n"
            "1. First, write your OBSERVATIONS about the video frames — "
            "describe what you see.\n"
            "2. For EACH dimension, provide chain-of-thought REASONING before "
            "assigning a label. Note specific issues if any.\n"
            "3. Assign an OVERALL label (EXCELLENT / GOOD / FAIR / POOR).\n"
            "4. If the overall label is FAIR or POOR, you MUST provide "
            "corrective_feedback with concrete suggestions.\n"
            "5. Return your ENTIRE response as a single JSON object with "
            "EXACTLY this structure (no markdown, no extra text):\n\n"
            "```\n"
            "{\n"
            '  "observations": "<what you see in the frames>",\n'
            '  "dimension_assessments": {\n'
            '    "visual_fidelity": {\n'
            '      "reasoning": "<chain of thought>",\n'
            '      "label": "EXCELLENT|GOOD|FAIR|POOR",\n'
            '      "issues": ["issue1", "issue2"]\n'
            "    },\n"
            '    "content_alignment": { ... same structure ... },\n'
            '    "narrative_coherence": { ... same structure ... },\n'
            '    "overall_feel": { ... same structure ... }\n'
            "  },\n"
            '  "overall_label": "EXCELLENT|GOOD|FAIR|POOR",\n'
            '  "corrective_feedback": {\n'
            '    "primary_issue": "<main problem>",\n'
            '    "suggested_prompt_changes": "<how to rewrite the prompt>",\n'
            '    "parameter_adjustments": {"key": "value"}\n'
            "  }\n"
            "}\n"
            "```\n\n"
            "IMPORTANT: The corrective_feedback field is REQUIRED when "
            "overall_label is FAIR or POOR, and should be null otherwise."
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
        # Guard: no API key
        if not self.api_key:
            logger.warning("No API key configured for VLM provider '%s'.", self.provider)
            return VLMResult(
                label="POOR",
                reasoning="No API key configured for VLM review.",
                scores={},
                critique="VLM review skipped — no API key available.",
            )

        try:
            frames = self.sample_frames(video_path)
            prompt = self.build_review_prompt(script, criteria)
            response = self._call_provider(frames, prompt)
            return self._parse_response(response, original_prompt=script)
        except Exception as exc:
            logger.error("VLM review failed: %s", exc, exc_info=True)
            return VLMResult(
                label="POOR",
                reasoning=f"VLM review failed with error: {exc}",
                scores={},
                critique=f"Error during VLM review: {exc}",
            )

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
        reprompt_instruction = (
            "You are a video generation prompt engineer.\n\n"
            "## Original Prompt\n"
            f"{original_prompt}\n\n"
            "## Quality Critique\n"
            f"{critique}\n\n"
            "## Task\n"
            "Rewrite the original prompt to address ALL issues mentioned in "
            "the critique. The corrected prompt should generate a higher-quality "
            "video.\n\n"
            "Return your response as JSON with EXACTLY this structure:\n"
            "```\n"
            "{\n"
            '  "corrected_prompt": "<the improved prompt>",\n'
            '  "changes": ["change1", "change2", ...],\n'
            '  "parameter_adjustments": {"key": "value"}\n'
            "}\n"
            "```"
        )

        try:
            # Call provider with no frames (text-only reprompt)
            raw_text = self._call_provider_text(reprompt_instruction)
            data = self._extract_json(raw_text)
        except Exception as exc:
            logger.error("Reprompt failed: %s", exc, exc_info=True)
            # Fallback: return the original prompt with the critique appended
            return CorrectedPrompt(
                original=original_prompt,
                corrected=f"{original_prompt}\n\n[Quality note: {critique}]",
                changes=["Appended critique as quality note (VLM reprompt failed)."],
                parameter_adjustments={},
            )

        return CorrectedPrompt(
            original=original_prompt,
            corrected=data.get("corrected_prompt", original_prompt),
            changes=data.get("changes", []),
            parameter_adjustments=data.get("parameter_adjustments", {}),
        )

    # -- private helpers -----------------------------------------------------

    def _call_provider(
        self, frames: list[Any], prompt: str
    ) -> dict[str, Any]:
        """Send frames + prompt to the configured VLM provider.

        Returns the raw parsed JSON response dict.
        """
        if self.provider == "gemini":
            return self._call_gemini(frames, prompt)
        elif self.provider == "openai":
            return self._call_openai(frames, prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_provider_text(self, prompt: str) -> str:
        """Send a text-only prompt to the configured VLM provider.

        Returns the raw response text.
        """
        if self.provider == "gemini":
            return self._call_gemini_text(prompt)
        elif self.provider == "openai":
            return self._call_openai_text(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # -- Gemini provider -----------------------------------------------------

    def _call_gemini(
        self, frames: list[Any], prompt: str
    ) -> dict[str, Any]:
        """Call Google Gemini with frames and prompt."""
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai is required for Gemini provider. "
                "Install it with: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)

        # Build content list: frames as images + text prompt
        content: list[Any] = []
        content.append("Here are frames from a video, sampled uniformly:")
        for _i, frame in enumerate(frames):
            content.append(frame)  # PIL Image is accepted directly
        content.append(prompt)

        response = model.generate_content(content)
        return self._extract_json(response.text)

    def _call_gemini_text(self, prompt: str) -> str:
        """Call Google Gemini with a text-only prompt."""
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai is required for Gemini provider. "
                "Install it with: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text

    # -- OpenAI provider -----------------------------------------------------

    def _call_openai(
        self, frames: list[Any], prompt: str
    ) -> dict[str, Any]:
        """Call OpenAI with frames and prompt."""
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "openai is required for OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc

        import base64
        import io

        client = openai.OpenAI(api_key=self.api_key)

        # Build message content: images as base64 data URLs + text
        content_parts: list[dict[str, Any]] = []

        content_parts.append({
            "type": "text",
            "text": "Here are frames from a video, sampled uniformly:",
        })

        for frame in frames:
            buf = io.BytesIO()
            frame.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}",
                    "detail": "low",
                },
            })

        content_parts.append({"type": "text", "text": prompt})

        messages = [{"role": "user", "content": content_parts}]

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content or ""
        return self._extract_json(raw_text)

    def _call_openai_text(self, prompt: str) -> str:
        """Call OpenAI with a text-only prompt."""
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "openai is required for OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc

        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""

    # -- JSON extraction -----------------------------------------------------

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Extract a JSON object from VLM response text.

        Handles common cases:
        - Raw JSON string
        - JSON wrapped in ```json ... ``` markdown code blocks
        - JSON wrapped in ``` ... ``` code blocks
        - JSON embedded in surrounding prose

        Args:
            text: Raw response text from the VLM.

        Returns:
            Parsed dict.

        Raises:
            ValueError: If no valid JSON object can be extracted.
        """
        # Strip whitespace
        text = text.strip()

        # Attempt 1: Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Attempt 2: Extract from ```json ... ``` or ``` ... ``` blocks
        code_block_pattern = re.compile(
            r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL
        )
        match = code_block_pattern.search(text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Attempt 3: Find the first { ... } block (greedy, outermost braces)
        brace_pattern = re.compile(r"\{.*\}", re.DOTALL)
        match = brace_pattern.search(text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Could not extract valid JSON from VLM response. "
            f"Response text (first 500 chars): {text[:500]}"
        )

    # -- response parsing ----------------------------------------------------

    @staticmethod
    def _parse_response(
        response: dict[str, Any],
        original_prompt: str = "",
    ) -> VLMResult:
        """Parse raw VLM JSON response into a VLMResult.

        Args:
            response: Parsed JSON dict from the VLM.
            original_prompt: The original generation prompt (used when
                constructing CorrectedPrompt).

        Returns:
            VLMResult with label, scores, reasoning, and optional
            corrected prompt.
        """
        # -- Extract overall label -------------------------------------------
        raw_label = str(response.get("overall_label", "POOR")).upper().strip()
        if raw_label not in _VALID_LABELS:
            # Try to fuzzy-match
            for valid in _VALID_LABELS:
                if valid in raw_label:
                    raw_label = valid
                    break
            else:
                raw_label = "POOR"

        # -- Extract observations / reasoning --------------------------------
        observations = response.get("observations", "")
        reasoning_parts = [observations] if observations else []

        # -- Extract dimension scores ----------------------------------------
        scores: dict[str, float] = {}
        dimension_assessments = response.get("dimension_assessments", {})
        for dim_name, dim_data in dimension_assessments.items():
            if isinstance(dim_data, dict):
                dim_label = str(dim_data.get("label", "")).upper().strip()
                dim_score = _LABEL_SCORES.get(dim_label, 0.0)
                scores[dim_name] = dim_score

                # Collect reasoning for the overall narrative
                dim_reasoning = dim_data.get("reasoning", "")
                if dim_reasoning:
                    reasoning_parts.append(f"{dim_name}: {dim_reasoning}")

                # Collect issues
                issues = dim_data.get("issues", [])
                if issues:
                    reasoning_parts.append(
                        f"{dim_name} issues: {', '.join(str(i) for i in issues)}"
                    )

        reasoning = "\n".join(reasoning_parts)

        # -- Extract corrective feedback into CorrectedPrompt ----------------
        corrected_prompt: CorrectedPrompt | None = None
        critique = ""

        feedback = response.get("corrective_feedback")
        if feedback and isinstance(feedback, dict):
            primary_issue = feedback.get("primary_issue", "")
            suggested_changes = feedback.get("suggested_prompt_changes", "")
            param_adjustments = feedback.get("parameter_adjustments", {})

            critique = primary_issue
            if suggested_changes:
                critique = f"{critique}. Suggested changes: {suggested_changes}"

            if primary_issue or suggested_changes:
                corrected_prompt = CorrectedPrompt(
                    original=original_prompt,
                    corrected=suggested_changes or original_prompt,
                    changes=[primary_issue] if primary_issue else [],
                    parameter_adjustments=(
                        param_adjustments if isinstance(param_adjustments, dict)
                        else {}
                    ),
                )

        return VLMResult(
            label=raw_label,
            reasoning=reasoning,
            scores=scores,
            critique=critique,
            corrected_prompt=corrected_prompt,
        )
