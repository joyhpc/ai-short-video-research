"""Tests for correction module — diagnosis and prompt rewriting."""
import unittest
from src.quality_gate.layer1_programmatic import CheckResult as L1Check, LayerResult as L1Result
from src.quality_gate.layer2_ml import CheckResult as L2Check, LayerResult as L2Result
from src.quality_gate import QualityResult
from src.correction.diagnosis import ProblemDiagnoser, ProblemType, Diagnosis
from src.correction.prompt_rewriter import PromptRewriter, RewriteResult


class TestProblemDiagnoser(unittest.TestCase):
    def setUp(self):
        self.diagnoser = ProblemDiagnoser()

    def test_l1_technical_failure(self):
        """L1 file_integrity failure should be diagnosed as TECHNICAL."""
        qr = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(
                checks=[L1Check("file_integrity", False, 0.0, {"error": "corrupt"})],
                passed=False, score=0.0,
            ),
        )
        d = self.diagnoser.diagnose(qr)
        self.assertEqual(d.problem_type, ProblemType.TECHNICAL)
        self.assertEqual(d.severity, "critical")

    def test_l2_alignment_failure(self):
        """L2 text_alignment failure should be diagnosed as ALIGNMENT."""
        qr = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            l2_result=L2Result(
                checks=[
                    L2Check("text_alignment", False, 0.2, {}),
                    L2Check("color_consistency", True, 0.8, {}),
                ],
                passed=False, score=0.4,
            ),
        )
        d = self.diagnoser.diagnose(qr)
        self.assertEqual(d.problem_type, ProblemType.ALIGNMENT)

    def test_l2_coherence_failure(self):
        """L2 temporal_consistency failure should be diagnosed as COHERENCE."""
        qr = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            l2_result=L2Result(
                checks=[
                    L2Check("temporal_consistency", False, 0.3, {}),
                    L2Check("text_alignment", True, 0.7, {}),
                ],
                passed=False, score=0.5,
            ),
        )
        d = self.diagnoser.diagnose(qr)
        self.assertEqual(d.problem_type, ProblemType.COHERENCE)

    def test_no_failures_returns_minor(self):
        """All checks passing should return a minor diagnosis."""
        qr = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            l2_result=L2Result(checks=[L2Check("visual_quality", True, 0.8)], passed=True, score=0.8),
        )
        d = self.diagnoser.diagnose(qr)
        self.assertEqual(d.severity, "minor")

    def test_multiple_failures_picks_worst(self):
        """With multiple failures, should pick the lowest-scoring one."""
        qr = QualityResult(
            video_path="test.mp4",
            l1_result=L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True, score=1.0),
            l2_result=L2Result(
                checks=[
                    L2Check("text_alignment", False, 0.4, {}),
                    L2Check("color_consistency", False, 0.1, {}),  # worst
                ],
                passed=False, score=0.25,
            ),
        )
        d = self.diagnoser.diagnose(qr)
        self.assertEqual(d.details["worst_check"], "color_consistency")


class TestPromptRewriter(unittest.TestCase):
    def setUp(self):
        self.rewriter = PromptRewriter()

    def test_alignment_rewrite(self):
        """ALIGNMENT diagnosis should add alignment modifiers."""
        d = Diagnosis(
            problem_type=ProblemType.ALIGNMENT,
            severity="major",
            description="text_alignment scored 0.2",
            suggested_fix_strategy="Rewrite prompt",
        )
        result = self.rewriter.rewrite("a cat playing piano", d)
        self.assertIsInstance(result, RewriteResult)
        self.assertNotEqual(result.rewritten_prompt, "a cat playing piano")
        self.assertGreater(len(result.changes), 0)

    def test_aesthetic_rewrite(self):
        """AESTHETIC diagnosis should add aesthetic modifiers."""
        d = Diagnosis(
            problem_type=ProblemType.AESTHETIC,
            severity="major",
            description="visual quality low",
            suggested_fix_strategy="Adjust style",
        )
        result = self.rewriter.rewrite("sunset beach scene", d)
        self.assertIn("cinematic", result.rewritten_prompt.lower())

    def test_vlm_critique_incorporated(self):
        """VLM critique should be incorporated into the rewrite."""
        d = Diagnosis(
            problem_type=ProblemType.ALIGNMENT,
            severity="major",
            description="alignment failure",
            suggested_fix_strategy="Rewrite",
        )
        result = self.rewriter.rewrite(
            "a cat playing piano",
            d,
            vlm_critique="The video shows a dog instead of a cat",
        )
        self.assertIn("reviewer feedback", result.rewritten_prompt.lower())
        self.assertGreaterEqual(result.confidence, 0.5)

    def test_original_prompt_preserved_in_result(self):
        """Original prompt should be stored in result."""
        d = Diagnosis(
            problem_type=ProblemType.TECHNICAL,
            severity="minor",
            description="minor issue",
            suggested_fix_strategy="Re-encode",
        )
        result = self.rewriter.rewrite("original prompt here", d)
        self.assertEqual(result.original_prompt, "original prompt here")
