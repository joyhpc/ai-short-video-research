"""Background music generator — select and prepare BGM tracks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


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

    def __init__(self, library_path: str | None = None) -> None:
        self.library_path = library_path

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
        # TODO: implement BGM selection and trimming
        raise NotImplementedError
