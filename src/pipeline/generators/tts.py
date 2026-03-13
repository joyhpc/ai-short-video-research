"""Text-to-speech generator — convert script text to narration audio."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AudioClip:
    """Generated audio clip with metadata."""

    local_path: str
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 1
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class TTSGenerator:
    """Generate narration audio from text using TTS engines.

    Supports edge-tts (free), Azure TTS, and ElevenLabs.

    Args:
        default_provider: Default TTS provider.
        default_voice: Default voice identifier.
    """

    SUPPORTED_PROVIDERS = ("edge-tts", "azure", "elevenlabs")

    def __init__(
        self,
        default_provider: str = "edge-tts",
        default_voice: str = "zh-CN-XiaoxiaoNeural",
    ) -> None:
        self.default_provider = default_provider
        self.default_voice = default_voice

    def generate(
        self,
        text: str,
        voice: str | None = None,
        provider: str | None = None,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> AudioClip:
        """Generate speech audio from text.

        Args:
            text: The script text to convert to speech.
            voice: Voice identifier (provider-specific).
            provider: Override the default provider.
            output_path: Where to save the audio file.
            **kwargs: Provider-specific parameters (rate, pitch, etc.).

        Returns:
            AudioClip with local_path pointing to the generated audio.
        """
        # TODO: implement provider-specific TTS generation
        raise NotImplementedError
