"""VideoQA — end-to-end AI short video generation + quality gate CLI."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

logger = logging.getLogger("videoqa")


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate a video from a topic, end-to-end."""
    from src.pipeline.generators.script import ScriptGenerator
    from src.pipeline.generators.tts import TTSGenerator
    from src.pipeline.generators.ai_video import AIVideoGenerator
    from src.pipeline.generators.bgm import BGMGenerator
    from src.pipeline.generators.subtitles import SubtitleGenerator
    from src.pipeline.composer import VideoComposer
    from src.quality_gate import evaluate

    topic = args.topic
    output_dir = Path(args.output or f"./output/{int(time.time())}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] Generating script for: {topic}")
    script_gen = ScriptGenerator(provider=args.llm_provider)
    script = script_gen.generate(
        topic=topic,
        duration=args.duration,
        style=args.style,
        language=args.language,
    )

    # Save script
    script_path = output_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"    Script: {script.title} ({len(script.scenes)} scenes)")

    print("[2/5] Generating narration audio (TTS)...")
    tts = TTSGenerator(
        default_provider=args.tts_provider,
        default_voice=args.voice,
    )
    narration_texts = [s.narration for s in script.scenes]
    full_narration = "\n".join(narration_texts)
    audio_path = str(output_dir / "narration.mp3")
    audio_clip = tts.generate(full_narration, output_path=audio_path)
    print(f"    Audio: {audio_clip.duration:.1f}s -> {audio_path}")

    print("[3/5] Generating subtitles...")
    sub_gen = SubtitleGenerator()
    srt_path = str(output_dir / "subtitles.srt")
    srt_content = sub_gen.generate(audio_path, output_path=srt_path)
    print(f"    Subtitles: {srt_path}")

    print("[4/5] Preparing video clips...")
    # For now, use a placeholder — real generation would call AIVideoGenerator
    # which requires API keys. Instead, create a test pattern video per scene.
    video_clips = []
    for i, scene in enumerate(script.scenes):
        clip_path = str(output_dir / f"clip_{i:03d}.mp4")
        # Generate a simple color card with text as placeholder
        _generate_placeholder_clip(clip_path, scene.visual_description, scene.duration_hint)
        video_clips.append(clip_path)
    print(f"    {len(video_clips)} clips prepared")

    print("[5/5] Composing final video...")
    composer = VideoComposer()
    final_path = str(output_dir / "final.mp4")
    try:
        bgm_path = ""
        if args.bgm_library and os.path.isdir(args.bgm_library):
            bgm_gen = BGMGenerator(library_path=args.bgm_library)
            try:
                bgm_clip = bgm_gen.select(
                    mood=script.scenes[0].mood if script.scenes else "calm",
                    duration=audio_clip.duration,
                )
                bgm_path = bgm_clip.local_path
            except (ValueError, Exception) as e:
                logger.warning("BGM generation failed: %s", e)

        composer.compose(
            video_clips=video_clips,
            audio=audio_path,
            subtitles=srt_path,
            bgm=bgm_path,
            output_path=final_path,
        )
        print(f"    Final video: {final_path}")
    except RuntimeError as e:
        print(f"    Composition failed: {e}")
        print(f"    Individual components saved in: {output_dir}")
        return 1

    # Quality evaluation
    if not args.skip_eval:
        print("\n[QA] Running quality evaluation...")
        result = evaluate(final_path, prompt=topic, layers=[1, 2])
        if result.decision:
            print(f"    Verdict: {result.decision.verdict.upper()}")
            print(f"    Confidence: {result.decision.confidence:.2f}")
        else:
            print("    Verdict: N/A")

    print(f"\nDone! Output directory: {output_dir}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    """Evaluate an existing video's quality."""
    from src.quality_gate import evaluate

    video_path = args.video
    if not os.path.isfile(video_path):
        print(f"Error: file not found: {video_path}")
        return 1

    print(f"Evaluating: {video_path}")
    layers = args.layers or [1, 2, 3]

    result = evaluate(
        video_path=video_path,
        prompt=args.prompt,
        layers=layers,
    )

    print(f"\nVideo:    {result.video_path}")
    print(f"Layers:   {', '.join(result.layers_run)}")

    if result.l1_result:
        passed = sum(1 for c in result.l1_result.checks if c.passed)
        total = len(result.l1_result.checks)
        print(f"\nL1 Programmatic: {passed}/{total} checks passed")
        for check in result.l1_result.checks:
            status = "PASS" if check.passed else "FAIL"
            detail = check.details.get("message", "") if check.details else ""
            print(f"  [{status}] {check.name}: {check.score:.2f} — {detail}")

    if result.l2_result:
        passed = sum(1 for c in result.l2_result.checks if c.passed)
        total = len(result.l2_result.checks)
        print(f"\nL2 ML: {passed}/{total} checks passed")
        for check in result.l2_result.checks:
            detail = check.details.get("message", "") if check.details else ""
            status = "PASS" if check.passed else "SKIP" if "skip" in detail.lower() else "FAIL"
            print(f"  [{status}] {check.name}: {check.score:.2f} — {detail}")

    if result.decision:
        print(f"\nVerdict:  {result.decision.verdict.upper()}")
        print(f"Confidence: {result.decision.confidence:.2f}")
        for reason in result.decision.reasons:
            print(f"  - {reason}")

    if args.json:
        report = {
            "video_path": result.video_path,
            "layers": result.layers_run,
            "verdict": result.decision.verdict if result.decision else None,
            "confidence": result.decision.confidence if result.decision else None,
        }
        print(f"\n{json.dumps(report, indent=2)}")

    return 0 if result.passed else 1


def cmd_script(args: argparse.Namespace) -> int:
    """Generate a video script from a topic."""
    from src.pipeline.generators.script import ScriptGenerator

    gen = ScriptGenerator(provider=args.llm_provider)
    script = gen.generate(
        topic=args.topic,
        duration=args.duration,
        style=args.style,
        language=args.language,
    )

    output = json.dumps(script.to_dict(), ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Script saved to: {args.output}")
    else:
        print(output)

    return 0


def _generate_placeholder_clip(output_path: str, text: str, duration: float) -> None:
    """Generate a simple placeholder video clip with text overlay using FFmpeg."""
    import subprocess

    # Truncate text for display
    display_text = text[:60].replace("'", "").replace('"', "").replace(":", " ")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:s=1080x1920:d={duration}:r=30",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration),
        "-vf", f"drawtext=text='{display_text}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:font=monospace",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", "-shortest",
        output_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=30)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logger.warning("Placeholder clip failed: %s — creating minimal clip", exc)
        # Absolute minimum fallback
        cmd_min = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={duration}:r=30",
            "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-shortest",
            output_path,
        ]
        subprocess.run(cmd_min, capture_output=True, check=True, timeout=30)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="videoqa",
        description="AI Short Video Generator + Quality Gate System",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug logging",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -- generate --
    gen_parser = subparsers.add_parser(
        "generate", help="Generate a video from a topic",
        description="End-to-end: topic → script → TTS → video → compose → QA",
    )
    gen_parser.add_argument("topic", help="Video topic")
    gen_parser.add_argument("-o", "--output", help="Output directory")
    gen_parser.add_argument("--duration", type=float, default=60.0, help="Target duration (seconds)")
    gen_parser.add_argument("--style", default="informative", choices=["informative", "storytelling", "tutorial", "review"])
    gen_parser.add_argument("--language", default="zh", help="Narration language")
    gen_parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
    gen_parser.add_argument("--tts-provider", default="edge-tts", choices=["edge-tts", "elevenlabs"])
    gen_parser.add_argument("--llm-provider", default=None, choices=["openai", "gemini", "fallback"])
    gen_parser.add_argument("--bgm-library", default=None, help="Path to BGM library directory")
    gen_parser.add_argument("--skip-eval", action="store_true", help="Skip quality evaluation")
    gen_parser.set_defaults(func=cmd_generate)

    # -- evaluate --
    eval_parser = subparsers.add_parser(
        "evaluate", help="Evaluate video quality",
        description="Run quality gate checks on an existing video",
    )
    eval_parser.add_argument("video", help="Path to video file")
    eval_parser.add_argument("--prompt", default="", help="Generation prompt for alignment checks")
    eval_parser.add_argument("--layers", type=int, nargs="+", choices=[1, 2, 3], help="Quality layers to run")
    eval_parser.add_argument("--json", action="store_true", help="Output JSON report")
    eval_parser.set_defaults(func=cmd_evaluate)

    # -- script --
    script_parser = subparsers.add_parser(
        "script", help="Generate a video script",
        description="Generate a structured video script from a topic using LLM",
    )
    script_parser.add_argument("topic", help="Video topic")
    script_parser.add_argument("-o", "--output", help="Output file path (JSON)")
    script_parser.add_argument("--duration", type=float, default=60.0, help="Target duration")
    script_parser.add_argument("--style", default="informative", choices=["informative", "storytelling", "tutorial", "review"])
    script_parser.add_argument("--language", default="zh")
    script_parser.add_argument("--llm-provider", default=None, choices=["openai", "gemini", "fallback"])
    script_parser.set_defaults(func=cmd_script)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
