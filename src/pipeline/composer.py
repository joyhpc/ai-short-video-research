"""Video composer — assemble video clips, audio, subtitles, and BGM into a final video."""

from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


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

    Uses FFmpeg (via subprocess) to combine video clips,
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
        if not video_clips:
            raise ValueError("At least one video clip is required.")

        # Create parent directories for output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # --- Determine what inputs and filters we need ---
        has_bgm = bool(bgm)
        has_subtitles = bool(subtitles) and Path(subtitles).is_file()
        needs_concat = len(video_clips) > 1

        # --- Build FFmpeg command with a complex filter graph ---
        cmd: list[str] = ["ffmpeg", "-y"]

        # Input 0: video (either concat demuxer or single file)
        concat_file: Optional[str] = None
        if needs_concat:
            concat_file = self._build_concat_file(video_clips)
            cmd.extend(["-f", "concat", "-safe", "0", "-i", concat_file])
        else:
            cmd.extend(["-i", video_clips[0]])

        # Input 1: narration audio
        cmd.extend(["-i", audio])

        # Input 2 (optional): BGM
        if has_bgm:
            cmd.extend(["-i", bgm])

        # --- Build filter graph ---
        filter_parts: list[str] = []
        video_label = "[0:v]"
        audio_label: str

        # Video filter: scale + pad to target resolution
        scale_filter = (
            f"scale={width}:{height}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        )

        # Subtitle burn-in: chain with scale using comma
        if has_subtitles:
            # Escape special characters in the subtitle path for FFmpeg
            escaped_srt = subtitles.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            video_filter = f"{video_label}{scale_filter},subtitles='{escaped_srt}'[vout]"
        else:
            video_filter = f"{video_label}{scale_filter}[vout]"
        filter_parts.append(video_filter)

        # Audio mixing
        if has_bgm:
            # Narration is input 1, BGM is input 2
            # Duck BGM to bgm_volume relative to narration
            # Get narration duration to trim BGM
            filter_parts.append(
                f"[2:a]volume={bgm_volume}[bgm_ducked]"
            )
            filter_parts.append(
                "[1:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            audio_label = "[aout]"
        else:
            audio_label = "[1:a]"
            # Pass narration through as-is (no filter needed, map directly)

        # --- Assemble the full command ---
        if has_bgm:
            # We have video + audio filters: use -filter_complex
            full_filter = ";".join(filter_parts)
            cmd.extend(["-filter_complex", full_filter])
            cmd.extend(["-map", "[vout]", "-map", audio_label])
        else:
            # Only video filters: use -filter_complex for consistency
            full_filter = ";".join(filter_parts)
            cmd.extend(["-filter_complex", full_filter])
            cmd.extend(["-map", "[vout]", "-map", "1:a"])

        # Encoding parameters
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(fps),
            "-shortest",
        ])

        cmd.append(output_path)

        # Run FFmpeg
        logger.info("Composing video: %d clips, audio=%s, bgm=%s, subs=%s",
                     len(video_clips), audio, bgm or "(none)", subtitles or "(none)")
        self._run_ffmpeg(cmd)

        # Clean up concat file
        if concat_file and os.path.exists(concat_file):
            try:
                os.unlink(concat_file)
            except OSError:
                pass

        logger.info("Composition complete: %s", output_path)
        return output_path

    def compose_from_spec(self, spec: CompositionSpec) -> str:
        """Convenience method that delegates to compose() using a CompositionSpec.

        Args:
            spec: A CompositionSpec dataclass with all composition parameters.

        Returns:
            The output path on success.
        """
        return self.compose(
            video_clips=spec.video_clips,
            audio=spec.audio_path,
            subtitles=spec.subtitle_path,
            bgm=spec.bgm_path,
            output_path=spec.output_path,
            width=spec.output_width,
            height=spec.output_height,
            fps=spec.fps,
            bgm_volume=spec.bgm_volume,
        )

    # -- helper methods --------------------------------------------------------

    def _build_concat_file(self, clips: list[str]) -> str:
        """Create a temporary concat demuxer file listing all clips.

        Args:
            clips: List of absolute or relative paths to video files.

        Returns:
            Path to the temporary concat list file.
        """
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="ffmpeg_concat_")
        try:
            with os.fdopen(fd, "w") as f:
                for clip in clips:
                    # FFmpeg concat demuxer requires escaped single quotes in paths
                    escaped = clip.replace("'", "'\\''")
                    f.write(f"file '{escaped}'\n")
        except Exception:
            os.close(fd)
            raise
        logger.debug("Created concat file: %s with %d entries", path, len(clips))
        return path

    def _get_duration(self, file_path: str) -> float:
        """Query the duration of a media file using ffprobe.

        Args:
            file_path: Path to the media file.

        Returns:
            Duration in seconds.

        Raises:
            RuntimeError: If ffprobe fails or cannot determine duration.
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            file_path,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            return duration
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"ffprobe failed for {file_path}: {exc.stderr}"
            ) from exc
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Could not parse duration from ffprobe output for {file_path}"
            ) from exc

    def _run_ffmpeg(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Run an FFmpeg command via subprocess with error handling.

        Args:
            cmd: The full FFmpeg command as a list of arguments.

        Returns:
            The completed process result.

        Raises:
            RuntimeError: If FFmpeg exits with a non-zero return code.
        """
        logger.debug("Running: %s", shlex.join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for long videos
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"FFmpeg timed out after 600 seconds: {shlex.join(cmd)}"
            ) from exc
        except FileNotFoundError as exc:
            raise RuntimeError(
                "FFmpeg not found. Ensure ffmpeg is installed and on PATH."
            ) from exc

        if result.returncode != 0:
            stderr_tail = result.stderr[-2000:] if result.stderr else "(no stderr)"
            raise RuntimeError(
                f"FFmpeg exited with code {result.returncode}.\n"
                f"Command: {shlex.join(cmd)}\n"
                f"stderr (last 2000 chars):\n{stderr_tail}"
            )

        return result
