"""Script generator — LLM-based topic → structured video script."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Scene:
    """A single scene in the video script."""
    scene_number: int
    narration: str  # Text to be spoken (TTS input)
    visual_description: str  # Visual description (video gen prompt)
    mood: str = "neutral"  # BGM mood tag
    duration_hint: float = 5.0  # Estimated duration in seconds


@dataclass
class VideoScript:
    """Complete video script with multiple scenes."""
    title: str
    topic: str
    scenes: list[Scene] = field(default_factory=list)
    total_duration: float = 0.0
    style: str = "informative"
    language: str = "zh"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "VideoScript":
        """Parse a JSON dict (e.g., from LLM output) into a VideoScript."""
        scenes = [
            Scene(
                scene_number=s.get("scene_number", i + 1),
                narration=s.get("narration", ""),
                visual_description=s.get("visual_description", ""),
                mood=s.get("mood", "neutral"),
                duration_hint=float(s.get("duration_hint", 5.0)),
            )
            for i, s in enumerate(data.get("scenes", []))
        ]
        return cls(
            title=data.get("title", ""),
            topic=data.get("topic", ""),
            scenes=scenes,
            total_duration=sum(s.duration_hint for s in scenes),
            style=data.get("style", "informative"),
            language=data.get("language", "zh"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_prompt_list(self) -> list[tuple[str, str]]:
        """Return [(narration, visual_description), ...] for downstream pipeline."""
        return [(s.narration, s.visual_description) for s in self.scenes]


SYSTEM_PROMPT = """You are a professional short video scriptwriter.
Given a topic, generate a structured video script in JSON format.

The output MUST be valid JSON with this structure:
{
  "title": "Video title",
  "topic": "Original topic",
  "style": "informative|storytelling|tutorial|review",
  "language": "zh",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "Text to be spoken by the narrator (in the requested language)",
      "visual_description": "Detailed visual description for AI video generation (in English for best results)",
      "mood": "upbeat|calm|dramatic|inspiring|suspenseful|happy|melancholic|energetic",
      "duration_hint": 5.0
    }
  ]
}

Guidelines:
- Each scene should be 3-8 seconds
- Narration should be natural, engaging, and concise
- Visual descriptions should be detailed and cinematic
- Total script duration should match the requested duration
- Use appropriate mood tags for each scene
- Return ONLY the JSON, no other text"""


class ScriptGenerator:
    """Generate structured video scripts from topics using LLM.

    Supports OpenAI and Gemini as LLM providers, with a rule-based
    fallback when no API key is available.

    Args:
        provider: LLM provider ("openai", "gemini", or "fallback").
        model: Model name override.
    """

    SUPPORTED_PROVIDERS = ("openai", "gemini", "fallback")

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        # Auto-detect provider from available API keys
        if provider is None:
            if os.environ.get("OPENAI_API_KEY"):
                provider = "openai"
            elif os.environ.get("GOOGLE_API_KEY"):
                provider = "gemini"
            else:
                provider = "fallback"
        self.provider = provider
        self.model = model

    def generate(
        self,
        topic: str,
        duration: float = 60.0,
        style: str = "informative",
        language: str = "zh",
        num_scenes: int | None = None,
    ) -> VideoScript:
        """Generate a video script from a topic.

        Args:
            topic: The video topic/subject.
            duration: Target total duration in seconds.
            style: Script style (informative, storytelling, tutorial, review).
            language: Output language for narration.
            num_scenes: Number of scenes (auto-calculated if None).

        Returns:
            VideoScript with structured scenes.
        """
        if num_scenes is None:
            num_scenes = max(3, min(20, int(duration / 5)))

        user_prompt = (
            f"Topic: {topic}\n"
            f"Target duration: {duration} seconds\n"
            f"Style: {style}\n"
            f"Language: {language}\n"
            f"Number of scenes: {num_scenes}"
        )

        if self.provider == "openai":
            raw = self._call_openai(user_prompt)
        elif self.provider == "gemini":
            raw = self._call_gemini(user_prompt)
        else:
            raw = self._fallback_script(topic, duration, style, language, num_scenes)

        try:
            if isinstance(raw, str):
                # Strip markdown code blocks if present
                text = raw.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                data = json.loads(text)
            else:
                data = raw
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON, using fallback")
            data = self._fallback_script(topic, duration, style, language, num_scenes)

        script = VideoScript.from_json(data)
        script.topic = topic
        script.style = style
        script.language = language
        logger.info("Script generated: %s — %d scenes, %.0fs", script.title, len(script.scenes), script.total_duration)
        return script

    def _call_openai(self, user_prompt: str) -> str:
        """Call OpenAI API to generate script."""
        import urllib.request

        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = self.model or "gpt-4o-mini"

        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("OpenAI API failed: %s — using fallback", exc)
            return json.dumps(self._fallback_script(
                "topic", 60, "informative", "zh", 12
            ))

    def _call_gemini(self, user_prompt: str) -> str:
        """Call Gemini API to generate script."""
        import urllib.request

        api_key = os.environ.get("GOOGLE_API_KEY", "")
        model = self.model or "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = json.dumps({
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_prompt}"}]}],
            "generationConfig": {"temperature": 0.7},
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as exc:
            logger.warning("Gemini API failed: %s — using fallback", exc)
            return json.dumps(self._fallback_script(
                "topic", 60, "informative", "zh", 12
            ))

    @staticmethod
    def _fallback_script(
        topic: str,
        duration: float,
        style: str,
        language: str,
        num_scenes: int,
    ) -> dict[str, Any]:
        """Generate a simple rule-based script when no LLM is available."""
        scene_duration = duration / num_scenes

        # Template-based scenes
        templates = [
            ("opening", f"欢迎来到今天的视频，我们来聊聊{topic}。", f"Title card with text '{topic}', modern clean design, cinematic lighting", "inspiring"),
            ("context", f"首先，让我们了解一下{topic}的背景。", f"Wide establishing shot related to {topic}, soft natural lighting, 4K quality", "calm"),
            ("detail1", f"关于{topic}，有一个非常重要的方面值得关注。", f"Close-up detail shot showcasing key aspect of {topic}, sharp focus, professional lighting", "dramatic"),
            ("detail2", f"另一个有趣的点是，{topic}正在快速发展变化。", f"Dynamic montage showing evolution and progress related to {topic}, modern style", "energetic"),
            ("example", f"举个例子来说明{topic}的实际应用。", f"Real-world application scene of {topic}, bright daylight, documentary style", "upbeat"),
            ("insight", f"深入分析{topic}，我们可以发现一些规律。", f"Data visualization and analysis graphics related to {topic}, clean infographic style", "calm"),
            ("trend", f"从趋势来看，{topic}的未来非常值得期待。", f"Futuristic scene representing innovation in {topic}, neon lights, tech aesthetic", "inspiring"),
            ("impact", f"这对我们每个人都有深远的影响。", f"People interacting with {topic} in daily life, warm color grading, human stories", "happy"),
            ("challenge", f"当然，{topic}也面临一些挑战和问题。", f"Dramatic scene showing obstacles and challenges, moody atmosphere", "suspenseful"),
            ("solution", f"但是解决方案已经出现，让我们看看如何应对。", f"Solution-oriented scene, bright hopeful atmosphere, problem-solving visuals", "upbeat"),
            ("summary", f"总结一下今天关于{topic}的内容。", f"Summary graphics with key points about {topic}, clean layout", "calm"),
            ("closing", f"感谢观看，如果觉得有用，请点赞关注！下期见！", f"Outro card with subscribe button animation, warm friendly style", "happy"),
        ]

        scenes = []
        for i in range(num_scenes):
            idx = i % len(templates)
            tag, narration, visual, mood = templates[idx]
            scenes.append({
                "scene_number": i + 1,
                "narration": narration,
                "visual_description": visual,
                "mood": mood,
                "duration_hint": scene_duration,
            })

        return {
            "title": f"关于{topic}的深度解析",
            "topic": topic,
            "style": style,
            "language": language,
            "scenes": scenes,
        }
