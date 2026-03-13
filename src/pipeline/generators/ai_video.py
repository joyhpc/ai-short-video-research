"""AI video generator — dispatch to AI video generation APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class VideoClip:
    """Generated video clip with metadata."""

    local_path: str
    prompt: str
    provider: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    generation_params: dict[str, Any] = field(default_factory=dict)


class AIVideoGenerator:
    """Generate video clips using AI video generation models.

    Supports multiple providers: Kling, Runway, Pika, etc.

    Args:
        default_provider: Default generation provider.
        api_keys: Mapping of provider names to API keys.
    """

    SUPPORTED_PROVIDERS = ("kling", "runway", "pika", "hailuo")

    def __init__(
        self,
        default_provider: str = "kling",
        api_keys: dict[str, str] | None = None,
    ) -> None:
        self.default_provider = default_provider
        self.api_keys = api_keys or {}

    def generate(
        self,
        prompt: str,
        provider: str | None = None,
        duration: float = 5.0,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> VideoClip:
        """Generate a video clip from a text prompt.

        Args:
            prompt: Text description of the desired video.
            provider: Override the default provider.
            duration: Desired clip duration in seconds.
            width: Output width in pixels.
            height: Output height in pixels.
            seed: Random seed for reproducibility.
            **kwargs: Provider-specific generation parameters.

        Returns:
            VideoClip with local_path set to the downloaded output.
        """
        # TODO: implement provider-specific API calls
        raise NotImplementedError
