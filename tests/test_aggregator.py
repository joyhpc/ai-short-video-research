"""Tests for quality score aggregation and decision logic."""
import unittest
from src.quality_gate.layer1_programmatic import CheckResult as L1Check, LayerResult as L1Result
from src.quality_gate.layer2_ml import CheckResult as L2Check, LayerResult as L2Result
from src.quality_gate.layer3_vlm import VLMResult
from src.quality_gate.aggregator import QualityAggregator, Decision

class TestDecision(unittest.TestCase):
    def setUp(self):
        self.agg = QualityAggregator()

    def test_l1_fail_means_fail(self):
        l1 = L1Result(checks=[L1Check("file_integrity", False, 0.0)], passed=False)
        d = self.agg.decide(l1, None, None)
        self.assertEqual(d.verdict, "fail")

    def test_l1_pass_l2_high_means_pass(self):
        l1 = L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True)
        l2 = L2Result(checks=[
            L2Check("visual_quality", True, 0.85),
            L2Check("text_alignment", True, 0.80),
        ], passed=True, score=0.82)
        d = self.agg.decide(l1, l2, None)
        self.assertEqual(d.verdict, "pass")

    def test_l2_low_means_fail(self):
        l1 = L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True)
        l2 = L2Result(checks=[
            L2Check("visual_quality", False, 0.3),
            L2Check("text_alignment", False, 0.2),
        ], passed=False, score=0.25)
        d = self.agg.decide(l1, l2, None)
        self.assertEqual(d.verdict, "fail")

    def test_l2_borderline_means_review(self):
        l1 = L1Result(checks=[L1Check("file_integrity", True, 1.0)], passed=True)
        l2 = L2Result(checks=[
            L2Check("visual_quality", True, 0.6),
            L2Check("text_alignment", True, 0.55),
        ], passed=True, score=0.58)
        d = self.agg.decide(l1, l2, None)
        self.assertEqual(d.verdict, "review")

    def test_no_layers_means_escalate(self):
        d = self.agg.decide(None, None, None)
        self.assertEqual(d.verdict, "escalate")
