"""Video composer — assemble video clips, audio, subtitles, and BGM into a final video."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CompositionSpec:
    """Specification for a video composition."""

    video_clips: list[str] = field(default_factory=list)
    audio_path: str = ""
    subtitle_path: str = ""
    bgm_path: str = ""
    bgm_volume: float = 0.15  # relative to narration
    output_path: str = ""
    output_width: int = 1080
    output_height: int = 1920
    fps: int = 30
    codec: str = "libx264"
    audio_codec: str = "aac"


class VideoComposer:
    """Assemble final video from individual components.

    Uses FFmpeg (via subprocess or ffmpeg-python) to combine video clips,
    narration audio, subtitles, and background music into a single output.
    """

    def compose(
        self,
        video_clips: list[str],
        audio: str,
        subtitles: str,
        bgm: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        bgm_volume: float = 0.15,
        **kwargs: Any,
    ) -> str:
        """Compose a final video from components.

        Pipeline:
        1. Concatenate / crossfade video clips.
        2. Mix narration audio with BGM (BGM ducked to bgm_volume).
        3. Burn-in or mux subtitles.
        4. Encode to H.264 + AAC.

        Args:
            video_clips: List of paths to video clip files.
            audio: Path to the narration audio file.
            subtitles: Path to the SRT subtitle file.
            bgm: Path to the background music file.
            output_path: Destination path for the final video.
            width: Output width in pixels.
            height: Output height in pixels.
            fps: Output frame rate.
            bgm_volume: BGM volume relative to narration (0.0 - 1.0).
            **kwargs: Additional FFmpeg options.

        Returns:
            The output_path on success.
        """
        # TODO: implement FFmpeg-based composition pipeline
        raise NotImplementedError
