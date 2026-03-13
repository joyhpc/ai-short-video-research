"""Tests for Layer 1 — Programmatic quality checks."""
import unittest
from unittest.mock import patch, MagicMock
from src.quality_gate.layer1_programmatic import CheckResult, LayerResult, ProgrammaticChecker

class TestFileIntegrity(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_valid_file(self, mock):
        mock.return_value = {"streams": [{"codec_type": "video"}, {"codec_type": "audio"}], "format": {"duration": "60.0"}}
        r = self.checker.check_file_integrity("test.mp4")
        self.assertTrue(r.passed)

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_corrupt_file(self, mock):
        mock.side_effect = RuntimeError("fail")
        r = self.checker.check_file_integrity("test.mp4")
        self.assertFalse(r.passed)

class TestResolutionDuration(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_matching_resolution(self, mock):
        mock.return_value = {
            "streams": [{"codec_type": "video", "width": 1080, "height": 1920}],
            "format": {"duration": "60.0"}
        }
        r = self.checker.check_resolution_duration("test.mp4", 1080, 1920, 60.0)
        self.assertTrue(r.passed)
        self.assertEqual(r.score, 1.0)

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_wrong_resolution(self, mock):
        mock.return_value = {
            "streams": [{"codec_type": "video", "width": 720, "height": 1280}],
            "format": {"duration": "60.0"}
        }
        r = self.checker.check_resolution_duration("test.mp4", 1080, 1920, 60.0)
        # Should fail or have lower score
        self.assertLessEqual(r.score, 0.5)

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_duration_within_tolerance(self, mock):
        mock.return_value = {
            "streams": [{"codec_type": "video", "width": 1080, "height": 1920}],
            "format": {"duration": "63.0"}  # within 10% of 60
        }
        r = self.checker.check_resolution_duration("test.mp4", 1080, 1920, 60.0)
        self.assertTrue(r.passed)

class TestAVSync(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_good_sync(self, mock):
        mock.return_value = {
            "streams": [
                {"codec_type": "video", "start_time": "0.000000"},
                {"codec_type": "audio", "start_time": "0.020000"}
            ]
        }
        r = self.checker.check_av_sync("test.mp4", max_drift_ms=100.0)
        self.assertTrue(r.passed)

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_bad_sync(self, mock):
        mock.return_value = {
            "streams": [
                {"codec_type": "video", "start_time": "0.000000"},
                {"codec_type": "audio", "start_time": "0.500000"}
            ]
        }
        r = self.checker.check_av_sync("test.mp4", max_drift_ms=100.0)
        self.assertFalse(r.passed)

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_no_audio_stream(self, mock):
        mock.return_value = {"streams": [{"codec_type": "video", "start_time": "0.0"}]}
        r = self.checker.check_av_sync("test.mp4")
        # Should handle gracefully
        self.assertFalse(r.passed)

class TestAudioLoudness(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    @patch("subprocess.run")
    def test_good_loudness(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr='[Parsed_loudnorm_0 @ 0x1234] {\n"input_i": "-23.5"\n}'
        )
        r = self.checker.check_audio_loudness("test.mp4", target_lufs=-23.0, tolerance=2.0)
        self.assertTrue(r.passed)

class TestRunAll(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    @patch.object(ProgrammaticChecker, "_ffprobe_json")
    def test_run_all_returns_layer_result(self, mock):
        mock.return_value = {
            "streams": [
                {"codec_type": "video", "width": 1080, "height": 1920, "start_time": "0.0"},
                {"codec_type": "audio", "start_time": "0.0", "sample_rate": "44100"}
            ],
            "format": {"duration": "60.0"}
        }
        result = self.checker.run_all("test.mp4")
        self.assertIsInstance(result, LayerResult)
        self.assertEqual(result.layer, "L1_programmatic")
        self.assertGreater(len(result.checks), 0)

class TestSubtitles(unittest.TestCase):
    def setUp(self):
        self.checker = ProgrammaticChecker()

    def test_valid_srt(self):
        # Use the actual test fixture
        import os
        srt_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample.srt")
        if os.path.exists(srt_path):
            r = self.checker.check_subtitles(srt_path, audio_duration=5.0)
            self.assertTrue(r.passed)
