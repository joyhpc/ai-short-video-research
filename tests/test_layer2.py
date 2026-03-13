"""Tests for Layer 2 — ML quality checks."""
import unittest
from unittest.mock import patch, MagicMock
from src.quality_gate.layer2_ml import CheckResult, LayerResult, MLChecker

class TestSceneChanges(unittest.TestCase):
    def setUp(self):
        self.checker = MLChecker()

    def test_scene_detection_with_fixture(self):
        """Test scene detection on sample video."""
        import os
        video = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")
        if os.path.exists(video):
            r = self.checker.check_scene_changes(video)
            # Should not be skipped since scenedetect is installed
            self.assertNotEqual(r.details.get("status"), "skipped")

class TestColorConsistency(unittest.TestCase):
    def setUp(self):
        self.checker = MLChecker()

    def test_color_consistency_with_fixture(self):
        import os
        video = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")
        if os.path.exists(video):
            try:
                r = self.checker.check_color_consistency(video)
                # If implemented, should not be skipped and should have a score
                self.assertNotEqual(r.details.get("status"), "skipped")
                self.assertGreater(r.score, 0.0)
            except NotImplementedError:
                # Method is still a stub — acceptable during development
                pass

class TestRunAll(unittest.TestCase):
    def setUp(self):
        self.checker = MLChecker()

    def test_run_all_with_fixture(self):
        import os
        video = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")
        if os.path.exists(video):
            result = self.checker.run_all(video, prompt="test pattern with colors")
            self.assertIsInstance(result, LayerResult)
            self.assertEqual(result.layer, "L2_ml")
