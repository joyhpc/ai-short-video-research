"""Text-to-speech generator — convert script text to narration audio."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import edge_tts

    _HAS_EDGE_TTS = True
except ImportError:
    _HAS_EDGE_TTS = False

logger = logging.getLogger(__name__)


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

    # ── public API ───────────────────────────────────────────────

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
        provider = provider or self.default_provider
        voice = voice or self.default_voice

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

        if provider == "edge-tts":
            self._generate_edge_tts(text, voice, output_path, **kwargs)
        elif provider == "elevenlabs":
            self._generate_elevenlabs(text, voice, output_path, **kwargs)
        else:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Choose from: {self.SUPPORTED_PROVIDERS}"
            )

        duration = self._get_duration(output_path)
        logger.info("TTS (%s): %.1fs audio -> %s", provider, duration, output_path)

        return AudioClip(
            local_path=output_path,
            duration=duration,
            provider=provider,
            metadata={"voice": voice, **kwargs},
        )

    # ── edge-tts provider ────────────────────────────────────────

    def _generate_edge_tts(
        self,
        text: str,
        voice: str,
        output_path: str,
        **kwargs: Any,
    ) -> None:
        if not _HAS_EDGE_TTS:
            raise RuntimeError(
                "edge-tts is not installed. Run: pip install edge-tts"
            )

        import asyncio

        rate = kwargs.get("rate", "+0%")
        pitch = kwargs.get("pitch", "+0Hz")

        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        asyncio.run(communicate.save(output_path))

    # ── ElevenLabs provider ──────────────────────────────────────

    def _generate_elevenlabs(
        self,
        text: str,
        voice: str,
        output_path: str,
        **kwargs: Any,
    ) -> None:
        import urllib.request

        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ELEVENLABS_API_KEY environment variable is not set."
            )

        voice_id = kwargs.get("voice_id", voice)
        model_id = kwargs.get("model_id", "eleven_multilingual_v2")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        payload = json.dumps({"text": text, "model_id": model_id}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )

        with urllib.request.urlopen(req) as resp, open(output_path, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _get_duration(path: str) -> float:
        """Return audio duration in seconds via ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            info = json.loads(result.stdout)
            return float(info["format"]["duration"])
        except (subprocess.CalledProcessError, KeyError, FileNotFoundError) as exc:
            logger.warning("ffprobe failed for %s: %s — returning 0.0", path, exc)
            return 0.0
