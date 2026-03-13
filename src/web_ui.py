"""VideoQA Web UI — Gradio interface for video generation and evaluation."""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def create_ui():
    """Create and configure the Gradio interface."""
    try:
        import gradio as gr
    except ImportError:
        raise RuntimeError(
            "Gradio is not installed. Install with: pip install 'videoqa-gate[web]'"
        )

    def generate_script(topic, duration, style, language, llm_provider):
        """Generate a video script from a topic."""
        from src.pipeline.generators.script import ScriptGenerator

        provider = llm_provider if llm_provider != "auto" else None
        gen = ScriptGenerator(provider=provider)
        script = gen.generate(
            topic=topic,
            duration=float(duration),
            style=style,
            language=language,
        )
        return json.dumps(script.to_dict(), ensure_ascii=False, indent=2)

    def generate_narration(script_json, voice, tts_provider):
        """Generate narration audio from script."""
        from src.pipeline.generators.script import VideoScript
        from src.pipeline.generators.tts import TTSGenerator

        try:
            data = json.loads(script_json)
            script = VideoScript.from_json(data)
        except (json.JSONDecodeError, Exception) as e:
            return None, f"Error parsing script: {e}"

        output_dir = Path(f"./output/ui_{int(time.time())}")
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = str(output_dir / "narration.mp3")

        tts = TTSGenerator(default_provider=tts_provider, default_voice=voice)
        narration = "\n".join(s.narration for s in script.scenes)

        try:
            clip = tts.generate(narration, output_path=audio_path)
            return audio_path, f"Generated {clip.duration:.1f}s audio at {audio_path}"
        except Exception as e:
            return None, f"TTS failed: {e}"

    def evaluate_video(video_path, prompt, l1, l2, l3):
        """Run quality evaluation on a video."""
        from src.quality_gate import evaluate

        if not video_path or not os.path.isfile(video_path):
            return "Error: Please provide a valid video file path."

        layers = []
        if l1: layers.append(1)
        if l2: layers.append(2)
        if l3: layers.append(3)
        if not layers:
            layers = [1, 2]

        result = evaluate(video_path=video_path, prompt=prompt, layers=layers)

        report_lines = [
            f"## Quality Evaluation Report",
            f"**Video:** {result.video_path}",
            f"**Layers:** {', '.join(result.layers_run)}",
            "",
        ]

        if result.l1_result:
            report_lines.append("### L1 — Programmatic Checks")
            for check in result.l1_result.checks:
                icon = "✅" if check.passed else "❌"
                detail = check.details.get("message", "") if check.details else ""
                report_lines.append(f"- {icon} **{check.name}**: {check.score:.2f} — {detail}")
            report_lines.append("")

        if result.l2_result:
            report_lines.append("### L2 — ML Checks")
            for check in result.l2_result.checks:
                detail = check.details.get("message", "") if check.details else ""
                icon = "✅" if check.passed else "⚠️" if "skip" in detail.lower() else "❌"
                report_lines.append(f"- {icon} **{check.name}**: {check.score:.2f} — {detail}")
            report_lines.append("")

        if result.decision:
            verdict = result.decision.verdict.upper()
            color = "🟢" if verdict == "PASS" else "🔴" if verdict == "FAIL" else "🟡"
            report_lines.append(f"### Verdict: {color} {verdict}")
            report_lines.append(f"**Confidence:** {result.decision.confidence:.2f}")
            for r in result.decision.reasons:
                report_lines.append(f"- {r}")

        return "\n".join(report_lines)

    # ── Build the Gradio Interface ──

    with gr.Blocks(
        title="VideoQA — AI Video Quality Gate",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# VideoQA — AI 短视频生成 + 质量门控系统\n"
            "三层质量门控 + 评估-纠错闭环 | Three-Layer Quality Gate + Correction Loop"
        )

        with gr.Tab("Script Generation"):
            gr.Markdown("### Generate Video Script from Topic")
            with gr.Row():
                with gr.Column(scale=1):
                    topic_input = gr.Textbox(label="Topic", placeholder="e.g., AI 在医疗领域的应用")
                    with gr.Row():
                        duration_input = gr.Number(label="Duration (s)", value=60)
                        style_input = gr.Dropdown(
                            label="Style",
                            choices=["informative", "storytelling", "tutorial", "review"],
                            value="informative",
                        )
                    with gr.Row():
                        language_input = gr.Dropdown(label="Language", choices=["zh", "en", "ja"], value="zh")
                        llm_input = gr.Dropdown(
                            label="LLM Provider",
                            choices=["auto", "openai", "gemini", "fallback"],
                            value="auto",
                        )
                    gen_script_btn = gr.Button("Generate Script", variant="primary")
                with gr.Column(scale=2):
                    script_output = gr.Textbox(label="Script (JSON)", lines=20)

            gen_script_btn.click(
                fn=generate_script,
                inputs=[topic_input, duration_input, style_input, language_input, llm_input],
                outputs=script_output,
            )

        with gr.Tab("Narration (TTS)"):
            gr.Markdown("### Generate Narration Audio from Script")
            with gr.Row():
                with gr.Column(scale=1):
                    tts_script_input = gr.Textbox(label="Script JSON", lines=10, placeholder="Paste script JSON here")
                    with gr.Row():
                        voice_input = gr.Textbox(label="Voice", value="zh-CN-XiaoxiaoNeural")
                        tts_provider_input = gr.Dropdown(
                            label="TTS Provider",
                            choices=["edge-tts", "elevenlabs"],
                            value="edge-tts",
                        )
                    gen_tts_btn = gr.Button("Generate Audio", variant="primary")
                with gr.Column(scale=1):
                    audio_output = gr.Audio(label="Narration Audio", type="filepath")
                    tts_status = gr.Textbox(label="Status")

            gen_tts_btn.click(
                fn=generate_narration,
                inputs=[tts_script_input, voice_input, tts_provider_input],
                outputs=[audio_output, tts_status],
            )

        with gr.Tab("Quality Evaluation"):
            gr.Markdown("### Evaluate Video Quality")
            with gr.Row():
                with gr.Column(scale=1):
                    eval_video_input = gr.Textbox(
                        label="Video File Path",
                        placeholder="/path/to/video.mp4",
                    )
                    eval_prompt_input = gr.Textbox(
                        label="Generation Prompt (for alignment check)",
                        placeholder="Original prompt used to generate the video",
                    )
                    gr.Markdown("**Quality Layers:**")
                    with gr.Row():
                        l1_check = gr.Checkbox(label="L1 Programmatic", value=True)
                        l2_check = gr.Checkbox(label="L2 ML", value=True)
                        l3_check = gr.Checkbox(label="L3 VLM", value=False)
                    eval_btn = gr.Button("Evaluate", variant="primary")
                with gr.Column(scale=2):
                    eval_output = gr.Markdown(label="Evaluation Report")

            eval_btn.click(
                fn=evaluate_video,
                inputs=[eval_video_input, eval_prompt_input, l1_check, l2_check, l3_check],
                outputs=eval_output,
            )

        with gr.Tab("About"):
            gr.Markdown("""
## Architecture

**Three-Layer Quality Gate:**
- **L1 Programmatic** (<1s): File integrity, resolution, A/V sync, loudness, frame consistency
- **L2 ML** (1-10s): NIQE visual quality, CLIP text alignment, temporal consistency, motion, color
- **L3 VLM** (5-30s): Gemini/GPT-4V review with CoT reasoning and discrete labels

**Correction Loop:**
- Problem diagnosis → prompt rewriting → retry with budget management
- Strategies: cheap retry, correction retry, graceful degradation, human escalation

**Generator Adapters:**
- Video: Kling, Runway API
- Audio: edge-tts, ElevenLabs
- BGM: local library with mood matching
- Subtitles: Whisper transcription
- Composition: FFmpeg complex filter graph

[GitHub](https://github.com/joyhpc/ai-short-video-research)
            """)

    return demo


def main():
    """Launch the Gradio UI."""
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
