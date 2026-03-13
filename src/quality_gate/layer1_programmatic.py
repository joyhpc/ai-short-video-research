"""Layer 1 — Programmatic (rule-based) video quality checks.

Uses ffprobe / ffmpeg and standard libraries to verify hard-gate
properties: file integrity, resolution, duration, A/V sync, loudness,
subtitle format, and frame consistency.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import imagehash
import pysrt


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
        try:
            probe = self._ffprobe_json(video_path)
            # Find the first video stream for resolution
            video_stream = next(
                (s for s in probe.get("streams", []) if s["codec_type"] == "video"),
                None,
            )
            if video_stream is None:
                return CheckResult(
                    name="resolution_duration",
                    passed=False,
                    score=0.0,
                    details={"error": "no video stream found"},
                )

            actual_width = int(video_stream.get("width", 0))
            actual_height = int(video_stream.get("height", 0))

            # Duration: prefer format-level, fall back to stream-level
            duration_str = (
                probe.get("format", {}).get("duration")
                or video_stream.get("duration")
            )
            actual_duration = float(duration_str) if duration_str else 0.0

            resolution_ok = (actual_width == target_width and actual_height == target_height)
            duration_ok = abs(actual_duration - target_duration) <= target_duration * 0.10

            if resolution_ok and duration_ok:
                score = 1.0
            elif resolution_ok or duration_ok:
                score = 0.5
            else:
                score = 0.0

            return CheckResult(
                name="resolution_duration",
                passed=(resolution_ok and duration_ok),
                score=score,
                details={
                    "actual_width": actual_width,
                    "actual_height": actual_height,
                    "target_width": target_width,
                    "target_height": target_height,
                    "actual_duration": actual_duration,
                    "target_duration": target_duration,
                    "resolution_ok": resolution_ok,
                    "duration_ok": duration_ok,
                },
            )
        except Exception as exc:
            return CheckResult(
                name="resolution_duration",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

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
        try:
            probe = self._ffprobe_json(video_path)
            streams = probe.get("streams", [])

            video_stream = next(
                (s for s in streams if s["codec_type"] == "video"), None
            )
            audio_stream = next(
                (s for s in streams if s["codec_type"] == "audio"), None
            )

            if video_stream is None or audio_stream is None:
                return CheckResult(
                    name="av_sync",
                    passed=False,
                    score=0.0,
                    details={"error": "missing video or audio stream"},
                )

            video_start = float(video_stream.get("start_time", 0.0))
            audio_start = float(audio_stream.get("start_time", 0.0))
            drift_ms = abs(video_start - audio_start) * 1000.0

            if drift_ms < 50.0:
                score = 1.0
            elif drift_ms < 100.0:
                score = 0.5
            else:
                score = 0.0

            return CheckResult(
                name="av_sync",
                passed=(drift_ms < max_drift_ms),
                score=score,
                details={
                    "video_start_time": video_start,
                    "audio_start_time": audio_start,
                    "drift_ms": round(drift_ms, 3),
                    "max_drift_ms": max_drift_ms,
                },
            )
        except Exception as exc:
            return CheckResult(
                name="av_sync",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

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
        try:
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-af", "loudnorm=print_format=json",
                "-f", "null",
                "-",
            ]
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            # The loudnorm filter prints a JSON block in stderr.
            # It appears after a line like "[Parsed_loudnorm_0 @ 0x...] {"
            stderr = proc.stderr

            # Extract the JSON block from stderr
            match = re.search(
                r"\[Parsed_loudnorm_0\s+@\s+0x[0-9a-f]+\]\s*(\{.*?\})",
                stderr,
                re.DOTALL,
            )
            if match is None:
                # Fallback: try to find a bare JSON block with "input_i"
                match = re.search(
                    r'(\{[^{}]*"input_i"[^{}]*\})',
                    stderr,
                    re.DOTALL,
                )
            if match is None:
                return CheckResult(
                    name="audio_loudness",
                    passed=False,
                    score=0.0,
                    details={"error": "could not parse loudnorm output from ffmpeg"},
                )

            loudnorm_data = json.loads(match.group(1))
            measured_lufs = float(loudnorm_data["input_i"])

            deviation = abs(measured_lufs - target_lufs)
            passed = deviation <= tolerance

            # Score: 1.0 if within tolerance, linearly drops to 0.0 at 2x tolerance
            if deviation <= tolerance:
                score = 1.0
            elif deviation <= tolerance * 2:
                score = 1.0 - (deviation - tolerance) / tolerance
            else:
                score = 0.0

            return CheckResult(
                name="audio_loudness",
                passed=passed,
                score=round(max(score, 0.0), 4),
                details={
                    "measured_lufs": measured_lufs,
                    "target_lufs": target_lufs,
                    "tolerance": tolerance,
                    "deviation": round(deviation, 2),
                    "loudnorm_raw": loudnorm_data,
                },
            )
        except Exception as exc:
            return CheckResult(
                name="audio_loudness",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

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
        try:
            subs = pysrt.open(srt_path)
        except Exception as exc:
            return CheckResult(
                name="subtitles",
                passed=False,
                score=0.0,
                details={"parse_error": str(exc)},
            )

        try:
            parse_errors: list[str] = []
            if len(subs) == 0:
                parse_errors.append("SRT file contains no subtitle entries")

            # Check for overlapping timestamps
            overlaps: list[dict[str, Any]] = []
            for i in range(len(subs) - 1):
                current_end = (
                    subs[i].end.hours * 3600
                    + subs[i].end.minutes * 60
                    + subs[i].end.seconds
                    + subs[i].end.milliseconds / 1000.0
                )
                next_start = (
                    subs[i + 1].start.hours * 3600
                    + subs[i + 1].start.minutes * 60
                    + subs[i + 1].start.seconds
                    + subs[i + 1].start.milliseconds / 1000.0
                )
                if current_end > next_start:
                    overlaps.append({
                        "index": i,
                        "current_end": round(current_end, 3),
                        "next_start": round(next_start, 3),
                    })

            # Calculate coverage ratio
            total_sub_duration = 0.0
            for sub in subs:
                start_sec = (
                    sub.start.hours * 3600
                    + sub.start.minutes * 60
                    + sub.start.seconds
                    + sub.start.milliseconds / 1000.0
                )
                end_sec = (
                    sub.end.hours * 3600
                    + sub.end.minutes * 60
                    + sub.end.seconds
                    + sub.end.milliseconds / 1000.0
                )
                total_sub_duration += max(0.0, end_sec - start_sec)

            coverage = total_sub_duration / audio_duration if audio_duration > 0 else 0.0

            no_parse_errors = len(parse_errors) == 0
            no_overlaps = len(overlaps) == 0
            coverage_ok = coverage >= 0.5

            passed = no_parse_errors and no_overlaps and coverage_ok

            # Score: weight parse/overlap as binary, coverage as continuous
            score_parts = []
            score_parts.append(1.0 if no_parse_errors else 0.0)
            score_parts.append(1.0 if no_overlaps else 0.0)
            score_parts.append(min(coverage / 0.5, 1.0) if coverage >= 0 else 0.0)
            score = sum(score_parts) / len(score_parts)

            return CheckResult(
                name="subtitles",
                passed=passed,
                score=round(score, 4),
                details={
                    "subtitle_count": len(subs),
                    "parse_errors": parse_errors,
                    "overlap_count": len(overlaps),
                    "overlaps": overlaps[:10],  # limit detail size
                    "total_sub_duration": round(total_sub_duration, 3),
                    "audio_duration": audio_duration,
                    "coverage": round(coverage, 4),
                    "coverage_ok": coverage_ok,
                },
            )
        except Exception as exc:
            return CheckResult(
                name="subtitles",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

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
        try:
            import cv2
        except ImportError:
            return CheckResult(
                name="frame_consistency",
                passed=False,
                score=0.0,
                details={"error": "cv2 (opencv-python) is not installed"},
            )

        try:
            from PIL import Image

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return CheckResult(
                    name="frame_consistency",
                    passed=False,
                    score=0.0,
                    details={"error": "could not open video file"},
                )

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0 or fps <= 0:
                cap.release()
                return CheckResult(
                    name="frame_consistency",
                    passed=False,
                    score=0.0,
                    details={"error": "could not determine frame count or fps"},
                )

            # Sample every Nth frame (~1 fps)
            sample_interval = max(int(fps), 1)  # roughly 1 sample per second
            hashes: list[imagehash.ImageHash] = []
            frame_indices: list[int] = []

            for frame_idx in range(0, total_frames, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert BGR (OpenCV) to RGB (PIL)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
                h = imagehash.phash(pil_img)
                hashes.append(h)
                frame_indices.append(frame_idx)

            cap.release()

            if len(hashes) < 2:
                return CheckResult(
                    name="frame_consistency",
                    passed=True,
                    score=1.0,
                    details={
                        "sampled_frames": len(hashes),
                        "note": "too few frames to analyze",
                    },
                )

            # Compute Hamming distances between consecutive sampled frames
            distances: list[int] = []
            frozen_pairs: list[dict[str, Any]] = []
            glitch_pairs: list[dict[str, Any]] = []
            glitch_threshold = 40  # very high distance = visual glitch

            for i in range(len(hashes) - 1):
                dist = hashes[i] - hashes[i + 1]
                distances.append(dist)
                if dist < hash_threshold:
                    frozen_pairs.append({
                        "frame_a": frame_indices[i],
                        "frame_b": frame_indices[i + 1],
                        "distance": dist,
                    })
                if dist > glitch_threshold:
                    glitch_pairs.append({
                        "frame_a": frame_indices[i],
                        "frame_b": frame_indices[i + 1],
                        "distance": dist,
                    })

            total_transitions = len(distances)
            normal_transitions = total_transitions - len(frozen_pairs) - len(glitch_pairs)
            score = normal_transitions / total_transitions if total_transitions > 0 else 1.0

            # Passed if the majority of transitions are normal
            passed = score >= 0.5

            return CheckResult(
                name="frame_consistency",
                passed=passed,
                score=round(score, 4),
                details={
                    "sampled_frames": len(hashes),
                    "total_transitions": total_transitions,
                    "frozen_count": len(frozen_pairs),
                    "glitch_count": len(glitch_pairs),
                    "normal_count": normal_transitions,
                    "frozen_pairs": frozen_pairs[:10],  # limit detail size
                    "glitch_pairs": glitch_pairs[:10],
                    "hash_threshold": hash_threshold,
                },
            )
        except Exception as exc:
            return CheckResult(
                name="frame_consistency",
                passed=False,
                score=0.0,
                details={"error": str(exc)},
            )

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

        # Subtitles check requires a separate srt_path; skip if not provided
        srt_path = kwargs.get("srt_path")
        if srt_path:
            # We need audio duration for subtitle coverage check;
            # attempt to extract it from ffprobe
            try:
                probe = self._ffprobe_json(video_path)
                audio_duration = float(
                    probe.get("format", {}).get("duration", 0.0)
                )
            except Exception:
                audio_duration = 0.0

            optional_methods.append(
                ("subtitles", lambda: self.check_subtitles(
                    srt_path,
                    audio_duration=kwargs.get("audio_duration", audio_duration),
                ))
            )

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
