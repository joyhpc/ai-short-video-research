"""Subtitle generator — transcribe audio and produce SRT subtitles."""

from __future__ import annotations

from typing import Any, Optional


class SubtitleGenerator:
    """Generate SRT subtitles from audio via speech-to-text.

    Supports Whisper (local) and cloud ASR providers.

    Args:
        default_method: Default transcription method.
        model_size: Whisper model size (tiny/base/small/medium/large).
    """

    SUPPORTED_METHODS = ("whisper", "whisper_api", "azure_stt")

    def __init__(
        self,
        default_method: str = "whisper",
        model_size: str = "base",
    ) -> None:
        self.default_method = default_method
        self.model_size = model_size

    def generate(
        self,
        audio_path: str,
        method: str | None = None,
        language: str = "zh",
        max_chars_per_line: int = 20,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate SRT subtitle content from an audio file.

        Args:
            audio_path: Path to the audio file to transcribe.
            method: Override the default transcription method.
            language: ISO 639-1 language code.
            max_chars_per_line: Maximum characters per subtitle line.
            output_path: If provided, also writes the SRT to this path.
            **kwargs: Method-specific parameters.

        Returns:
            SRT-formatted subtitle string.
        """
        # TODO: implement Whisper transcription and SRT formatting
        raise NotImplementedError
