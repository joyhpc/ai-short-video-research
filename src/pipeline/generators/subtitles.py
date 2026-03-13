"""Subtitle generator — transcribe audio and produce SRT subtitles."""

from __future__ import annotations

import logging
import math
import os
import tempfile
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _split_text(text: str, max_chars: int) -> list[str]:
    """Split text into lines of at most *max_chars* characters.

    Tries to split on natural boundaries (spaces, punctuation) when possible.
    """
    if len(text) <= max_chars:
        return [text]

    lines: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            lines.append(remaining)
            break

        # Find a good split point
        split_at = max_chars
        # Look backwards for a space or punctuation to split on
        for i in range(max_chars, max(max_chars - 10, 0), -1):
            if remaining[i] in (" ", ",", ".", "!", "?", ";", "\u3002", "\uff0c",
                                "\uff01", "\uff1f", "\u3001"):
                split_at = i + 1
                break

        lines.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    return lines


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
        active_method = method or self.default_method

        if active_method == "whisper":
            srt_content = self._generate_whisper(
                audio_path, language, max_chars_per_line, **kwargs
            )
        else:
            raise NotImplementedError(
                f"Method '{active_method}' is not yet implemented"
            )

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            logger.info("SRT written to %s", output_path)

        return srt_content

    def _generate_whisper(
        self,
        audio_path: str,
        language: str,
        max_chars_per_line: int,
        **kwargs: Any,
    ) -> str:
        """Transcribe with openai-whisper and return SRT string."""
        try:
            import whisper  # type: ignore[import-untyped]
        except ImportError:
            logger.warning(
                "openai-whisper is not installed. "
                "Install it with: pip install openai-whisper. "
                "Returning empty SRT."
            )
            return "# openai-whisper not installed — no subtitles generated\n"

        logger.info(
            "Loading Whisper model '%s' for %s ...", self.model_size, audio_path
        )
        model = whisper.load_model(self.model_size)

        logger.info("Transcribing %s (language=%s) ...", audio_path, language)
        result = model.transcribe(audio_path, language=language, **kwargs)

        segments = result.get("segments", [])
        if not segments:
            logger.warning("Whisper returned no segments for %s", audio_path)
            return ""

        srt_blocks: list[str] = []
        index = 1

        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()

            if not text:
                continue

            # Split long lines
            lines = _split_text(text, max_chars_per_line)

            # If split produced multiple chunks, distribute time evenly
            if len(lines) > 1:
                chunk_duration = (end - start) / len(lines)
                for i, line in enumerate(lines):
                    chunk_start = start + i * chunk_duration
                    chunk_end = start + (i + 1) * chunk_duration
                    srt_blocks.append(
                        f"{index}\n"
                        f"{_format_timestamp(chunk_start)} --> "
                        f"{_format_timestamp(chunk_end)}\n"
                        f"{line}\n"
                    )
                    index += 1
            else:
                srt_blocks.append(
                    f"{index}\n"
                    f"{_format_timestamp(start)} --> "
                    f"{_format_timestamp(end)}\n"
                    f"{text}\n"
                )
                index += 1

        return "\n".join(srt_blocks)
