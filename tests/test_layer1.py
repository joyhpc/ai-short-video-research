"""Tests for Layer 1 — Programmatic quality checks."""

from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from src.quality_gate.layer1_programmatic import (
    CheckResult,
    LayerResult,
    ProgrammaticChecker,
)


class TestProgrammaticChecker(unittest.TestCase):
    """Unit tests for ProgrammaticChecker."""

    def setUp(self) -> None:
        self.checker = ProgrammaticChecker()
        self.sample_video = "tests/fixtures/sample.mp4"

    # -- file integrity ------------------------------------------------------

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_file_integrity_valid(self, mock_ffprobe: MagicMock) -> None:
        """A valid file with video+audio streams should pass."""
        mock_ffprobe.return_value = {
            "streams": [
                {"codec_type": "video", "width": 1080, "height": 1920},
                {"codec_type": "audio", "sample_rate": "44100"},
            ],
            "format": {"duration": "60.0"},
        }
        result = self.checker.check_file_integrity(self.sample_video)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.details["has_video"])
        self.assertTrue(result.details["has_audio"])

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_file_integrity_corrupt(self, mock_ffprobe: MagicMock) -> None:
        """A corrupt file (ffprobe raises) should fail."""
        mock_ffprobe.side_effect = RuntimeError("ffprobe failed")
        result = self.checker.check_file_integrity(self.sample_video)
        self.assertFalse(result.passed)
        self.assertEqual(result.score, 0.0)
        self.assertIn("error", result.details)

    # -- resolution check ----------------------------------------------------

    def test_resolution_check_not_implemented(self) -> None:
        """Resolution check should raise NotImplementedError in stub phase."""
        with self.assertRaises(NotImplementedError):
            self.checker.check_resolution_duration(
                self.sample_video,
                target_width=1080,
                target_height=1920,
                target_duration=60.0,
            )

    # -- A/V sync ------------------------------------------------------------

    def test_av_sync_not_implemented(self) -> None:
        """A/V sync check should raise NotImplementedError in stub phase."""
        with self.assertRaises(NotImplementedError):
            self.checker.check_av_sync(self.sample_video, max_drift_ms=100.0)

    # -- audio loudness ------------------------------------------------------

    def test_audio_loudness_not_implemented(self) -> None:
        """Audio loudness check should raise NotImplementedError in stub phase."""
        with self.assertRaises(NotImplementedError):
            self.checker.check_audio_loudness(
                self.sample_video, target_lufs=-23.0, tolerance=2.0
            )

    # -- run_all -------------------------------------------------------------

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_run_all_returns_layer_result(self, mock_ffprobe: MagicMock) -> None:
        """run_all should return a LayerResult even when stubs raise."""
        mock_ffprobe.return_value = {
            "streams": [
                {"codec_type": "video", "width": 1080, "height": 1920},
                {"codec_type": "audio", "sample_rate": "44100"},
            ],
            "format": {"duration": "60.0"},
        }
        result = self.checker.run_all(self.sample_video)
        self.assertIsInstance(result, LayerResult)
        self.assertEqual(result.layer, "L1_programmatic")
        self.assertGreater(len(result.checks), 0)


if __name__ == "__main__":
    unittest.main()
