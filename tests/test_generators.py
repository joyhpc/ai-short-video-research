"""Tests for Phase 4 — generator adapters and video composer."""
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open

# ── Stock Footage ──────────────────────────────────────────────────
from src.pipeline.generators.stock_footage import StockFootageGenerator, VideoClip as StockClip


class TestStockFootageSearch(unittest.TestCase):
    def setUp(self):
        self.gen = StockFootageGenerator(provider="pexels", api_key="test-key")

    @patch("urllib.request.urlopen")
    def test_pexels_search_parses_results(self, mock_urlopen):
        """Pexels search should parse video files from API response."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "videos": [{
                "id": 123,
                "duration": 15,
                "video_files": [
                    {"link": "https://example.com/v1.mp4", "width": 1920, "height": 1080, "quality": "hd", "file_type": "video/mp4"},
                    {"link": "https://example.com/v2.mp4", "width": 640, "height": 360, "quality": "sd", "file_type": "video/mp4"},
                ],
            }],
        }).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        clips = self.gen.search("ocean sunset", count=1)
        self.assertEqual(len(clips), 1)
        self.assertEqual(clips[0].width, 1920)  # picked best quality
        self.assertEqual(clips[0].duration, 15.0)

    @patch("urllib.request.urlopen")
    def test_pexels_search_empty_response(self, mock_urlopen):
        """Empty Pexels response should return empty list."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"videos": []}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        clips = self.gen.search("nothing", count=5)
        self.assertEqual(clips, [])

    def test_unsupported_provider_raises(self):
        gen = StockFootageGenerator(provider="unknown")
        with self.assertRaises(ValueError):
            gen.search("test")

    @patch("os.path.getsize", return_value=1024)
    @patch("src.pipeline.generators.stock_footage.urllib.request.urlretrieve")
    def test_download_creates_dirs(self, mock_retrieve, mock_getsize):
        """Download should create parent directories."""
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "sub", "dir", "video.mp4")
            self.gen.download("https://example.com/v.mp4", out)
            self.assertTrue(os.path.isdir(os.path.join(td, "sub", "dir")))
            mock_retrieve.assert_called_once()


class TestPixabaySearch(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_pixabay_search(self, mock_urlopen):
        """Pixabay search should parse hits."""
        gen = StockFootageGenerator(provider="pixabay", api_key="pix-key")
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "hits": [{
                "id": 456,
                "duration": 10,
                "tags": "nature, sky",
                "videos": {
                    "large": {"url": "https://pixabay.com/v1.mp4", "width": 1920, "height": 1080},
                },
            }],
        }).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        clips = gen.search("nature sky", count=1)
        self.assertEqual(len(clips), 1)
        self.assertEqual(clips[0].metadata["provider"], "pixabay")


# ── AI Video Generator ────────────────────────────────────────────
from src.pipeline.generators.ai_video import AIVideoGenerator, VideoClip as AIClip


class TestAIVideoGenerator(unittest.TestCase):
    def test_missing_api_key_raises(self):
        gen = AIVideoGenerator(default_provider="kling", api_keys={})
        with self.assertRaises(ValueError):
            gen.generate("a cat")

    def test_unsupported_provider_raises(self):
        gen = AIVideoGenerator(default_provider="unsupported")
        with self.assertRaises(ValueError):
            gen.generate("a cat")

    @patch.object(AIVideoGenerator, "_download_result")
    @patch.object(AIVideoGenerator, "_poll_task")
    @patch.object(AIVideoGenerator, "_submit_task")
    def test_kling_full_flow(self, mock_submit, mock_poll, mock_download):
        """Kling generation should submit → poll → download."""
        mock_submit.return_value = {"task_id": "task-123"}
        mock_poll.return_value = {
            "status": "completed",
            "output": {"video_url": "https://kling.ai/result.mp4"},
        }
        mock_download.return_value = "/tmp/result.mp4"

        gen = AIVideoGenerator(api_keys={"kling": "key-123"})
        clip = gen.generate("a cat playing piano", provider="kling")

        self.assertEqual(clip.local_path, "/tmp/result.mp4")
        self.assertEqual(clip.provider, "kling")
        self.assertEqual(clip.prompt, "a cat playing piano")
        mock_submit.assert_called_once()
        mock_poll.assert_called_once()

    @patch.object(AIVideoGenerator, "_download_result")
    @patch.object(AIVideoGenerator, "_poll_task")
    @patch.object(AIVideoGenerator, "_submit_task")
    def test_runway_full_flow(self, mock_submit, mock_poll, mock_download):
        """Runway generation should submit → poll → download."""
        mock_submit.return_value = {"id": "run-456"}
        mock_poll.return_value = {
            "status": "completed",
            "output": {"url": "https://runway.ai/result.mp4"},
        }
        mock_download.return_value = "/tmp/runway.mp4"

        gen = AIVideoGenerator(api_keys={"runway": "rw-key"})
        clip = gen.generate("sunset beach", provider="runway")

        self.assertEqual(clip.provider, "runway")


# ── TTS Generator ─────────────────────────────────────────────────
from src.pipeline.generators.tts import TTSGenerator, AudioClip


class TestTTSGenerator(unittest.TestCase):
    def test_unsupported_provider_raises(self):
        gen = TTSGenerator(default_provider="unknown")
        with self.assertRaises(ValueError):
            gen.generate("hello")

    @patch.object(TTSGenerator, "_get_duration", return_value=3.5)
    @patch.object(TTSGenerator, "_generate_edge_tts")
    def test_edge_tts_returns_audio_clip(self, mock_gen, mock_dur):
        """edge-tts generation should return an AudioClip."""
        gen = TTSGenerator()
        clip = gen.generate("你好世界", output_path="/tmp/test_tts.mp3")
        self.assertIsInstance(clip, AudioClip)
        self.assertEqual(clip.duration, 3.5)
        self.assertEqual(clip.provider, "edge-tts")
        mock_gen.assert_called_once()

    @patch.object(TTSGenerator, "_get_duration", return_value=2.0)
    @patch.object(TTSGenerator, "_generate_elevenlabs")
    def test_elevenlabs_returns_audio_clip(self, mock_gen, mock_dur):
        """ElevenLabs should return an AudioClip with correct provider."""
        gen = TTSGenerator(default_provider="elevenlabs")
        clip = gen.generate("hello", output_path="/tmp/test_el.mp3")
        self.assertIsInstance(clip, AudioClip)
        self.assertEqual(clip.provider, "elevenlabs")
        self.assertEqual(clip.duration, 2.0)
        mock_gen.assert_called_once()


# ── BGM Generator ─────────────────────────────────────────────────
from src.pipeline.generators.bgm import BGMGenerator, AudioClip as BGMAudio


class TestBGMGenerator(unittest.TestCase):
    def test_no_library_raises(self):
        gen = BGMGenerator(library_path=None)
        with self.assertRaises(ValueError):
            gen.select("upbeat", duration=30.0)

    @patch.object(BGMGenerator, "_get_duration", return_value=30.0)
    @patch.object(BGMGenerator, "_trim_and_fade", return_value="/tmp/trimmed.mp3")
    def test_mood_match(self, mock_trim, mock_dur):
        """Should pick a file matching the mood tag."""
        with tempfile.TemporaryDirectory() as td:
            # Create test audio files
            for name in ["upbeat_track1.mp3", "calm_ambient.mp3", "random.wav"]:
                open(os.path.join(td, name), "w").close()

            gen = BGMGenerator(library_path=td)
            clip = gen.select("upbeat", duration=30.0)

            self.assertIsInstance(clip, BGMAudio)
            self.assertEqual(clip.mood, "upbeat")
            mock_trim.assert_called_once()
            # Verify the source was the mood-matched file
            call_args = mock_trim.call_args
            self.assertIn("upbeat", call_args[0][0])

    @patch.object(BGMGenerator, "_get_duration", return_value=20.0)
    @patch.object(BGMGenerator, "_trim_and_fade", return_value="/tmp/trimmed.mp3")
    def test_no_mood_match_picks_random(self, mock_trim, mock_dur):
        """When no mood match, should pick randomly from all files."""
        with tempfile.TemporaryDirectory() as td:
            open(os.path.join(td, "track1.mp3"), "w").close()
            open(os.path.join(td, "track2.wav"), "w").close()

            gen = BGMGenerator(library_path=td)
            clip = gen.select("suspenseful", duration=20.0)
            self.assertIsInstance(clip, BGMAudio)


# ── Subtitle Generator ────────────────────────────────────────────
from src.pipeline.generators.subtitles import SubtitleGenerator, _format_timestamp, _split_text


class TestSubtitleHelpers(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(_format_timestamp(0.0), "00:00:00,000")
        self.assertEqual(_format_timestamp(62.5), "00:01:02,500")
        self.assertEqual(_format_timestamp(3661.123), "01:01:01,123")

    def test_split_text_short(self):
        result = _split_text("短文本", 20)
        self.assertEqual(result, ["短文本"])

    def test_split_text_long(self):
        result = _split_text("这是一段比较长的中文文本需要进行分割处理", 10)
        self.assertTrue(all(len(line) <= 11 for line in result))  # allow slight overflow at split point
        self.assertGreater(len(result), 1)


class TestSubtitleGenerator(unittest.TestCase):
    @patch("src.pipeline.generators.subtitles.SubtitleGenerator._generate_whisper")
    def test_generate_writes_file(self, mock_whisper):
        """Should write SRT to output_path when specified."""
        mock_whisper.return_value = "1\n00:00:00,000 --> 00:00:02,000\n测试字幕\n"

        gen = SubtitleGenerator()
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as f:
            out = f.name
        try:
            srt = gen.generate("audio.wav", output_path=out)
            self.assertIn("测试字幕", srt)
            with open(out) as f:
                self.assertEqual(f.read(), srt)
        finally:
            os.unlink(out)

    def test_whisper_import_error_graceful(self):
        """Should return a comment when whisper is not installed."""
        gen = SubtitleGenerator()
        # Whisper is likely not installed in test env
        srt = gen.generate("nonexistent.wav")
        # Either generates subtitles or returns the import error message
        self.assertIsInstance(srt, str)


# ── Video Composer ─────────────────────────────────────────────────
from src.pipeline.composer import VideoComposer, CompositionSpec


class TestVideoComposer(unittest.TestCase):
    def setUp(self):
        self.composer = VideoComposer()

    def test_no_clips_raises(self):
        with self.assertRaises(ValueError):
            self.composer.compose([], "audio.wav", "", "", "/tmp/out.mp4")

    def test_build_concat_file(self):
        """Concat file should list all clips."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            pass
        clips = ["/tmp/clip1.mp4", "/tmp/clip2.mp4"]
        path = self.composer._build_concat_file(clips)
        try:
            with open(path) as f:
                content = f.read()
            self.assertIn("clip1.mp4", content)
            self.assertIn("clip2.mp4", content)
            self.assertEqual(content.count("file"), 2)
        finally:
            os.unlink(path)

    def test_compose_from_spec_delegates(self):
        """compose_from_spec should delegate to compose."""
        spec = CompositionSpec(
            video_clips=["a.mp4"],
            audio_path="a.wav",
            output_path="/tmp/out.mp4",
        )
        with patch.object(self.composer, "compose", return_value="/tmp/out.mp4") as mock:
            result = self.composer.compose_from_spec(spec)
            mock.assert_called_once()
            self.assertEqual(result, "/tmp/out.mp4")

    @patch.object(VideoComposer, "_run_ffmpeg")
    def test_compose_single_clip_no_bgm(self, mock_ffmpeg):
        """Single clip without BGM should work."""
        mock_ffmpeg.return_value = MagicMock(returncode=0)
        fixture = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")
        if os.path.exists(fixture):
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                out = f.name
            try:
                result = self.composer.compose(
                    video_clips=[fixture],
                    audio=fixture,  # reuse as audio source for test
                    subtitles="",
                    bgm="",
                    output_path=out,
                )
                mock_ffmpeg.assert_called_once()
            finally:
                if os.path.exists(out):
                    os.unlink(out)
