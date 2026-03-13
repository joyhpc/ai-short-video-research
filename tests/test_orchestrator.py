"""Tests for pipeline orchestrator — evaluate-only and retry loop."""
import unittest
from unittest.mock import patch, MagicMock
from src.pipeline.orchestrator import VideoOrchestrator, VideoState, OrchestratorResult
from src.quality_gate import QualityResult
from src.quality_gate.layer1_programmatic import CheckResult as L1Check, LayerResult as L1Result
from src.quality_gate.layer2_ml import CheckResult as L2Check, LayerResult as L2Result
from src.quality_gate.aggregator import Decision


class TestEvaluateVideo(unittest.TestCase):
    """Test evaluate-only mode."""

    @patch("src.pipeline.orchestrator.qa_evaluate")
    def test_passing_video(self, mock_eval):
        """A passing video should return success=True."""
        mock_eval.return_value = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            l2_result=L2Result(checks=[L2Check("visual_quality", True, 0.8)], passed=True, score=0.8),
            decision=Decision(verdict="pass", confidence=0.9, reasons=["L2 weighted score: 0.80"]),
            layers_run=["L1_programmatic", "L2_ml"],
        )
        result = VideoOrchestrator.evaluate_video("test.mp4", prompt="test")
        self.assertTrue(result.success)
        self.assertIsNone(result.diagnosis)

    @patch("src.pipeline.orchestrator.qa_evaluate")
    def test_failing_video_produces_diagnosis(self, mock_eval):
        """A failing video should produce a diagnosis."""
        mock_eval.return_value = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(
                checks=[L1Check("file_integrity", False, 0.0, {"error": "corrupt"})],
                passed=False, score=0.0,
            ),
            decision=Decision(verdict="fail", confidence=0.95, reasons=["L1 hard-gate failed"]),
            layers_run=["L1_programmatic"],
        )
        result = VideoOrchestrator.evaluate_video("test.mp4")
        self.assertFalse(result.success)
        self.assertIsNotNone(result.diagnosis)


class TestReportGeneration(unittest.TestCase):
    """Test JSON report output."""

    def test_report_structure(self):
        """Report should contain expected keys."""
        result = OrchestratorResult(
            video_path="test.mp4",
            prompt="test prompt",
            decision=Decision(verdict="pass", confidence=0.9, reasons=["good"]),
            success=True,
            retries_used=0,
        )
        report = result.to_report()
        self.assertIn("video_path", report)
        self.assertIn("success", report)
        self.assertIn("decision", report)
        self.assertEqual(report["decision"]["verdict"], "pass")


class TestRetryLoop(unittest.TestCase):
    """Test the generate -> evaluate -> correct retry loop."""

    @patch("src.pipeline.orchestrator.qa_evaluate")
    def test_evaluate_only_no_retries(self, mock_eval):
        """Evaluate-only mode with a passing video should not retry."""
        mock_eval.return_value = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            decision=Decision(verdict="pass", confidence=0.9),
            layers_run=["L1_programmatic"],
        )
        orch = VideoOrchestrator()
        result = orch.run("test prompt", video_path="test.mp4", max_retries=3)
        self.assertTrue(result.success)
        self.assertEqual(result.retries_used, 0)

    @patch("src.pipeline.orchestrator.qa_evaluate")
    def test_retry_budget_exhaustion(self, mock_eval):
        """Should stop after max_retries even if still failing."""
        mock_eval.return_value = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(
                checks=[L1Check("file_integrity", True, 1.0)],
                passed=True, score=1.0,
            ),
            l2_result=L2Result(
                checks=[L2Check("text_alignment", False, 0.3)],
                passed=False, score=0.3,
            ),
            decision=Decision(verdict="fail", confidence=0.7, reasons=["L2 low"]),
            layers_run=["L1_programmatic", "L2_ml"],
        )
        orch = VideoOrchestrator()
        result = orch.run("test prompt", video_path="test.mp4", max_retries=2)
        self.assertFalse(result.success)
        # Should have used retries (retry_count goes 0, 1, 2 = 3 evaluations)
        self.assertLessEqual(result.retries_used, 3)

    @patch("src.pipeline.orchestrator.qa_evaluate")
    def test_generator_callable(self, mock_eval):
        """Should call generator function when provided."""
        mock_generator = MagicMock(return_value="generated.mp4")
        mock_eval.return_value = QualityResult(
            video_path="generated.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            decision=Decision(verdict="pass", confidence=0.9),
            layers_run=["L1_programmatic"],
        )
        orch = VideoOrchestrator()
        result = orch.run("test prompt", generator=mock_generator, max_retries=1)
        self.assertTrue(result.success)
        mock_generator.assert_called_once()
