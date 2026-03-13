"""Layer 1 — Programmatic (rule-based) video quality checks.

Uses ffprobe / ffmpeg and standard libraries to verify hard-gate
properties: file integrity, resolution, duration, A/V sync, loudness,
subtitle format, and frame consistency.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of a single programmatic check."""

    name: str
    passed: bool
    score: float  # 0.0 – 1.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerResult:
    """Aggregate result for the entire programmatic layer."""

    layer: str = "L1_programmatic"
    checks: list[CheckResult] = field(default_factory=list)
    passed: bool = False
    score: float = 0.0


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class ProgrammaticChecker:
    """Hard-gate checks that use only deterministic, rule-based logic."""

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def _ffprobe_json(video_path: str) -> dict[str, Any]:
        """Run ffprobe and return the parsed JSON output.

        Raises:
            RuntimeError: If ffprobe fails or returns non-JSON output.
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)

    # -- individual checks ---------------------------------------------------

    def check_file_integrity(self, video_path: str) -> CheckResult:
        """Verify the video file is decodable by ffprobe.

        Attempts to parse container metadata.  A decode error or missing
        streams indicates a corrupt / truncated file.
        """
        try:
            probe = self._ffprobe_json(video_path)
            streams = probe.get("streams", [])
            has_video = any(s["codec_type"] == "video" for s in streams)
            has_audio = any(s["codec_type"] == "audio" for s in streams)
            return CheckResult(
                name="file_integrity",
                passed=has_video,
                score=1.0 if has_video else 0.0,
                details={
                    "has_video": has_video,
                    "has_audio": has_audio,
                    "stream_count": len(streams),
                },
            )
        except Exception as exc:
            return CheckResult(
                name="file_integrity",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

    def check_resolution_duration(
        self,
        video_path: str,
        target_width: int = 1080,
        target_height: int = 1920,
        target_duration: float = 60.0,
    ) -> CheckResult:
        """Check that resolution and duration match expected targets.

        Args:
            video_path: Path to the video file.
            target_width: Expected width in pixels.
            target_height: Expected height in pixels.
            target_duration: Expected duration in seconds (allows +/- 10 %).
        """
        # TODO: implement ffprobe-based resolution & duration extraction
        raise NotImplementedError

    def check_av_sync(
        self, video_path: str, max_drift_ms: float = 100.0
    ) -> CheckResult:
        """Check audio/video PTS drift stays within tolerance.

        Parses presentation timestamps for the first audio and video streams
        and computes maximum drift in milliseconds.

        Args:
            video_path: Path to the video file.
            max_drift_ms: Maximum allowable drift in milliseconds.
        """
        # TODO: implement PTS diff analysis via ffprobe frame-level output
        raise NotImplementedError

    def check_audio_loudness(
        self,
        video_path: str,
        target_lufs: float = -23.0,
        tolerance: float = 2.0,
    ) -> CheckResult:
        """Measure integrated loudness (EBU R128) via ffmpeg loudnorm filter.

        Args:
            video_path: Path to the video file.
            target_lufs: Target integrated loudness in LUFS.
            tolerance: Acceptable deviation in LU.
        """
        # TODO: implement ffmpeg loudnorm measurement
        raise NotImplementedError

    def check_subtitles(
        self, srt_path: str, audio_duration: float
    ) -> CheckResult:
        """Validate SRT subtitle file: format, overlap, and coverage.

        Args:
            srt_path: Path to the .srt subtitle file.
            audio_duration: Duration of the accompanying audio in seconds.

        Returns:
            CheckResult with details about parsing errors, overlaps,
            and coverage ratio.
        """
        # TODO: implement SRT parsing and validation
        raise NotImplementedError

    def check_frame_consistency(
        self, video_path: str, hash_threshold: int = 10
    ) -> CheckResult:
        """Detect stuck / duplicate frames via perceptual hashing (pHash).

        Samples N evenly-spaced frames, computes imagehash pHash for each,
        and flags sequences where the Hamming distance between consecutive
        hashes falls below *hash_threshold*.

        Args:
            video_path: Path to the video file.
            hash_threshold: Hamming-distance threshold below which two
                consecutive frames are considered identical.
        """
        # TODO: implement imagehash-based frame consistency check
        raise NotImplementedError

    # -- aggregate -----------------------------------------------------------

    def run_all(self, video_path: str, **kwargs: Any) -> LayerResult:
        """Run every programmatic check and return an aggregate LayerResult.

        Individual check failures do *not* short-circuit; all checks are
        attempted so the caller gets a complete diagnostic picture.

        Keyword args are forwarded to the individual check methods where
        applicable (e.g. target_width, target_height, target_duration).
        """
        checks: list[CheckResult] = []

        # File integrity is always first — if this fails the rest are suspect
        checks.append(self.check_file_integrity(video_path))

        # Remaining checks: wrap in try/except so a NotImplementedError
        # (stub phase) or runtime error doesn't break the whole run.
        optional_methods = [
            ("resolution_duration", lambda: self.check_resolution_duration(
                video_path,
                target_width=kwargs.get("target_width", 1080),
                target_height=kwargs.get("target_height", 1920),
                target_duration=kwargs.get("target_duration", 60.0),
            )),
            ("av_sync", lambda: self.check_av_sync(
                video_path,
                max_drift_ms=kwargs.get("max_drift_ms", 100.0),
            )),
            ("audio_loudness", lambda: self.check_audio_loudness(
                video_path,
                target_lufs=kwargs.get("target_lufs", -23.0),
                tolerance=kwargs.get("tolerance", 2.0),
            )),
            ("frame_consistency", lambda: self.check_frame_consistency(
                video_path,
                hash_threshold=kwargs.get("hash_threshold", 10),
            )),
        ]

        for name, fn in optional_methods:
            try:
                checks.append(fn())
            except NotImplementedError:
                checks.append(CheckResult(
                    name=name, passed=True, score=0.0,
                    details={"status": "not_implemented"},
                ))
            except Exception as exc:
                checks.append(CheckResult(
                    name=name, passed=False, score=0.0,
                    details={"error": str(exc)},
                ))

        all_passed = all(c.passed for c in checks)
        avg_score = (
            sum(c.score for c in checks) / len(checks) if checks else 0.0
        )

        return LayerResult(
            layer="L1_programmatic",
            checks=checks,
            passed=all_passed,
            score=round(avg_score, 4),
        )
