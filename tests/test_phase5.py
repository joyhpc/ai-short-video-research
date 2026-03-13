"""Tests for Phase 5 — script generator, CLI, and server."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# ── Script Generator ──────────────────────────────────────────────
from src.pipeline.generators.script import (
    ScriptGenerator, VideoScript, Scene, SYSTEM_PROMPT,
)


class TestScene(unittest.TestCase):
    def test_scene_defaults(self):
        s = Scene(scene_number=1, narration="Hello", visual_description="A sunset")
        self.assertEqual(s.mood, "neutral")
        self.assertEqual(s.duration_hint, 5.0)


class TestVideoScript(unittest.TestCase):
    def test_from_json(self):
        data = {
            "title": "Test Video",
            "topic": "AI",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Welcome",
                    "visual_description": "Title card",
                    "mood": "inspiring",
                    "duration_hint": 5.0,
                },
                {
                    "scene_number": 2,
                    "narration": "Content",
                    "visual_description": "Content scene",
                    "mood": "calm",
                    "duration_hint": 10.0,
                },
            ],
        }
        script = VideoScript.from_json(data)
        self.assertEqual(script.title, "Test Video")
        self.assertEqual(len(script.scenes), 2)
        self.assertAlmostEqual(script.total_duration, 15.0)

    def test_to_prompt_list(self):
        script = VideoScript(
            title="T",
            topic="T",
            scenes=[
                Scene(1, "narr1", "vis1"),
                Scene(2, "narr2", "vis2"),
            ],
        )
        prompts = script.to_prompt_list()
        self.assertEqual(len(prompts), 2)
        self.assertEqual(prompts[0], ("narr1", "vis1"))

    def test_to_dict(self):
        script = VideoScript(title="T", topic="T", scenes=[])
        d = script.to_dict()
        self.assertIn("title", d)
        self.assertIn("scenes", d)

    def test_from_json_missing_fields(self):
        """Should handle missing optional fields gracefully."""
        data = {"scenes": [{"narration": "Hi"}]}
        script = VideoScript.from_json(data)
        self.assertEqual(len(script.scenes), 1)
        self.assertEqual(script.scenes[0].visual_description, "")
        self.assertEqual(script.title, "")


class TestScriptGenerator(unittest.TestCase):
    def test_fallback_generation(self):
        gen = ScriptGenerator(provider="fallback")
        script = gen.generate("测试主题", duration=30, num_scenes=4)
        self.assertIsInstance(script, VideoScript)
        self.assertEqual(len(script.scenes), 4)
        self.assertAlmostEqual(script.total_duration, 30.0)
        self.assertIn("测试主题", script.title)

    def test_auto_scene_count(self):
        gen = ScriptGenerator(provider="fallback")
        script = gen.generate("Topic", duration=60)
        self.assertEqual(len(script.scenes), 12)  # 60/5 = 12

    def test_auto_detect_fallback(self):
        """Without API keys, should auto-detect to fallback."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("OPENAI_API_KEY", "GOOGLE_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            gen = ScriptGenerator()
            self.assertEqual(gen.provider, "fallback")


# ── CLI ────────────────────────────────────────────────────────────
from src.cli import build_parser, cmd_script, cmd_evaluate


class TestCLIParser(unittest.TestCase):
    def test_script_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["script", "AI趋势", "--duration", "30"])
        self.assertEqual(args.command, "script")
        self.assertEqual(args.topic, "AI趋势")
        self.assertEqual(args.duration, 30.0)

    def test_evaluate_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["evaluate", "video.mp4", "--prompt", "test"])
        self.assertEqual(args.command, "evaluate")
        self.assertEqual(args.video, "video.mp4")
        self.assertEqual(args.prompt, "test")

    def test_generate_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["generate", "AI health", "--duration", "45", "--skip-eval"])
        self.assertEqual(args.command, "generate")
        self.assertEqual(args.topic, "AI health")
        self.assertTrue(args.skip_eval)

    def test_no_command_returns_zero(self):
        from src.cli import main
        with patch("sys.stdout"):
            ret = main([])
        self.assertEqual(ret, 0)


class TestCLIScript(unittest.TestCase):
    def test_script_to_stdout(self):
        """Script command should output JSON to stdout."""
        parser = build_parser()
        args = parser.parse_args(["script", "test", "--llm-provider", "fallback"])
        with patch("builtins.print") as mock_print:
            ret = cmd_script(args)
        self.assertEqual(ret, 0)
        # First print call should be valid JSON
        output = mock_print.call_args_list[0][0][0]
        data = json.loads(output)
        self.assertIn("scenes", data)

    def test_script_to_file(self):
        parser = build_parser()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out = f.name
        try:
            args = parser.parse_args(["script", "test", "-o", out, "--llm-provider", "fallback"])
            ret = cmd_script(args)
            self.assertEqual(ret, 0)
            with open(out) as f:
                data = json.loads(f.read())
            self.assertIn("scenes", data)
        finally:
            os.unlink(out)


class TestCLIEvaluate(unittest.TestCase):
    def test_evaluate_missing_file(self):
        parser = build_parser()
        args = parser.parse_args(["evaluate", "/nonexistent/video.mp4"])
        with patch("builtins.print"):
            ret = cmd_evaluate(args)
        self.assertEqual(ret, 1)

    def test_evaluate_real_fixture(self):
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")
        if not os.path.exists(fixture):
            return
        parser = build_parser()
        args = parser.parse_args(["evaluate", fixture, "--layers", "1", "2"])
        with patch("builtins.print"):
            ret = cmd_evaluate(args)
        self.assertIn(ret, (0, 1))  # Either pass or fail is valid


# ── Server ─────────────────────────────────────────────────────────

class TestServerImport(unittest.TestCase):
    def test_server_module_importable(self):
        """Server module should be importable (FastAPI may not be installed)."""
        try:
            from src.server import create_app
            app = create_app()
            self.assertIsNotNone(app)
        except RuntimeError as e:
            self.assertIn("FastAPI", str(e))
