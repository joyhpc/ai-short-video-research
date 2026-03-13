"""Background music generator — select and prepare BGM tracks."""

from __future__ import annotations

import glob
import logging
import os
import random
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AudioClip:
    """Background music audio clip."""

    local_path: str
    duration: float = 0.0
    mood: str = ""
    bpm: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class BGMGenerator:
    """Select and prepare background music for video compositions.

    Supports local library lookup and API-based music generation.

    Args:
        library_path: Path to a local BGM library directory.
    """

    MOOD_TAGS = (
        "upbeat", "calm", "dramatic", "inspiring",
        "suspenseful", "happy", "melancholic", "energetic",
    )

    AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac")

    def __init__(self, library_path: str | None = None) -> None:
        self.library_path = library_path

    def _scan_library(self) -> list[str]:
        """Scan the library path for audio files."""
        if not self.library_path or not os.path.isdir(self.library_path):
            raise ValueError("No BGM library configured")

        files: list[str] = []
        for ext in self.AUDIO_EXTENSIONS:
            pattern = os.path.join(self.library_path, f"**/*{ext}")
            files.extend(glob.glob(pattern, recursive=True))
            # Also match files directly in library_path
            pattern_flat = os.path.join(self.library_path, f"*{ext}")
            files.extend(glob.glob(pattern_flat))

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for f in files:
            real = os.path.realpath(f)
            if real not in seen:
                seen.add(real)
                unique.append(f)

        return unique

    def _get_duration(self, path: str) -> float:
        """Get audio duration in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as exc:
            logger.warning("ffprobe failed for %s: %s", path, exc)
            return 0.0

    def _trim_and_fade(
        self,
        input_path: str,
        duration: float,
        fade_in: float,
        fade_out: float,
    ) -> str:
        """Trim audio to *duration* and apply fade in/out. Returns temp file path."""
        suffix = os.path.splitext(input_path)[1] or ".mp3"
        fd, output_path = tempfile.mkstemp(suffix=suffix, prefix="bgm_trimmed_")
        os.close(fd)

        fade_out_start = max(0.0, duration - fade_out)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-t", str(duration),
            "-af",
            f"afade=t=in:d={fade_in},afade=t=out:st={fade_out_start}:d={fade_out}",
            output_path,
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as exc:
            logger.error("ffmpeg trim failed: %s\nstderr: %s", exc, exc.stderr)
            # Clean up on failure
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise

        return output_path

    def select(
        self,
        mood: str,
        duration: float,
        fade_in: float = 1.0,
        fade_out: float = 2.0,
    ) -> AudioClip:
        """Select a BGM track matching the desired mood and duration.

        If the selected track is longer than *duration*, it will be
        trimmed and faded out.

        Args:
            mood: Desired mood tag (see MOOD_TAGS).
            duration: Target duration in seconds.
            fade_in: Fade-in duration in seconds.
            fade_out: Fade-out duration in seconds.

        Returns:
            AudioClip trimmed and faded to the requested duration.
        """
        all_files = self._scan_library()
        if not all_files:
            raise ValueError("No BGM library configured")

        # Try to match files containing the mood tag in the filename
        mood_lower = mood.lower()
        matched = [
            f for f in all_files
            if mood_lower in os.path.basename(f).lower()
        ]

        if matched:
            chosen = random.choice(matched)
            logger.info("Mood-matched BGM: %s (mood=%s)", chosen, mood)
        else:
            chosen = random.choice(all_files)
            logger.info(
                "No mood match for '%s', randomly selected: %s", mood, chosen
            )

        # Trim to target duration with fade in/out
        trimmed_path = self._trim_and_fade(chosen, duration, fade_in, fade_out)

        # Get actual duration of the trimmed file
        actual_duration = self._get_duration(trimmed_path)

        return AudioClip(
            local_path=trimmed_path,
            duration=actual_duration,
            mood=mood,
            metadata={
                "source": chosen,
                "fade_in": fade_in,
                "fade_out": fade_out,
                "target_duration": duration,
            },
        )
