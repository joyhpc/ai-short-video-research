# 📖 2026 AI短视频工业化生产全书 (The Complete AI Video Encyclopedia)

> **汇编时间**：2026.03
> **卷首语**：本书由所有独立文档重构聚合而成，包含底层技术剖析、商业模型选型、全自动工作流搭建以及千万级曝光广告大片拆解。全书实用先行，自上而下为您呈现 2026 年 AI 视频工业的终极全景图。

---

## 📚 全书总目录

- [VideoQA Gate — Project Navigation](#videoqa-gate-project-navigation)
- [Open-Source Short Video Generation Landscape](#open-source-short-video-generation-landscape)
- [Video Quality Evaluation Tools -- A Comprehensive Survey](#video-quality-evaluation-tools-a-comprehensive-survey)
- [Self-Correction Patterns for AI Video Generation](#self-correction-patterns-for-ai-video-generation)
- [Commercial AI Video Landscape](#commercial-ai-video-landscape)
- [Gap Analysis -- Where Open Source Falls Short](#gap-analysis-where-open-source-falls-short)
- [Architecture Proposal -- Three-Layer Quality Gate + Evaluation-Correction Loop](#architecture-proposal-three-layer-quality-gate-evaluation-correction-loop)
- [07 — AI 短视频自动生成：工具链选型与工作流分析](#07-ai-短视频自动生成工具链选型与工作流分析)
- [08 — AI 短视频生产最佳实践指南 (2026.03)](#08-ai-短视频生产最佳实践指南-202603)
- [商业广告短视频 AI 制作方案（落地版）](#商业广告短视频-ai-制作方案落地版)
- [10 — 全景解析：2026 AI 短视频自动化工作流体系与模型最佳实践](#10-全景解析2026-ai-短视频自动化工作流体系与模型最佳实践)
- [10 — AI 短视频制作终极指南 (2026.03)](#10-ai-短视频制作终极指南-202603)
- [11 — 一键出片最佳实践：工具、技巧与工作流 (2026.03.14)](#11-一键出片最佳实践工具技巧与工作流-20260314)
- [2026 AI 短视频工业化生产全书 (The Ultimate AI Video Handbook)](#2026-ai-短视频工业化生产全书-the-ultimate-ai-video-handbook)



<!-- FILE: 00-navigation.md -->
# VideoQA Gate — Project Navigation

> AI 短视频自动生成 — 评估闭环系统 | Three-Layer Quality Gate + Correction Loop

---

## Quick Start

```bash
# Generate a video from topic (with Veo 3.1)
videoqa generate "AI改变生活" --video-provider veo --duration 30

# Generate with free placeholder (no API key needed)
videoqa generate "AI改变生活" --duration 30

# Evaluate existing video quality
videoqa evaluate video.mp4 --layers 1 2

# Generate script only
videoqa script "量子计算" --duration 60

# Launch Web UI
python3 -m src.web_ui

# Launch REST API server
python3 -m src.server
```

---

## Project Documentation

| # | Document | Description | Key Topics |
|---|----------|-------------|------------|
| 01 | [Open-Source Landscape](docs/01-open-source-landscape.md) | 4-tier comparison of video generation projects | MoneyPrinterTurbo, ShortGPT, NarratoAI, Zeroscope |
| 02 | [Evaluation Tools](docs/02-evaluation-tools.md) | Survey of video quality assessment tools | VBench, DOVER, OpenCLIP, LGVQ, Q-Bench-Video, VGBE |
| 03 | [Self-Correction Patterns](docs/03-self-correction-patterns.md) | Closed-loop correction architectures | Google VISTA, Anthropic Evaluator-Optimizer, Netflix VMAF |
| 04 | [Commercial Landscape](docs/04-commercial-landscape.md) | Commercial video generation platforms | Runway, Synthesia, Kling 3.0, Jimeng, market analysis |
| 05 | [Gap Analysis](docs/05-gap-analysis.md) | 5 major gaps in current ecosystem | Quality evaluation gaps, correction loop absence |
| 06 | [Architecture Proposal](docs/06-architecture-proposal.md) | Core system architecture design | Three-layer gate, LangGraph, Veo 3.1, LangSmith |
| 07 | [Workflow Analysis](docs/07-workflow-analysis.md) | **工具链选型与工作流分析** (2026.03) | 推荐方案、2 月大爆发、Kling/Seedance/Veo 对比、路线 C 决策 |
| 08 | [Best Practices](docs/08-best-practices.md) | **AI 短视频生产最佳实践指南** | 4 套完整工作流、6 步实操手册、按预算选工具、Prompt 模板 |
| 09 | [Commercial Production](docs/09-commercial-production-guide.md) | **商业广告 AI 制作方案（落地版）** | 反投毒选型、Runway 为主力、完整广告工作流、月费 ~$280 |
| **10** | **[Ultimate Guide](docs/10-ultimate-guide.md)** | **AI 短视频制作终极指南** | 4 套工作流、8 步全流程、Prompt 模板、质量检测、自动化引擎、成本计算 |
| **11** | **[One-Click Best Practices](docs/11-one-click-best-practices.md)** | **一键出片最佳实践** | GitHub 活跃项目排名、4 种创作者模式、6 个突破性技巧、工具活跃度监控 |

---

## Source Code Map

### Core Pipeline

| Module | Path | Lines | Description |
|--------|------|-------|-------------|
| CLI | [`src/cli.py`](src/cli.py) | ~310 | `videoqa generate/evaluate/script` commands |
| Orchestrator | [`src/pipeline/orchestrator.py`](src/pipeline/orchestrator.py) | ~400 | Generate → evaluate → correct → retry loop |
| Composer | [`src/pipeline/composer.py`](src/pipeline/composer.py) | ~306 | FFmpeg complex filter graph composition |

### Quality Gate (Three Layers)

| Layer | Path | Latency | Cost | Checks |
|-------|------|---------|------|--------|
| L1 Programmatic | [`src/quality_gate/layer1_programmatic.py`](src/quality_gate/layer1_programmatic.py) | <1s | $0 | File integrity, resolution, A/V sync, loudness, frame consistency |
| L2 ML | [`src/quality_gate/layer2_ml.py`](src/quality_gate/layer2_ml.py) | 1-10s | ~$0.01 | NIQE visual quality, CLIP alignment, temporal consistency, motion, color |
| L3 VLM | [`src/quality_gate/layer3_vlm.py`](src/quality_gate/layer3_vlm.py) | 5-30s | ~$0.05 | Gemini/GPT-4V review, CoT reasoning, discrete labels, corrected prompts |
| Aggregator | [`src/quality_gate/aggregator.py`](src/quality_gate/aggregator.py) | — | — | Weighted decision matrix, configurable thresholds |

### Correction Loop

| Module | Path | Description |
|--------|------|-------------|
| Diagnosis | [`src/correction/diagnosis.py`](src/correction/diagnosis.py) | 5 problem types × 3 severity levels, fix strategy mapping |
| Prompt Rewriter | [`src/correction/prompt_rewriter.py`](src/correction/prompt_rewriter.py) | VLM-assisted + rule-based fallback, 20+ modifier templates |

### Generator Adapters

| Generator | Path | Providers |
|-----------|------|-----------|
| AI Video | [`src/pipeline/generators/ai_video.py`](src/pipeline/generators/ai_video.py) | **Veo 3.1**, Kling, Runway |
| Script | [`src/pipeline/generators/script.py`](src/pipeline/generators/script.py) | OpenAI, Gemini, fallback templates |
| TTS | [`src/pipeline/generators/tts.py`](src/pipeline/generators/tts.py) | edge-tts (free), ElevenLabs |
| BGM | [`src/pipeline/generators/bgm.py`](src/pipeline/generators/bgm.py) | Local library + FFmpeg trim/fade |
| Subtitles | [`src/pipeline/generators/subtitles.py`](src/pipeline/generators/subtitles.py) | Whisper (openai-whisper) |
| Stock Footage | [`src/pipeline/generators/stock_footage.py`](src/pipeline/generators/stock_footage.py) | Pexels, Pixabay (free) |

### Web Interface

| Module | Path | Port | Description |
|--------|------|------|-------------|
| FastAPI Server | [`src/server.py`](src/server.py) | 8000 | REST API: /api/generate, /api/evaluate, /api/jobs |
| Gradio Web UI | [`src/web_ui.py`](src/web_ui.py) | 7860 | Script generation, TTS, quality evaluation tabs |

---

## Configuration Files

| File | Purpose |
|------|---------|
| [`src/quality_gate/config.yaml`](src/quality_gate/config.yaml) | L1/L2/L3 thresholds, weights, retry settings |
| [`config/quality_thresholds.yaml`](config/quality_thresholds.yaml) | Per-metric pass/fail thresholds |
| [`config/pipeline.yaml`](config/pipeline.yaml) | Generation providers, retry policies, composition settings |
| [`pyproject.toml`](pyproject.toml) | Dependencies, entry points, optional dep groups |

---

## Test Suite

```bash
python3 -m pytest tests/ -v    # Run all 75 tests
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/test_layer1.py` | 11 | L1 programmatic checks (mock-based) |
| `tests/test_layer2.py` | 3 | L2 ML checks (real video fixture) |
| `tests/test_aggregator.py` | 5 | Decision matrix logic |
| `tests/test_correction.py` | 9 | Diagnosis + prompt rewriter |
| `tests/test_orchestrator.py` | 6 | Evaluate-only, retry loop, generator callable |
| `tests/test_generators.py` | 24 | All generator adapters + composer |
| `tests/test_phase5.py` | 17 | Script generator, CLI, server |

---

## Development Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Research repository — 6 analysis documents |
| Phase 2 | ✅ Complete | Quality Gate framework — L1/L2/L3 + aggregator |
| Phase 3 | ✅ Complete | Correction loop — diagnosis, prompt rewriting, orchestrator |
| Phase 4 | ✅ Complete | Generator adapters — Veo/Kling/Runway, TTS, BGM, subtitles, composer |
| Phase 5 | ✅ Complete | Full product — CLI, FastAPI, Gradio Web UI, Veo 3.1 integration |

---

## Key Academic References

| Paper | Org | Year | Contribution |
|-------|-----|------|-------------|
| [VISTA](https://arxiv.org/abs/2407.18178) | Google DeepMind | 2024 | Closed-loop video evaluation, 60% quality improvement |
| [Evaluator-Optimizer](https://arxiv.org/abs/2502.14802) | Anthropic | 2025 | Two-agent iterative improvement pattern |
| [VBench](https://github.com/Vchitect/VBench) | Tsinghua | 2024 | 16-dimension video generation benchmark |
| [VMAF](https://github.com/Netflix/vmaf) | Netflix | 2016+ | Perceptual video quality metric |
| [CLIPScore](https://arxiv.org/abs/2104.08718) | CMU | 2021 | Reference-free image-text alignment |
| [T2VQA-DB](https://arxiv.org/abs/2407.17003) | Multiple | 2024 | Text-to-video quality assessment benchmark |
| [Q-Bench-Video](https://github.com/Q-Future/Q-Bench-Video) | Multiple | 2025 | LMM video quality judgment benchmark (CVPR 2025) |
| [VGBE Workshop](https://vgbe-workshop.github.io/) | CVPR | 2026 | Video Generative Models: Benchmarks and Evaluation |

---

## External Tools & APIs

| Tool | Purpose | Cost |
|------|---------|------|
| [Google Veo 3.1](https://ai.google.dev/) | AI video generation (default) | $0.15-0.40/s |
| [Kling AI](https://klingai.com) | AI video generation (alt) | $0.50-1.50/clip |
| [Runway](https://runwayml.com) | AI video generation (alt) | $0.05-0.12/s |
| [edge-tts](https://github.com/rany2/edge-tts) | Free text-to-speech | Free |
| [Pexels API](https://www.pexels.com/api/) | Free stock footage | Free |
| [OpenAI Whisper](https://github.com/openai/whisper) | Speech-to-text for subtitles | Free (local) |
| [FFmpeg](https://ffmpeg.org/) | Video/audio processing | Free |

---

## License

MIT License — see [LICENSE](LICENSE)

## GitHub

https://github.com/joyhpc/ai-short-video-research


<br><br>

---



<!-- FILE: 01-open-source-landscape.md -->
# Open-Source Short Video Generation Landscape

> A comprehensive survey of open-source projects, frameworks, and models relevant to automated short video production. Last updated: March 2026.

---

## Executive Summary

The open-source short video generation ecosystem is large but structurally fragmented. **Every mainstream end-to-end pipeline relies on stock footage assembly** -- none integrates true AI video generation. Text-to-video models exist as standalone research artifacts with no production-ready pipeline wrapper. This creates a clear integration gap (see [05-gap-analysis.md](05-gap-analysis.md)).

---

## Tier 1 -- End-to-End Pipelines

These projects accept a topic/script and produce a finished short video with narration, subtitles, and background music.

| Project | Stars | Language / Stack | Approach | Active? | Key Limitations |
|---------|-------|-----------------|----------|---------|-----------------|
| **MoneyPrinterTurbo** | 50k+ | Python, Flask, MoviePy | Stock footage assembly from Pexels/Pixabay. LLM writes script, Edge-TTS narrates, FFmpeg composites. | Yes | No AI video generation. Minimal quality checks. Output quality depends entirely on stock footage relevance. |
| **MoneyPrinterV2** | ~15k | Python | YouTube Shorts automation. Downloads clips, re-edits with transitions, adds TTS voiceover. | Moderate | Primarily remix/repurpose workflow. Copyright risk with source material. |
| **NarratoAI** | ~8.3k | Python | Narration-focused pipeline. Stronger script generation and voice control than MoneyPrinter. | Yes | Still stock footage. Limited visual creativity. |
| **ShortGPT** | ~7.2k | Python | Early mover in LLM-driven video creation. Asset sourcing + editing pipeline. | Stalled (since 2025) | No updates. Dependencies drifting. Community moving to forks. |
| **AI-Youtube-Shorts-Generator** | ~3.1k | Python | Long-form video to short clips. Scene detection + highlight extraction. | Moderate | Long-to-short only. Not generative. |
| **short-video-maker** | ~1k | TypeScript, Remotion, MCP | Modern stack. Uses Remotion for rendering. MCP protocol integration for tool interop. | Yes | Smaller community. TypeScript ecosystem limits ML integrations. |

### Common Architecture Pattern (Tier 1)

```
Topic/Prompt
    |
    v
[LLM Script Generation] -- GPT-4 / Claude / DeepSeek / local LLM
    |
    v
[Asset Sourcing] -- Pexels / Pixabay / Storyblocks API
    |
    v
[TTS Narration] -- Edge-TTS / ElevenLabs / Azure
    |
    v
[Subtitle Generation] -- Whisper / stable-ts
    |
    v
[Composition] -- FFmpeg + MoviePy + OpenCV
    |
    v
[Output] -- MP4 (1080x1920 vertical)
```

**Key observation:** The "Asset Sourcing" step is always stock footage search, never AI video generation.

---

## Tier 2 -- Rendering Frameworks

These are not video generation tools but programmable rendering engines that can serve as the composition layer.

| Project | Stars | Language | What It Does | Strengths | Limitations |
|---------|-------|----------|-------------|-----------|-------------|
| **Remotion** | ~39.4k | TypeScript, React | Write videos as React components. Programmatic control over every frame. | Massive community. SSR support. Great for data-driven videos, explainers, motion graphics. | Not AI-native. Requires coding each template. No built-in TTS/LLM. |
| **Revideo** | ~3.7k | TypeScript | Fork of Motion Canvas. Declarative animation API. | Cleaner API than Remotion for animation-heavy content. | Smaller ecosystem. Fewer integrations. |

### When to Use a Rendering Framework

Rendering frameworks shine when you need **deterministic, template-driven output** (e.g., product ads with dynamic data). They complement AI generation rather than replacing it.

---

## Tier 3 -- Text-to-Video Models

Standalone research models that generate video from text prompts. None is integrated into an end-to-end pipeline.

| Project | Stars | Architecture | Resolution / Duration | Hardware Requirement | Quality Level |
|---------|-------|-------------|----------------------|---------------------|---------------|
| **Open-Sora** | ~28.7k | DiT (Diffusion Transformer) | Up to 720p, 2-16s | 8x A100 (full), 1x A100 (small) | Research grade. Temporal consistency issues. |
| **HunyuanVideo** | ~11.8k | Tencent's DiT variant | 720p, 5s | 1x A100 80GB | Better motion than Open-Sora. Chinese ecosystem docs. |
| **Wan 2.2** | n/a | DiT | 480-720p, 5s | 1.3B model runs on consumer GPU (RTX 3090) | Breakthrough accessibility. Quality trade-off vs larger models. |
| **CogVideoX** | ~8k+ | 3D VAE + DiT | 720p, 6s | 1x A100 | Good text adherence. Limited motion range. |
| **VideoCrafter** | ~5k | Latent Diffusion | 512x512, 2-4s | 1x A6000 | Early architecture. Surpassed by DiT models. |

### Why These Models Are Not in Pipelines

1. **Hardware barrier**: Most require A100-class GPUs, incompatible with typical pipeline deployment
2. **Generation time**: 2-10 minutes per 5-second clip at minimum
3. **Quality inconsistency**: No reliable way to ensure output matches script intent
4. **No API**: Unlike commercial offerings (Runway, Kling), these lack stable API interfaces
5. **Missing evaluation**: No built-in quality gate -- you get what you get

---

## Tier 4 -- Digital Human / Talking Head

| Project | Stars | Technique | Input | Output |
|---------|-------|-----------|-------|--------|
| **SadTalker** | ~13.6k | 3DMM + face rendering | Single photo + audio | Talking head video (256-512px) |
| **MuseV** | ~2.8k | Diffusion-based motion | Reference image + motion | Animated portrait |

These are useful for specific formats (news anchors, tutors) but do not solve general short video generation.

---

## Technical Stack Comparison

### LLM Options for Script Generation

| LLM | Cost | Latency | Script Quality | API Availability |
|-----|------|---------|---------------|-----------------|
| GPT-4o | $2.50-10/1M tokens | 1-3s | Excellent | OpenAI API |
| Claude 3.5 Sonnet | $3-15/1M tokens | 1-3s | Excellent | Anthropic API |
| DeepSeek V3 | ~$0.27/1M tokens | 2-5s | Good | DeepSeek API |
| Qwen 2.5 72B | Free (local) | 5-15s (local) | Good | Self-hosted / Dashscope |
| Llama 3.1 70B | Free (local) | 5-15s (local) | Good | Self-hosted / Groq |

### TTS Comparison

| Engine | Cost | Voice Quality | Languages | Latency | Emotional Range |
|--------|------|--------------|-----------|---------|-----------------|
| **Edge-TTS** | Free | Medium | 40+ | Low (<1s) | Limited |
| **ElevenLabs** | $5-330/mo | Excellent | 29 | Medium (2-5s) | Excellent (voice cloning) |
| **Azure TTS** | $1/100k chars | High | 140+ | Low | Good (SSML control) |
| **OpenAI TTS** | $15/1M chars | High | 50+ | Medium | Good |
| **Fish-Speech** | Free (local) | Good | 10+ | Medium (local) | Moderate |
| **ChatTTS** | Free (local) | Medium-High | 2 (EN/ZH) | Medium | Good (laughter, pauses) |

### Subtitle Generation

| Method | Accuracy | Alignment | Cost |
|--------|----------|-----------|------|
| Whisper (large-v3) | ~95% WER | Word-level via `--word_timestamps` | Free (local GPU) |
| stable-ts | ~95% WER | Improved timestamps over vanilla Whisper | Free |
| WhisperX | ~95% WER | Forced alignment for precise word boundaries | Free |
| AssemblyAI | ~97% WER | Word-level via API | $0.37/hr |

### Background Music (BGM)

| Source | Cost | Quality | Copyright Status |
|--------|------|---------|-----------------|
| Royalty-free libraries (Pixabay, Uppbeat) | Free / Freemium | Variable | Clear license |
| Suno AI | $10-30/mo | High (AI-generated) | License ambiguity |
| Udio | $10-30/mo | High (AI-generated) | License ambiguity |

**Critical gap:** No open-source pipeline integrates AI music generation. All use static royalty-free tracks or no music at all.

### Video Editing / Composition

| Tool | Role | Typical Usage |
|------|------|--------------|
| FFmpeg | Swiss army knife | Concatenation, encoding, format conversion, A/V mux |
| MoviePy | Python wrapper over FFmpeg | Clip assembly, text overlays, transitions |
| OpenCV | Frame-level processing | Scene detection, color grading, face detection |
| Pillow / PIL | Image manipulation | Thumbnail generation, text rendering |
| Remotion | Programmatic rendering | Template-based composition (TypeScript) |

---

## Key Findings

1. **ALL mainstream open-source pipelines use stock footage assembly, NOT AI video generation.** The "AI" in these tools is limited to script writing (LLM) and narration (TTS).

2. **AI Video API integration is zero.** Runway Gen-4.5, Pika, Kling 3.0, and Sora 2 all offer APIs, but no open-source pipeline integrates them.

3. **No quality evaluation exists.** None of these pipelines check whether the output video is any good. There is no feedback loop, no scoring, no retry mechanism.

4. **The technology stack is convergent.** Nearly every project uses: Python + FFmpeg + MoviePy + Whisper + some LLM API + some TTS API.

5. **Audio-video consistency is unsolved.** Stock footage is selected by keyword search, not by semantic alignment with the script. Mismatches are common and undetected.

---

## Cross-References

- For quality evaluation tools that could fill the assessment gap: [02-evaluation-tools.md](02-evaluation-tools.md)
- For self-correction patterns from academia: [03-self-correction-patterns.md](03-self-correction-patterns.md)
- For what commercial platforms do differently: [04-commercial-landscape.md](04-commercial-landscape.md)
- For the gap analysis summary: [05-gap-analysis.md](05-gap-analysis.md)
- For the proposed architecture to address these gaps: [06-architecture-proposal.md](06-architecture-proposal.md)


<br><br>

---



<!-- FILE: 02-evaluation-tools.md -->
# Video Quality Evaluation Tools -- A Comprehensive Survey

> A catalog of open-source and academic tools for assessing AI-generated video quality, with installation instructions, usage patterns, and integration guidance.

---

## Overview

The video quality evaluation ecosystem is **mature but fragmented**. Individual tools excel at narrow dimensions (aesthetic quality, temporal consistency, text alignment) but no single tool provides a holistic assessment. The opportunity lies in composing these tools into a unified quality gate (see [06-architecture-proposal.md](06-architecture-proposal.md)).

---

## Tool Catalog

### VBench -- Multi-Dimensional Video Benchmark

**What it is:** The most comprehensive open-source video evaluation suite. Developed by academic researchers, it evaluates AI-generated video across 16 orthogonal dimensions.

**Install:**
```bash
pip install vbench
# or from source:
git clone https://github.com/Vchitect/VBench.git
cd VBench && pip install -e .
```

**16 Evaluation Dimensions:**

| Category | Dimension | What It Measures |
|----------|-----------|-----------------|
| Video Quality | Subject Consistency | Does the main subject stay visually stable across frames? |
| Video Quality | Background Consistency | Does the background remain coherent? |
| Video Quality | Temporal Flickering | Are there jarring brightness/color changes between frames? |
| Video Quality | Motion Smoothness | Is motion natural and free of jitter? |
| Video Quality | Aesthetic Quality | Overall visual appeal (composition, color, lighting) |
| Video Quality | Imaging Quality | Frame-level sharpness, noise, artifacts |
| Video Quality | Dynamic Degree | Is there meaningful motion or is it a static image? |
| Condition Consistency | Overall Consistency | Combined subject + scene consistency |
| Condition Consistency | Temporal Style | Consistent visual style across time |
| Semantic | Object Class | Are the correct objects present? |
| Semantic | Multiple Objects | Can it handle multi-object scenes? |
| Semantic | Color | Are colors as specified in the prompt? |
| Semantic | Spatial Relationship | Are objects positioned correctly? |
| Semantic | Scene | Does the scene match the prompt description? |
| Semantic | Appearance Style | Does the style match (cartoon, realistic, etc.)? |
| Semantic | Human Action | Are human actions correctly rendered? |

**Usage Example:**
```python
from vbench import VBench

evaluator = VBench(device="cuda")

# Evaluate a single video against its prompt
results = evaluator.evaluate(
    video_path="output.mp4",
    prompt="A golden retriever running on a beach at sunset",
    dimensions=["subject_consistency", "temporal_flickering",
                 "motion_smoothness", "aesthetic_quality"]
)

for dim, score in results.items():
    print(f"{dim}: {score:.4f}")

# Output example:
# subject_consistency: 0.9234
# temporal_flickering: 0.8871
# motion_smoothness: 0.9012
# aesthetic_quality: 0.7845
```

**Performance:** 30-120 seconds per video depending on dimensions selected. GPU recommended.

---

### DOVER (DIVIDE) -- Dual-Branch Video Quality Assessment

**What it is:** A no-reference video quality assessment model that separates aesthetic quality from technical quality. Trained on large-scale human annotation datasets.

**Install:**
```bash
git clone https://github.com/VQAssessment/DOVER.git
cd DOVER && pip install -e .
# Download pretrained weights
python download_pretrained.py
```

**How it works:**
- **Technical branch:** Evaluates compression artifacts, noise, blur, exposure
- **Aesthetic branch:** Evaluates composition, color harmony, visual appeal
- **Combined score:** Weighted fusion of both branches

**Usage Example:**
```python
import dover

model = dover.DOVER(pretrained=True, device="cuda")

scores = model.evaluate("output.mp4")
print(f"Technical quality: {scores['technical']:.4f}")  # 0-1
print(f"Aesthetic quality: {scores['aesthetic']:.4f}")  # 0-1
print(f"Overall (DOVER):   {scores['overall']:.4f}")    # 0-1
```

**Output:** Three float scores in [0, 1]. A score above 0.7 is generally considered good quality.

**Performance:** 2-5 seconds per video. Single GPU.

---

### OpenCLIP -- Text-Video Alignment

**What it is:** Open-source CLIP implementation for measuring how well visual content matches a text description. Critical for verifying that generated video actually depicts what was requested.

**Install:**
```bash
pip install open_clip_torch
```

**Usage -- Computing Text-Video Similarity:**
```python
import open_clip
import torch
from PIL import Image
import cv2
import numpy as np

# Load model
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-H-14", pretrained="laion2b_s32b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-H-14")
model.eval()

# Extract frames from video
def extract_frames(video_path, n_frames=16):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total - 1, n_frames, dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
    cap.release()
    return frames

# Compute similarity
frames = extract_frames("output.mp4", n_frames=16)
text = tokenizer(["A golden retriever running on a beach at sunset"])

with torch.no_grad():
    frame_features = torch.stack([
        model.encode_image(preprocess(f).unsqueeze(0))
        for f in frames
    ]).squeeze(1)
    text_features = model.encode_text(text)

    # Normalize
    frame_features /= frame_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # Average similarity across frames
    similarities = (frame_features @ text_features.T).squeeze()
    avg_similarity = similarities.mean().item()

print(f"Text-video alignment: {avg_similarity:.4f}")
# Typical range: 0.20-0.35 for good alignment
```

**Performance:** 1-3 seconds for 16 frames. GPU recommended but CPU works.

---

### COVER -- Comprehensive Video Quality Evaluator

**What it is:** Successor to DOVER, designed for longer-form content evaluation. Better temporal modeling for multi-scene videos.

**Install:**
```bash
git clone https://github.com/VQAssessment/COVER.git
cd COVER && pip install -e .
```

**When to use COVER vs DOVER:**
- DOVER: Short clips (< 30s), single-scene content
- COVER: Longer videos, multi-scene content, narrative evaluation

---

### PySceneDetect -- Scene Change Detection

**What it is:** Detects scene boundaries in video. Useful for validating that transitions are intentional and not artifacts of bad generation.

**Install:**
```bash
pip install scenedetect[opencv]
```

**Usage:**
```python
from scenedetect import detect, ContentDetector

# Detect scene changes
scene_list = detect("output.mp4", ContentDetector(threshold=27.0))

print(f"Number of scenes: {len(scene_list)}")
for i, scene in enumerate(scene_list):
    print(f"  Scene {i+1}: {scene[0].get_timecode()} - {scene[1].get_timecode()}")

# For quality checking: unexpected scene changes in a continuous shot
# indicate generation artifacts
if len(scene_list) > expected_scenes:
    print("WARNING: Unexpected scene breaks detected")
```

**Performance:** Real-time or faster. CPU only.

---

### stable-ts -- Improved Whisper Timestamps

**What it is:** A wrapper around OpenAI Whisper that produces more accurate word-level timestamps. Essential for validating subtitle synchronization.

**Install:**
```bash
pip install stable-ts
```

**Usage:**
```python
import stable_whisper

model = stable_whisper.load_model("large-v3")
result = model.transcribe("audio.wav")

# Get word-level timestamps
for segment in result.segments:
    for word in segment.words:
        print(f"[{word.start:.2f} - {word.end:.2f}] {word.word}")

# Validate against existing subtitles
result.to_srt_vtt("validated_subtitles.srt")
```

**Performance:** 10-30 seconds per minute of audio. GPU recommended.

---

### imagehash -- Perceptual Frame Hashing

**What it is:** Computes perceptual hashes of images. For video QA, comparing hashes of adjacent frames detects visual consistency issues.

**Install:**
```bash
pip install imagehash
```

**Usage:**
```python
import imagehash
from PIL import Image
import cv2

def check_frame_consistency(video_path, threshold=15):
    """Detect frames with abnormal visual changes."""
    cap = cv2.VideoCapture(video_path)
    prev_hash = None
    anomalies = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        curr_hash = imagehash.phash(img)

        if prev_hash is not None:
            diff = curr_hash - prev_hash
            if diff > threshold:
                anomalies.append((frame_idx, diff))

        prev_hash = curr_hash
        frame_idx += 1

    cap.release()
    return anomalies

anomalies = check_frame_consistency("output.mp4")
if anomalies:
    print(f"Found {len(anomalies)} frame consistency anomalies")
```

**Performance:** Real-time. CPU only.

---

### pyiqa -- Frame-Level Image Quality

**What it is:** A unified interface for 30+ image quality assessment metrics. Useful for frame-level analysis of generated video.

**Install:**
```bash
pip install pyiqa
```

**Usage:**
```python
import pyiqa

# Available metrics include: musiq, clipiqa, niqe, brisque, etc.
metric = pyiqa.create_metric("musiq", device="cuda")

# Score individual frames
score = metric("frame_001.png")
print(f"Frame quality (MUSIQ): {score.item():.4f}")
```

**Performance:** 50-200ms per frame depending on metric.

---

### VF-EVAL -- MLLM-Based Video Evaluation

**What it is:** A benchmark framework that uses multimodal large language models (MLLMs) to evaluate video quality across dimensions like coherence, error perception, and reasoning.

**Key Capabilities:**
- Evaluates AI-generated video using VLMs (GPT-4V, Gemini, etc.)
- Structured rubric-based assessment
- Can detect semantic errors invisible to pixel-level metrics
- Outputs natural language explanations alongside scores

**Limitations:** Requires commercial VLM API access. Higher cost per evaluation.

---

### EvalCrafter -- Large-Scale AIGC Video Evaluation

**What it is:** An evaluation framework with 17 metrics, 700 prompts, and 10,000+ AI-generated video samples. Primarily a benchmark rather than a drop-in tool.

**Key Features:**
- 17 objective metrics covering quality, consistency, and text alignment
- Pre-computed benchmark dataset for comparing new models
- Reproducible evaluation protocol

**Best for:** Benchmarking a new generation model rather than per-video quality gating.

---

## Emerging Benchmarks (2025-2026)

The evaluation landscape is evolving rapidly. These newer benchmarks and datasets address gaps in existing tools and are worth tracking for integration.

### LGVQ / UGVQ -- Large-Scale Generated Video Quality

**What it is:** LGVQ is a dataset of 2,808 AIGC videos with human-annotated perceptual quality ratings. UGVQ is a unified model trained on LGVQ that assesses spatial quality, temporal quality, and text-video alignment in a single pass.

**Why it matters:** Previous tools evaluated dimensions separately. UGVQ integrates visual, motion, and textual features into one model, which is closer to what our Layer 2 aggregator does manually.

**Status:** Research paper published. Model weights available on HuggingFace.

**Reference:** [LGVQ arXiv](https://arxiv.org/abs/2401.14554)

---

### Q-Bench-Video -- LMM Video Quality Proficiency

**What it is:** A benchmark that tests how well Large Multimodal Models (LMMs) can judge video quality. Accepted at CVPR 2025.

**Why it matters:** Directly relevant to our Layer 3 VLM review design. Q-Bench-Video provides calibrated test data for measuring whether a VLM judge (Gemini, GPT-4o, etc.) can reliably distinguish quality levels, including AIGC-specific distortions.

**Application for this project:** Use Q-Bench-Video samples as anchor calibration data for Layer 3 VLM prompts.

---

### AIGCBench -- Image-to-Video Evaluation

**What it is:** A benchmark for evaluating image-to-video generation, covering control-video alignment, motion effects, temporal consistency, and overall quality.

**Why it matters:** As AI video APIs (Kling, Runway) often support image-to-video, this benchmark provides evaluation criteria specific to that workflow.

---

### CVPR 2026 VGBE Workshop

The **1st Workshop on Video Generative Models: Benchmarks and Evaluation (VGBE)** will be held at CVPR 2026 (June 3-7, Denver). Topics directly relevant to this project:

- **Explainable automated judges** leveraging Multimodal LLMs
- **Narrative and multi-shot evaluation suites**
- **Physics-grounded challenge sets**
- **Human preference alignment protocols**
- Challenges: Generic Instructional Video Editing + Image-to-Video Consistent Generation

**Action item:** Monitor VGBE 2026 papers (post-June) for next-generation evaluation methods that could be integrated into Layer 2/3.

**Reference:** [VGBE Workshop](https://vgbe-workshop.github.io/)

---

### Grok Imagine "Extend from Frame" -- Quality Degradation Case Study

xAI's Grok Imagine (launched Feb 2026) introduced "Extend from Frame" video chaining: the final frame of one clip becomes the starting frame of the next, enabling 30s+ AI video sequences. Community testing revealed a critical finding:

**Quality degrades after multiple chained extensions.** Users developed "Master Consistency Lock" prompt techniques to mitigate drift in motion, character appearance, and lighting.

**Relevance to this project:**
- Validates the need for our **L2 frame consistency checks** (imagehash pHash between chain boundaries)
- The quality degradation pattern is exactly what our **L3 VLM coherence review** should catch
- "Extend from Frame" workflows are a prime use case for the quality gate -- evaluate each extension before accepting it

**Reference:** [Grok Imagine Updates](https://basenor.com)

---

## Comparison Table

| Tool | Install | What It Measures | Output Format | Speed (per video) | Cost | Best For |
|------|---------|-----------------|---------------|-------------------|------|----------|
| **VBench** | pip / source | 16 dimensions (consistency, motion, aesthetics, semantics) | Dict of float scores [0-1] | 30-120s (GPU) | Free | Comprehensive multi-dimensional eval |
| **DOVER** | source | Aesthetic + technical quality | 3 floats [0-1] | 2-5s (GPU) | Free | Quick quality score |
| **OpenCLIP** | pip | Text-video semantic alignment | Float cosine similarity | 1-3s (GPU) | Free | Prompt adherence check |
| **COVER** | source | Long-form video quality | Float scores [0-1] | 5-15s (GPU) | Free | Multi-scene videos |
| **PySceneDetect** | pip | Scene boundaries | List of (start, end) timecodes | Real-time (CPU) | Free | Transition validation |
| **stable-ts** | pip | Word-level audio timestamps | SRT/VTT/JSON | 10-30s/min (GPU) | Free | Subtitle sync validation |
| **imagehash** | pip | Frame-to-frame visual consistency | Hamming distance (int) | Real-time (CPU) | Free | Flicker/artifact detection |
| **pyiqa** | pip | Frame-level image quality (30+ metrics) | Float per frame | 50-200ms/frame | Free | Frame quality screening |
| **VF-EVAL** | research | Coherence, errors, reasoning (via VLM) | Structured JSON + text | 5-30s (API) | VLM API cost | Semantic quality assessment |
| **EvalCrafter** | source | 17 metrics on AIGC video | Benchmark scores | Variable | Free | Model benchmarking |
| **UGVQ** | HuggingFace | Spatial + temporal + text alignment (unified) | Multi-dim scores | TBD | Free | Unified AIGC quality |
| **Q-Bench-Video** | research | LMM quality judgment proficiency | Calibration data | N/A | Free | VLM judge calibration |
| **AIGCBench** | research | I2V control alignment + temporal consistency | Benchmark scores | Variable | Free | Image-to-video eval |

---

## Integration Patterns

### Unified Quality Score

The key challenge is combining scores from different tools into a single actionable signal. The recommended approach:

```
Quality Gate Score = w1 * DOVER_overall
                   + w2 * OpenCLIP_similarity
                   + w3 * VBench_subset_avg
                   + w4 * (1 - flickering_anomaly_rate)
                   + w5 * subtitle_sync_accuracy
```

Where weights are configurable via YAML (see [06-architecture-proposal.md](06-architecture-proposal.md) Layer 2).

### Tiered Evaluation (Cost Optimization)

Inspired by the Netflix VMAF pipeline pattern (see [03-self-correction-patterns.md](03-self-correction-patterns.md)):

```
Layer 1: Programmatic checks (ffprobe, imagehash, pysrt)
    |
    PASS? --yes--> Layer 2: ML model checks (DOVER, OpenCLIP, VBench subset)
    |                  |
    FAIL               PASS? --yes--> Output
    |                  |
    v                  FAIL/UNCERTAIN
  Retry                    |
                           v
                      Layer 3: VLM review (Gemini / GPT-4V)
                           |
                        PASS? --yes--> Output
                           |
                           FAIL --> Correction Agent --> Retry
```

This pattern ensures that **99% of obviously bad outputs are caught cheaply** before expensive VLM evaluation is invoked.

### Tool Selection by Use Case

| Scenario | Recommended Tools | Why |
|----------|-------------------|-----|
| Quick pass/fail gate | DOVER + imagehash | Fast, cheap, catches major issues |
| Prompt adherence | OpenCLIP | Directly measures text-visual alignment |
| Temporal quality | VBench (subject_consistency + temporal_flickering + motion_smoothness) | Purpose-built for video temporal analysis |
| Subtitle validation | stable-ts + pysrt | Verifies timing accuracy |
| Deep quality review | VF-EVAL / VLM structured review | Catches semantic issues metrics miss |
| Model comparison | EvalCrafter + VBench full suite | Standardized benchmarking |

---

## Cross-References

- For how these tools fit into a quality gate architecture: [06-architecture-proposal.md](06-architecture-proposal.md)
- For self-correction patterns that use evaluation feedback: [03-self-correction-patterns.md](03-self-correction-patterns.md)
- For the gap these tools address in current pipelines: [05-gap-analysis.md](05-gap-analysis.md)


<br><br>

---



<!-- FILE: 03-self-correction-patterns.md -->
# Self-Correction Patterns for AI Video Generation

> Deep analysis of evaluation-correction feedback loops from academic research, industry practice, and production systems. These patterns form the theoretical foundation for the architecture proposed in [06-architecture-proposal.md](06-architecture-proposal.md).

---

## Why Self-Correction Matters

AI video generation is inherently stochastic. Even the best models produce unsatisfactory output 20-40% of the time. Without a correction loop, the only option is to generate and hope. Self-correction transforms the problem from "roll the dice" to "converge on quality."

The key insight across all patterns below: **evaluation capability is more important than generation capability.** If you can reliably tell whether output is good, you can iterate to quality even with a mediocre generator.

---

## Pattern 1: VISTA -- Multi-Agent Video Generation Review (Google, 2025)

### Architecture

```
                    +------------------+
                    |  Generation      |
                    |  (Veo 3)         |
                    +--------+---------+
                             |
              +--------------v--------------+
              |                             |
    +---------v---------+   +---------------v-----------+
    | Visual Fidelity   |   | Audio Fidelity            |
    | Reviewer          |   | Reviewer                  |
    +---------+---------+   +---------------+-----------+
              |                             |
              +---------+   +--------------+
                        |   |
                  +-----v---v-----+
                  | Context       |
                  | Preservation  |
                  | Reviewer      |
                  +------+--------+
                         |
                  +------v--------+
                  | Reasoning     |
                  | Agent         |
                  | (Gemini 2.5)  |
                  +------+--------+
                         |
                    +----v----+
                    | Re-gen  |  (if needed)
                    +---------+
```

### Key Insights

1. **Three specialized reviewers** evaluate different quality dimensions independently:
   - **Visual fidelity reviewer:** Checks for artifacts, consistency, motion quality
   - **Audio fidelity reviewer:** Checks audio quality, sync, naturalness
   - **Context preservation reviewer:** Verifies the output matches intent and context

2. **Critical distinction: "model capability limit" vs "imprecise prompt."** The reasoning agent must determine whether a failure is because the model cannot do what was asked (capability limit) or because the prompt was ambiguous/insufficient. This distinction determines the retry strategy:
   - Capability limit: Simplify the request, use fallback, or accept degraded output
   - Imprecise prompt: Refine the prompt and regenerate

3. **Results:** 60% win rate improvement over single-pass generation. 66.4% human preference for VISTA-corrected output over uncorrected.

4. **Limitations:** Not open source. Requires Veo 3 (Google's proprietary video model) and Gemini 2.5 Flash. The pattern is transferable; the implementation is not.

### Transferable Lessons

- Separate evaluation into independent dimensions
- Build a reasoning layer that interprets evaluation signals and decides on action
- Distinguish between generation failures and specification failures
- Cap retry attempts to prevent infinite loops

---

## Pattern 2: Anthropic Evaluator-Optimizer Pattern

### Architecture

```
Input
  |
  v
[Generator] --> Output
                  |
                  v
              [Evaluator]
                  |
            +-----+-----+
            |           |
          PASS        FAIL
            |           |
            v           v
        Output    [Structured Feedback]
                        |
                        v
                  [Optimizer / Corrector]
                        |
                        v
                  [Generator] --> (retry with corrected prompt)
```

### Key Principles

1. **Evaluation criteria must be expressible.** If you cannot write down what "good" means, you cannot evaluate it. For video, this means defining concrete rubrics (resolution, motion smoothness, text alignment) rather than vague "quality."

2. **Feedback must be structured and actionable.** A score alone is not enough. The evaluator must output:
   - What specifically is wrong
   - Why it is wrong
   - What would fix it

3. **The optimizer translates feedback into generation parameters.** It does not just retry -- it modifies the prompt, parameters, or approach based on the structured feedback.

### Application to Video

```python
# Pseudocode for evaluator-optimizer loop
class VideoEvaluator:
    def evaluate(self, video, prompt, criteria):
        return {
            "pass": False,
            "scores": {"visual": 0.6, "alignment": 0.4, "audio": 0.8},
            "feedback": [
                {
                    "dimension": "alignment",
                    "issue": "Video shows a lake but prompt specifies ocean",
                    "severity": "major",
                    "suggestion": "Add 'ocean waves, saltwater, beach' to prompt"
                }
            ]
        }

class PromptOptimizer:
    def optimize(self, original_prompt, feedback):
        # Use LLM to rewrite prompt incorporating feedback
        return corrected_prompt
```

---

## Pattern 3: Netflix VMAF Pipeline -- Tiered Gating

### Architecture

```
Generated Video
     |
     v
[Tier 1: Cheap Checks]  <-- File valid? Resolution correct? Duration match?
     |                       Audio present? Codec correct?
     |
   PASS? --no--> REJECT (instant, zero cost)
     |
    yes
     |
     v
[Tier 2: Compute Checks] <-- VMAF score, bitrate analysis
     |                        scene complexity metrics
     |
   PASS? --no--> RE-ENCODE or REJECT
     |
    yes
     |
     v
[Tier 3: Perceptual]     <-- Human QA sample, A/B testing
     |
   PASS? --> SHIP or REJECT
```

### Key Insight

**99% of issues are caught by cheap checks.** Netflix found that running expensive perceptual quality assessment on every asset was wasteful because the vast majority of failures were detectable by simple programmatic checks (wrong format, corrupted file, missing audio track).

### Application to AI Video

Map this pattern to AI video generation:
- **Tier 1 (< 1 second, zero cost):** ffprobe validation, file size, duration, resolution, audio stream presence
- **Tier 2 (1-10 seconds, low cost):** DOVER score, OpenCLIP alignment, imagehash consistency
- **Tier 3 (5-30 seconds, higher cost):** VLM structured review

This tiered approach is the foundation of the three-layer quality gate in [06-architecture-proposal.md](06-architecture-proposal.md).

---

## Pattern 4: DALL-E 3 -- Defense in Depth

### Six-Layer Safety/Quality Pipeline

| Layer | Stage | What It Does | Analogous Video Check |
|-------|-------|-------------|----------------------|
| 1 | Input validation | Prompt safety + feasibility check | Script validation, prompt engineering |
| 2 | Prompt rewriting | LLM rewrites user prompt for better generation | Script-to-visual-prompt translation |
| 3 | Mid-generation rejection | Classifier on intermediate latents | N/A (not applicable to API-based generation) |
| 4 | Output classifier | Multi-label classification on final output | DOVER + OpenCLIP + content safety |
| 5 | Bias mitigation | Demographic balance, representation | Content diversity check |
| 6 | Metadata + watermarking | C2PA provenance | AIGC watermarking |

### Transferable Lessons

- **Pre-generation optimization (prompt rewriting) prevents many failures.** Spending compute on a better prompt is cheaper than regenerating.
- **Multiple independent classifiers catch different failure modes.** No single check catches everything.
- **Defense in depth means any single layer failing is not catastrophic.**

---

## Pattern 5: LangGraph State Machine -- Conditional Retry

### Architecture

```python
from langgraph.graph import StateGraph, END

class VideoState(TypedDict):
    script: str
    prompt: str
    video_path: str
    quality_scores: dict
    feedback: str
    revision_count: int
    max_revisions: int

def generate_video(state: VideoState) -> VideoState:
    # Generate video from prompt
    ...

def evaluate_quality(state: VideoState) -> VideoState:
    # Run quality checks, populate quality_scores
    ...

def should_retry(state: VideoState) -> str:
    if state["revision_count"] >= state["max_revisions"]:
        return "output_best"
    if state["quality_scores"]["overall"] >= 0.7:
        return "pass"
    if state["quality_scores"]["overall"] < 0.3:
        return "fail_hard"
    return "retry"

def correct_prompt(state: VideoState) -> VideoState:
    # Use VLM feedback to rewrite prompt
    state["revision_count"] += 1
    ...

graph = StateGraph(VideoState)
graph.add_node("generate", generate_video)
graph.add_node("evaluate", evaluate_quality)
graph.add_node("correct", correct_prompt)
graph.add_node("output", output_video)

graph.set_entry_point("generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges("evaluate", should_retry, {
    "pass": "output",
    "retry": "correct",
    "output_best": "output",
    "fail_hard": END
})
graph.add_edge("correct", "generate")
```

### Key Design Decision: MAX_REVISIONS

Without a revision cap, the loop can run indefinitely (burning API credits and time). Recommended values:

| Generation Cost | Max Revisions | Rationale |
|----------------|---------------|-----------|
| Low (stock footage) | 3-5 | Cheap to retry, but diminishing returns |
| Medium (AI video API) | 2-3 | Each attempt costs $0.50-5.00 |
| High (local model, GPU time) | 1-2 | Minutes per attempt, high opportunity cost |

---

## Pattern 6: LLM-as-Judge Calibration

### The Problem

Using LLMs to judge quality seems natural, but uncalibrated LLM scoring introduces systematic biases:

- **Mean regression:** Numerical scales (1-10) cluster around 6-7 regardless of actual quality
- **Position bias:** First-presented options are favored
- **Verbosity bias:** Longer outputs are rated higher
- **Self-enhancement bias:** LLMs rate their own output higher

**Critical finding:** Uncalibrated LLM-as-judge scores can **reverse model rankings**, making a worse model appear better.

### Calibration Best Practices

1. **Use binary or ternary scales, not numerical:**
   - Binary: PASS / FAIL
   - Ternary: GOOD / ACCEPTABLE / POOR
   - Avoid: "Rate from 1 to 10"

2. **Provide anchor samples:**
   ```
   Here are calibration examples:
   - [Video A description]: This is a GOOD example because...
   - [Video B description]: This is a POOR example because...
   - [Video C description]: This is ACCEPTABLE because...

   Now evaluate the following video:
   ```

3. **Chain-of-thought before scoring:**
   ```
   First describe what you observe in the video.
   Then identify any quality issues.
   Finally, provide your assessment: GOOD, ACCEPTABLE, or POOR.
   ```
   Forcing reasoning before the label reduces snap judgments.

4. **Structured output format:**
   ```json
   {
     "observations": "The video shows a dog running...",
     "issues": ["slight motion blur in frames 45-60", "background inconsistency at 0:03"],
     "dimension_scores": {
       "visual_fidelity": "GOOD",
       "content_alignment": "ACCEPTABLE",
       "narrative_coherence": "GOOD"
     },
     "overall": "ACCEPTABLE",
     "corrective_feedback": "Regenerate with emphasis on background stability..."
   }
   ```

---

## Pattern 7: FilmAgent -- Multi-Agent Crew Simulation

### Architecture

A multi-agent system where specialized agents play different filmmaking roles:

| Agent | Role | Evaluates / Decides |
|-------|------|-------------------|
| Director | Creative vision | Overall coherence, pacing, narrative arc |
| Writer | Script quality | Dialogue, narration, story structure |
| Cinematographer | Visual composition | Framing, lighting, camera movement |
| Actor | Performance | Expression, timing, emotional delivery |
| Editor | Assembly quality | Transitions, rhythm, flow |

### Key Insight

Role specialization improves evaluation quality because each agent focuses on a narrow domain with clear expertise boundaries. However, this pattern has high latency (multiple LLM calls per evaluation cycle) and is most suitable for high-value content where quality justifies cost.

---

## Pattern 8: VideoAgent -- Self-Conditional Consistency

### Approach

1. Generate a keyframe from the prompt
2. Use the keyframe as a visual condition for subsequent generation
3. After generation, a VLM verifies consistency between the keyframe and the generated video
4. If inconsistent, regenerate conditioned more strongly on the keyframe

### Key Insight

**Self-conditioning reduces the search space.** Instead of evaluating arbitrary output, the system first establishes what "good" looks like (the keyframe) and then verifies conformance to that reference.

---

## Pattern 9: VF-EVAL + RePrompt -- Feedback-Driven Prompt Rewriting

### Approach

1. Generate video from prompt
2. VF-EVAL (MLLM-based) evaluates the video and produces structured critique
3. The critique is used to automatically rewrite the prompt
4. Regenerate with the improved prompt

### Example Flow

```
Original prompt: "A cat sitting on a windowsill watching rain"

VF-EVAL output:
  - Coherence: GOOD
  - Error: "Cat appears to float slightly above the windowsill"
  - Reasoning: "Physics inconsistency in object placement"

RePrompt output: "A cat sitting firmly on a windowsill, paws resting on
the surface, looking out through a rain-streaked window. Realistic
physics, cat's weight visible on the cushion."
```

### Key Insight

Prompt engineering is the cheapest form of correction. Before regenerating (which is expensive), always try prompt refinement first.

---

## Best Practices Checklist

1. **Separate evaluation into independent dimensions.** Do not try to compute a single holistic quality score directly. Evaluate visual quality, audio quality, text alignment, and narrative coherence independently, then aggregate.

2. **Use tiered gating (cheap checks first).** Run programmatic checks before ML models before VLM review. 99% of failures are catchable cheaply.

3. **Cap retry attempts.** Set MAX_REVISIONS based on generation cost. Never allow infinite loops.

4. **Distinguish capability limits from prompt failures.** When evaluation fails, determine whether the generation model cannot do what was asked (simplify the request) or whether the prompt was insufficient (refine the prompt).

5. **Produce structured, actionable feedback.** Scores alone are not enough. The evaluator must output what is wrong, why, and how to fix it.

6. **Calibrate LLM judges.** Use binary/ternary scales, provide anchor samples, require chain-of-thought reasoning before scoring.

7. **Pre-generation optimization beats post-generation correction.** Invest in prompt quality, script validation, and parameter tuning before generating.

8. **Log everything.** Store every generation attempt, its evaluation scores, the feedback produced, and the corrected prompt. This data is invaluable for improving the system over time.

9. **Design for graceful degradation.** When retries are exhausted, output the best version with a quality warning rather than failing silently or blocking indefinitely.

10. **Human-in-the-loop as final escalation.** After N consecutive POOR ratings, escalate to human review rather than burning more compute.

---

## Cross-References

- For the evaluation tools that implement these patterns: [02-evaluation-tools.md](02-evaluation-tools.md)
- For the architecture that combines these patterns: [06-architecture-proposal.md](06-architecture-proposal.md)
- For why these patterns are needed (gap analysis): [05-gap-analysis.md](05-gap-analysis.md)


<br><br>

---



<!-- FILE: 04-commercial-landscape.md -->
# Commercial AI Video Landscape

> A survey of commercial platforms for AI video generation, digital humans, and automated short video production. Organized by segment with pricing, capabilities, and competitive analysis.

---

## Market Segmentation

The commercial AI video market can be segmented into five categories:

| Segment | Core Capability | Target User | Price Range |
|---------|----------------|-------------|-------------|
| **AI Video Engines** | Text/image-to-video generation | Creators, studios | $12-100/mo |
| **Digital Human / Avatar** | Synthetic talking head video | Enterprise, marketing | $29-1000+/mo |
| **One-Click Video** | Prompt-to-complete-video | SMBs, social media managers | $10-50/mo |
| **Long-to-Short** | Extract highlights from long content | YouTubers, podcasters | $10-40/mo |
| **E-commerce Ad** | Product URL-to-video-ad | E-commerce sellers | $25-200/mo |

---

## International Players

### AI Video Engines

#### Runway Gen-4.5

| Attribute | Detail |
|-----------|--------|
| **Category** | Text/image-to-video generation |
| **Quality** | Film-grade. Industry leader in visual quality and consistency. |
| **Key Features** | Text-to-video, image-to-video, video-to-video, motion brush, camera controls, multi-reference character consistency |
| **Resolution** | Up to 4K upscale, native 1080p |
| **Duration** | Up to 40 seconds per generation |
| **API** | Yes. Runway API with per-second pricing. |
| **Pricing** | Standard $12/mo (625 credits), Pro $28/mo, Unlimited $76/mo |
| **Strengths** | Best-in-class visual quality. Strong motion. Professional-grade output. |
| **Weaknesses** | Expensive at scale. Text rendering still imperfect. API latency 60-120s. |

#### Sora 2 (OpenAI)

| Attribute | Detail |
|-----------|--------|
| **Category** | Text/image-to-video generation |
| **Quality** | Comparable to Runway. Strong in complex scene understanding. |
| **Key Features** | Text-to-video, image-to-video, storyboard mode, style presets |
| **Resolution** | Up to 1080p |
| **Duration** | Up to 20 seconds |
| **API** | Limited API access (as of early 2026) |
| **Pricing** | Included in ChatGPT Plus ($20/mo) with limits; Pro ($200/mo) for higher volume |
| **Strengths** | Strong scene comprehension. Bundled with ChatGPT ecosystem. |
| **Weaknesses** | Limited availability. Inconsistent motion in complex scenes. |

---

### Digital Human / Avatar

#### Synthesia

| Attribute | Detail |
|-----------|--------|
| **Category** | Enterprise digital human |
| **Quality** | Industry leader for avatar-based video |
| **Key Features** | 250+ stock avatars, custom avatar creation (enterprise), 140+ languages, script-to-video, brand kit |
| **Resolution** | 1080p |
| **API** | Yes. Full API for programmatic video creation. |
| **Pricing** | Starter $29/mo, Creator $89/mo, Enterprise custom |
| **Strengths** | Largest avatar library. Enterprise-grade security. SOC 2 compliant. |
| **Weaknesses** | Avatars still look synthetic. Limited non-avatar capabilities. Expensive at scale. |

#### HeyGen

| Attribute | Detail |
|-----------|--------|
| **Category** | Digital human + video translation |
| **Key Features** | Avatar creation, video translation with lip sync, instant avatar from 2-min video, streaming avatar |
| **Pricing** | Creator $29/mo, Business $89/mo, Enterprise custom |
| **Strengths** | Best lip-sync quality. Video translation feature is unique. Fast avatar creation. |
| **Weaknesses** | Avatar realism varies. Real-time streaming avatar quality inconsistent. |

#### D-ID

| Attribute | Detail |
|-----------|--------|
| **Category** | Avatar + interactive AI |
| **Key Features** | Photo-to-talking-head, interactive avatar (real-time conversation), API-first |
| **Pricing** | Lite $5.90/mo, Pro $49/mo, Enterprise custom |
| **Strengths** | Interactive avatar for customer service. Good API. Low entry price. |
| **Weaknesses** | Lower visual quality than Synthesia/HeyGen. |

---

### One-Click Video (Prompt to Complete Video)

#### InVideo AI

| Attribute | Detail |
|-----------|--------|
| **Category** | Prompt-to-complete-video |
| **Key Features** | Text prompt to full video (script + stock footage + voiceover + music + subtitles), edit via chat, 5000+ templates |
| **Resolution** | Up to 1080p |
| **Pricing** | Free tier (watermarked), Plus $25/mo, Max $50/mo |
| **Strengths** | Closest to the "one prompt, one video" vision. Good template variety. Conversational editing (chat to modify). |
| **Weaknesses** | Stock footage based (no AI generation). Template-dependent quality. |

#### Fliki

| Attribute | Detail |
|-----------|--------|
| **Category** | Text-to-video with strong TTS |
| **Key Features** | Blog/article-to-video, 2000+ voices, stock footage assembly, AI art option |
| **Pricing** | Standard $28/mo, Premium $88/mo |
| **Strengths** | Best TTS voice variety. Blog-to-video workflow. |
| **Weaknesses** | Similar stock footage approach as others. AI art integration basic. |

---

### Long-to-Short

#### Opus Clip

| Attribute | Detail |
|-----------|--------|
| **Category** | Long-form to short-form clip extraction |
| **Key Features** | AI virality score (1-100), auto-captioning, multi-clip extraction from single video, reframing |
| **Pricing** | Starter $19/mo, Growth $39/mo |
| **Strengths** | AI virality scoring is unique. Clean UI. Good auto-captioning. |
| **Weaknesses** | Not generative. Quality limited by source material. |

---

### E-commerce Ad

#### Creatify

| Attribute | Detail |
|-----------|--------|
| **Category** | URL-to-video-ad generation |
| **Key Features** | Paste product URL, AI generates video ad with avatar spokesperson, A/B variant generation, batch creation |
| **Pricing** | Starter $29/mo, Growth $99/mo, Enterprise custom |
| **Strengths** | URL-to-ad pipeline is innovative. A/B testing built in. E-commerce focused. |
| **Weaknesses** | Narrow use case. Avatar quality mid-range. |

---

## China Ecosystem

The Chinese market has a distinct and rapidly evolving set of players, often more tightly integrated with distribution platforms (Douyin/TikTok, Kuaishou, WeChat).

### Jimeng (即梦) -- ByteDance

| Attribute | Detail |
|-----------|--------|
| **Parent** | ByteDance (字节跳动) |
| **Category** | One-click video creation + AI image generation |
| **Key Features** | One-click script generation, AI music selection, automatic transitions, Douyin ecosystem integration, text-to-image, image-to-video |
| **Pricing** | 69 CNY/mo (~$9.50/mo) |
| **Strengths** | Deep Douyin integration. Low cost. ByteDance's distribution advantage. Fast iteration. |
| **Weaknesses** | Primarily Douyin-optimized. International availability limited. Quality below Runway/Kling for pure video generation. |
| **Significance** | Represents the platform-integrated approach: generation + distribution in one ecosystem. |

### Kling 3.0 (可灵) -- Kuaishou

| Attribute | Detail |
|-----------|--------|
| **Parent** | Kuaishou (快手) |
| **Category** | AI video engine + multimodal editing |
| **Key Features** | DiT architecture, text-to-video, image-to-video, video continuation, native audio generation with lip sync, multi-shot consistency, multimodal editing, camera controls |
| **Resolution** | Up to 1080p |
| **Duration** | Up to 3 minutes (extended generation) |
| **API** | Yes. Kling API available internationally. |
| **Pricing** | 46 CNY/mo (~$6.30/mo) domestic, international pricing varies |
| **Strengths** | Best-in-class for audio-video integration (native audio + lip sync). Multi-shot consistency is rare. Price/quality ratio excellent. Strong API. |
| **Weaknesses** | Text rendering weak. Occasional physics inconsistencies. |
| **Significance** | First commercial platform to ship native audio-video generation. Sets the bar for integrated AV output. |

### Tongyi Wanxiang (通义万相) -- Alibaba

| Attribute | Detail |
|-----------|--------|
| **Parent** | Alibaba Cloud (阿里云) |
| **Category** | Text-to-video + creative content |
| **Key Features** | Text-to-video generation, art/cultural content specialization, integration with Alibaba Cloud AI services |
| **Pricing** | Pay-per-use via Alibaba Cloud |
| **Strengths** | Good for art/cultural content (Chinese art styles, calligraphy, traditional aesthetics). Enterprise cloud integration. |
| **Weaknesses** | Narrower general-purpose video quality. Less community attention. |

### Zhipu Qingying (智谱清影) -- ZhipuAI

| Attribute | Detail |
|-----------|--------|
| **Parent** | ZhipuAI (智谱AI) |
| **Category** | Science/educational video generation |
| **Key Features** | Text-to-video, specialization in scientific visualization and educational content, based on CogVideoX lineage |
| **Free Tier** | Yes (limited usage) |
| **Strengths** | Free tier for experimentation. Good for science/education content. Strong research pedigree (CogVideoX → CogVideoX-5B → Qingying). |
| **Weaknesses** | Not general purpose. Limited creative range. |

### Hailuo AI (海螺AI) -- MiniMax

| Attribute | Detail |
|-----------|--------|
| **Parent** | MiniMax (稀宇科技) |
| **Category** | Video generation + virtual idol |
| **Key Features** | Smooth character motion, virtual idol generation, API-first design, international presence |
| **API** | Yes. Well-documented API. |
| **Strengths** | Smoothest character motion among Chinese players. API-first approach enables integration. Virtual idol / vtuber niche. |
| **Weaknesses** | Smaller model behind some competitors. Scene diversity limited. |

---

## Capability Comparison Matrix

| Capability | Runway | Sora 2 | Synthesia | Kling 3.0 | Jimeng | InVideo | Open Source (best) |
|-----------|--------|--------|-----------|-----------|--------|---------|-------------------|
| Text-to-video quality | 9/10 | 8/10 | N/A | 8/10 | 6/10 | N/A | 5/10 (Open-Sora) |
| Multi-shot consistency | 7/10 | 6/10 | 8/10 | 8/10 | 5/10 | N/A | 0/10 |
| Native audio generation | No | No | TTS only | Yes | Partial | TTS only | No |
| Lip sync | No | No | Yes | Yes | No | No | SadTalker (basic) |
| Self-evaluation / QA | Internal | Internal | Internal | Internal | Unknown | Unknown | None |
| Feedback/correction loop | Internal | Internal | N/A | Internal | Unknown | Unknown | None |
| API available | Yes | Limited | Yes | Yes | Limited | No | N/A |
| Cost per minute of video | $0.50-5 | ~$0.25-2 | $1-10 | $0.10-1 | $0.05-0.5 | $0.25-1 | Free (compute only) |
| End-to-end pipeline | No | No | Partial | Partial | Yes | Yes | Yes (stock only) |

---

## Gap Analysis: Commercial vs Open Source

| What Commercial Has | What Open Source Lacks |
|--------------------|----------------------|
| **Quality control systems** (internal evaluation, automated QA) | Zero quality evaluation in any pipeline |
| **Feedback loops** (regenerate on failure, prompt correction) | No retry, no correction, no feedback |
| **Multi-shot consistency** (character/scene persistence across clips) | Each clip is independent, no consistency |
| **Native audio-video** (Kling 3.0 generates audio with video) | Audio and video are completely separate tracks |
| **Professional templates** (motion graphics, transitions, branding) | Basic FFmpeg transitions at best |
| **Scale infrastructure** (GPU clusters, CDN, caching) | Single-machine, single-user |
| **Content safety** (moderation, watermarking, compliance) | Minimal or none |

The implication is clear: the gap is not in generation capability (open-source models are competitive) but in **production infrastructure** -- particularly quality control and feedback loops. See [05-gap-analysis.md](05-gap-analysis.md) for a detailed analysis.

---

## Cross-References

- For open-source alternatives: [01-open-source-landscape.md](01-open-source-landscape.md)
- For evaluation tools that could close the quality gap: [02-evaluation-tools.md](02-evaluation-tools.md)
- For the detailed gap analysis: [05-gap-analysis.md](05-gap-analysis.md)
- For an architecture proposal to bridge the gap: [06-architecture-proposal.md](06-architecture-proposal.md)


<br><br>

---



<!-- FILE: 05-gap-analysis.md -->
# Gap Analysis -- Where Open Source Falls Short

> A structured analysis of the gaps between what exists in open-source AI video tooling and what is needed for production-quality automated short video generation. This document identifies the opportunity window for a new system.

---

## Gap Map

```
                    Self-Evaluation Capability
                    ^
                    |
          HIGH      |   [Academic Research]
                    |     VISTA, VF-EVAL,
                    |     VideoAgent, FilmAgent
                    |        *
                    |
                    |              +========================+
                    |              |                        |
          MEDIUM    |              |   OPPORTUNITY WINDOW   |
                    |              |                        |
                    |              |   Production system    |
                    |              |   with evaluation +    |
                    |              |   AI video generation  |
                    |              |                        |
                    |              +========================+
                    |
                    |                         [Commercial]
          LOW       |   [Open Source Tools]    Runway, Kling,
                    |    MoneyPrinter,         Synthesia
                    |    ShortGPT, etc.          *
                    |       *
                    |
                    +-------+--------+--------+--------+----> AI Video Integration
                          NONE     BASIC    PARTIAL   FULL

    Legend:
      * = Cluster of existing solutions
      [Box] = Opportunity window for new system
```

**Reading the map:**
- Open-source tools (bottom-left) have no AI video integration and no self-evaluation
- Academic research (top-left) has strong evaluation but uses proprietary models, not integrated into tools
- Commercial platforms (bottom-right) have AI video but closed evaluation systems
- The opportunity window (center) is a system combining open-source accessibility with academic-grade evaluation and AI video integration

---

## Five Major Gaps

### Gap 1: AI Video Generation API Integration

**Current state:** Zero open-source projects integrate AI video generation APIs (Runway, Kling, Sora, Pika) into an end-to-end pipeline. Every pipeline uses stock footage assembly.

**Why it matters:** Stock footage creates a quality ceiling. The visual content is limited to what exists in stock libraries, and keyword-based search frequently returns irrelevant footage.

**Why it has not been done:**
- API costs ($0.10-5.00 per clip) make development expensive
- No quality gate means no way to know if generated clips are usable before assembling them
- API latency (30-120 seconds per clip) requires async pipeline architecture
- Rate limits and availability are inconsistent

**What closing this gap requires:**
- Multi-provider abstraction layer (Runway, Kling, Sora, with fallback)
- Async generation pipeline with progress tracking
- Per-clip quality evaluation before assembly
- Cost management and budgeting

**Addressable impact:** Transforms output from "stock footage slideshow" to "AI-generated visual narrative." Qualitative leap in output quality and uniqueness.

---

### Gap 2: Self-Evaluation Closed Loop

**Current state:** Academic research has validated that evaluation-correction loops dramatically improve output quality (VISTA: 60% win rate improvement, 66.4% human preference). Zero open-source implementations exist.

**Why it matters:** Without evaluation, there is no way to know whether output is good. Without correction, there is no way to improve bad output. The pipeline is open-loop: generate once, output whatever comes out, hope for the best.

**Why it has not been done:**
- Evaluation requires combining multiple specialized tools (see [02-evaluation-tools.md](02-evaluation-tools.md))
- No agreed-upon "quality score" standard for AI video
- Correction requires structured feedback generation (not just a score)
- Building the loop requires orchestration infrastructure (state machine, retry logic)

**What closing this gap requires:**
- Three-layer quality gate (programmatic, ML, VLM) -- see [06-architecture-proposal.md](06-architecture-proposal.md)
- Structured feedback generation from evaluation results
- Correction agent that translates feedback into improved prompts/parameters
- LangGraph or similar orchestration for the retry state machine

**Addressable impact:** Based on VISTA results, expect 40-60% improvement in output quality consistency. Turns unpredictable output into reliable output.

---

### Gap 3: AI Background Music Generation

**Current state:** AI music generation has advanced rapidly (Suno, Udio produce high-quality music from text prompts). No open-source video pipeline integrates AI music generation.

**Current approach:** Pipelines either use no music, or select from a fixed library of royalty-free tracks by keyword matching.

**Why it has not been done:**
- Copyright status of AI-generated music is legally uncertain
- Suno/Udio APIs are limited or nonexistent
- Music selection requires understanding video mood/pacing (multimodal reasoning)
- Open-source music generation models (MusicGen, Stable Audio) produce lower quality

**What closing this gap requires:**
- Integration with AI music API (Suno/Udio) or local model (MusicGen)
- Mood/tempo matching between video content and music
- Legal framework for commercial use of AI-generated music
- Audio mixing (music volume relative to narration)

**Addressable impact:** Music is a significant contributor to perceived video quality. Properly matched music transforms amateur-feeling output into professional-feeling output. Risk: copyright uncertainty.

---

### Gap 4: Multi-Shot Consistency

**Current state:** When a video consists of multiple clips (which all short videos do), there is no mechanism to maintain visual consistency across clips. Characters may change appearance, environments shift style, color grading varies.

**Only commercial solutions:** Kling 3.0 and Runway Gen-4.5 offer multi-reference character consistency. No open-source solution exists.

**Why it matters:** Visual inconsistency across shots is one of the most noticeable quality problems. It immediately signals "AI-generated" to viewers.

**What closing this gap requires:**
- Character reference conditioning (provide reference images for consistent characters)
- Style embedding extraction and application across shots
- Scene continuity validation (color grading, lighting, environment)
- This is partially a generation model capability and partially a pipeline concern

**Addressable impact:** Visual coherence across a 60-second video with 8-12 shots. Currently the weakest aspect of any AI-generated multi-shot content.

---

### Gap 5: End-to-End Native Audio-Video

**Current state:** Open-source pipelines treat audio and video as completely separate tracks. Video is generated (or sourced), audio is generated (TTS + BGM), and they are mechanically combined via FFmpeg muxing.

**What commercial platforms do:** Kling 3.0 generates audio natively alongside video, including lip-sync. This produces naturally integrated audio-video output.

**Why it matters:** Mismatched audio and video is immediately perceivable:
- Narration pacing does not match visual pacing
- Sound effects do not correspond to on-screen events
- Lip sync is impossible without integrated generation
- Emotional tone of voice may not match visual mood

**What closing this gap requires:**
- At minimum: audio-visual pacing alignment (match narration timing to scene durations)
- Better: scene-aware audio design (ambient sounds, effects)
- Best: native audio-video generation (requires model-level integration, not pipeline-level)
- Validation: A/V sync checking as part of quality gate

**Addressable impact:** Significant improvement in perceived quality. Audio-visual coherence is one of the top factors in viewer engagement.

---

## Common Failure Modes

These are the specific failure types observed in open-source pipeline output:

| Failure Mode | Frequency | Cause | Detection Method | Correction Approach |
|-------------|-----------|-------|-----------------|-------------------|
| **Audio-video sync drift** | ~10% of outputs | FFmpeg muxing timing error, TTS duration mismatch | PTS timestamp comparison (ffprobe) | Re-mux with corrected offsets |
| **Audio truncation** | ~15% of outputs | TTS output shorter than video duration | Duration comparison (ffprobe) | Regenerate TTS with adjusted speed, or trim video |
| **Visual-semantic deviation** | ~20% of outputs | Stock footage keyword search returns irrelevant clips | OpenCLIP text-image similarity | Replace clip with better match, or use AI generation |
| **Subtitle misalignment** | ~10% of outputs | Whisper timestamp inaccuracy | stable-ts validation against audio | Re-align with stable-ts or WhisperX |
| **Narrative coherence break** | ~25% of outputs | Script structure not reflected in visual sequence | VLM review (requires expensive check) | Reorder clips or regenerate script |
| **Resolution/format mismatch** | ~5% of outputs | Mixed source material resolutions | ffprobe validation | Normalize to target resolution before assembly |
| **Abrupt transitions** | ~15% of outputs | No transition logic, hard cuts between unrelated clips | PySceneDetect analysis | Add transition effects or regenerate adjacent clips |
| **Background music mismatch** | ~30% of outputs | Keyword-only music selection | No automated detection currently | AI mood matching (gap) |

---

## Why Evaluation Is THE Bottleneck

The conventional assumption is that generation quality is the bottleneck -- "if only the AI could generate better video, the pipeline would produce good output." This is wrong.

### Capability Comparison

```
Generation Capability     [=============================] High
                          (Open-Sora, Kling API, Runway API)

Assembly Capability       [=========================]     High
                          (FFmpeg, MoviePy, Remotion)

Script Generation         [===========================]   High
                          (GPT-4, Claude, DeepSeek)

TTS Quality               [==========================]    High
                          (ElevenLabs, Azure, Edge-TTS)

Evaluation Capability     [====]                          Very Low
                          (No pipeline has any)

Correction Capability     []                              Zero
                          (None implemented anywhere)
```

### Three Bottleneck Levels

**Level 1 -- Cannot evaluate:** Without evaluation, there is no way to know if output is good or bad. Bad output ships alongside good output. User trust erodes.

**Level 2 -- Can evaluate but cannot correct:** If you can score output but cannot act on the score, you can only reject bad output (waste generation cost) rather than improve it.

**Level 3 -- Can evaluate and correct:** The system converges on quality. Bad output is detected, diagnosed, and corrected through prompt refinement and regeneration. This is the target state.

**Current open-source ecosystem is at Level 0** -- cannot even evaluate.

---

## Opportunity Sizing

### Addressable Market

| Segment | Market Size (est.) | Relevant Pain Point |
|---------|-------------------|-------------------|
| Social media content creators | Millions | Need consistent quality at volume |
| Marketing / ad agencies | $50B+ digital ad market | Need brand-safe, on-message video |
| E-learning / training | $300B+ global market | Need consistent, clear explainer videos |
| E-commerce product videos | Growing rapidly | Need low-cost, high-volume product showcases |
| News / media | Emerging | Need fast turnaround, factually grounded |

### Differentiation Potential

| Differentiator | Difficulty | Impact | Time to Market |
|---------------|-----------|--------|---------------|
| Quality gate (3-layer evaluation) | Medium | Very High | 2-3 months |
| AI video API integration | Medium | High | 1-2 months |
| Correction loop | High | Very High | 3-4 months |
| AI BGM integration | Low | Medium | 1 month |
| Multi-shot consistency | Very High | High | 6+ months (depends on model progress) |

The highest-impact, most achievable differentiation is the **quality gate + correction loop**. This is the core of the architecture proposal in [06-architecture-proposal.md](06-architecture-proposal.md).

---

## Cross-References

- For the open-source landscape being analyzed: [01-open-source-landscape.md](01-open-source-landscape.md)
- For evaluation tools that can fill the assessment gap: [02-evaluation-tools.md](02-evaluation-tools.md)
- For correction patterns from research: [03-self-correction-patterns.md](03-self-correction-patterns.md)
- For commercial comparison: [04-commercial-landscape.md](04-commercial-landscape.md)
- For the architecture designed to address these gaps: [06-architecture-proposal.md](06-architecture-proposal.md)


<br><br>

---



<!-- FILE: 06-architecture-proposal.md -->
# Architecture Proposal -- Three-Layer Quality Gate + Evaluation-Correction Loop

> The core architecture design document for a production-quality AI short video generation system. This design synthesizes the findings from the open-source landscape survey ([01](01-open-source-landscape.md)), evaluation tools catalog ([02](02-evaluation-tools.md)), self-correction patterns ([03](03-self-correction-patterns.md)), commercial analysis ([04](04-commercial-landscape.md)), and gap analysis ([05](05-gap-analysis.md)).

---

## System Overview

```
+-------------------------------------------------------------------+
|                         USER INPUT                                |
|  (Topic / Script / Reference images / Style preferences)          |
+------------------------------+------------------------------------+
                               |
                               v
+------------------------------+------------------------------------+
|                      ORCHESTRATOR (LangGraph)                     |
|                                                                   |
|  +-----------+    +-----------+    +------------+    +----------+ |
|  | Script    |--->| Prompt    |--->| Generation |--->| Assembly | |
|  | Generator |    | Engineer  |    | Dispatcher |    | Engine   | |
|  +-----------+    +-----------+    +------------+    +----------+ |
|                                         |                  |      |
|                                    [AI Video API]     [FFmpeg/    |
|                                    Veo 3.1 / Kling   MoviePy]    |
|                                    / Runway / Sora                |
+------------------------------+------------------------------------+
                               |
                               v
+------------------------------+------------------------------------+
|                    QUALITY GATE (3 Layers)                        |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | Layer 1          |  | Layer 2          |  | Layer 3         |  |
|  | Programmatic     |  | ML Model         |  | VLM Review      |  |
|  | Checks           |  | Checks           |  |                 |  |
|  | (<1s, zero cost) |  | (1-10s, low cost)|  | (5-30s, $$)     |  |
|  +--------+---------+  +--------+---------+  +--------+--------+  |
|           |                      |                     |          |
|        PASS/FAIL             PASS/FAIL/             PASS/FAIL/   |
|                              UNCERTAIN              FEEDBACK     |
+------------------------------+------------------------------------+
                               |
                    +----------+-----------+
                    |                      |
                  PASS                   FAIL
                    |                      |
                    v                      v
            +------+------+    +-----------+-----------+
            | Final Output |    | CORRECTION AGENT      |
            | (MP4 + JSON  |    |                       |
            |  sidecar)    |    | Feedback --> Corrected|
            +--------------+    | prompt / parameters   |
                                +-----------+-----------+
                                            |
                                            v
                                    [Retry: back to Generation]
                                    (up to MAX_REVISIONS)
```

---

## Layer 1: Programmatic Checks

**Latency:** < 1 second | **Cost:** Zero | **Purpose:** Catch structural failures instantly

These checks validate that the generated video is a well-formed media file with correct technical properties. They require no ML models and run on CPU.

### Check Catalog

| Check | Tool | What It Validates | Pass Criteria | Failure Action |
|-------|------|-------------------|---------------|----------------|
| File integrity | FFmpeg / ffprobe | File is valid, parseable, not corrupted | `ffprobe` exits 0, reports valid streams | FAIL + regenerate |
| Resolution | ffprobe | Video matches target resolution | Width x Height matches spec (e.g., 1080x1920) | FAIL + re-encode or regenerate |
| Duration | ffprobe | Video length matches expected duration | Within +/- 10% of target duration | FAIL + trim or regenerate |
| A/V sync | ffprobe PTS analysis | Audio and video timestamps are aligned | PTS difference < 100ms | FAIL + re-mux |
| Audio loudness | FFmpeg loudnorm filter | Audio is at appropriate volume | -23 LUFS +/- 2dB (EBU R128) | WARN + normalize |
| Subtitle validation | pysrt | Subtitles parse correctly, no overlaps | All entries valid, no timing overlaps | FAIL + regenerate subtitles |
| Frame consistency | imagehash (pHash) | No extreme frame-to-frame changes | Hamming distance < 15 for adjacent frames | WARN + flag anomalous frames |
| Audio stream present | ffprobe | Video has audio track | Audio stream count >= 1 | FAIL + mux audio |
| Codec validation | ffprobe | Output uses expected codecs | H.264/H.265 video, AAC audio | FAIL + re-encode |

### Implementation

```python
import subprocess
import json
from dataclasses import dataclass

@dataclass
class L1Result:
    passed: bool
    checks: dict  # check_name -> {passed: bool, value: any, threshold: any}
    failures: list[str]

def layer1_check(video_path: str, config: dict) -> L1Result:
    """Run all Layer 1 programmatic checks."""
    checks = {}
    failures = []

    # File integrity
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", video_path],
            capture_output=True, text=True, timeout=10
        )
        info = json.loads(probe.stdout)
        checks["file_integrity"] = {"passed": True}
    except Exception as e:
        checks["file_integrity"] = {"passed": False, "error": str(e)}
        failures.append("file_integrity")
        return L1Result(passed=False, checks=checks, failures=failures)

    # Resolution check
    video_stream = next(
        (s for s in info["streams"] if s["codec_type"] == "video"), None
    )
    if video_stream:
        w, h = int(video_stream["width"]), int(video_stream["height"])
        target_w, target_h = config["target_resolution"]
        res_ok = (w == target_w and h == target_h)
        checks["resolution"] = {
            "passed": res_ok, "value": f"{w}x{h}",
            "threshold": f"{target_w}x{target_h}"
        }
        if not res_ok:
            failures.append("resolution")

    # Duration check
    duration = float(info["format"]["duration"])
    target_dur = config["target_duration"]
    tolerance = config.get("duration_tolerance", 0.1)
    dur_ok = abs(duration - target_dur) / target_dur <= tolerance
    checks["duration"] = {
        "passed": dur_ok, "value": duration,
        "threshold": f"{target_dur} +/- {tolerance*100}%"
    }
    if not dur_ok:
        failures.append("duration")

    # Audio stream check
    audio_stream = next(
        (s for s in info["streams"] if s["codec_type"] == "audio"), None
    )
    checks["audio_present"] = {"passed": audio_stream is not None}
    if not audio_stream:
        failures.append("audio_present")

    # A/V sync check (simplified: compare start times)
    if video_stream and audio_stream:
        v_start = float(video_stream.get("start_time", 0))
        a_start = float(audio_stream.get("start_time", 0))
        sync_diff_ms = abs(v_start - a_start) * 1000
        sync_ok = sync_diff_ms < config.get("max_av_sync_ms", 100)
        checks["av_sync"] = {
            "passed": sync_ok, "value": f"{sync_diff_ms:.1f}ms",
            "threshold": f"<{config.get('max_av_sync_ms', 100)}ms"
        }
        if not sync_ok:
            failures.append("av_sync")

    # Audio loudness check
    loudness_result = subprocess.run(
        ["ffmpeg", "-i", video_path, "-af", "loudnorm=print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=30
    )
    # Parse loudness from stderr (FFmpeg outputs to stderr)
    # ... (parsing logic for integrated loudness)

    return L1Result(
        passed=len(failures) == 0,
        checks=checks,
        failures=failures
    )
```

---

## Layer 2: ML Model Checks

**Latency:** 1-10 seconds | **Cost:** Low (local GPU inference) | **Purpose:** Assess perceptual quality and semantic alignment

Layer 2 uses pretrained ML models to evaluate quality dimensions that cannot be checked programmatically. All models run locally (no API cost).

### Check Catalog

| Check | Tool | What It Measures | Output | Threshold |
|-------|------|-----------------|--------|-----------|
| Aesthetic + technical quality | DOVER | Overall visual quality, separate aesthetic and technical scores | 3 floats [0-1] | Overall >= 0.65 |
| Text-video alignment | OpenCLIP | How well visual content matches the generation prompt | Cosine similarity [0-1] | >= 0.25 |
| Subject consistency | VBench | Subject visual stability across frames | Float [0-1] | >= 0.80 |
| Temporal flickering | VBench | Frame-to-frame brightness/color stability | Float [0-1] | >= 0.85 |
| Motion smoothness | VBench | Natural motion quality | Float [0-1] | >= 0.80 |
| Scene transitions | PySceneDetect | Unexpected scene breaks | Count vs expected | Detected <= expected + 1 |
| Color consistency | OpenCV histogram | Color distribution stability across shots | Bhattacharyya distance | < 0.4 between adjacent shots |
| Subtitle timing | stable-ts | Subtitle-audio synchronization accuracy | Timing offset per word | Mean offset < 200ms |

### Score Aggregation

```python
def compute_l2_score(checks: dict, weights: dict) -> float:
    """
    Compute weighted Layer 2 quality score.

    Default weights (configurable via quality_thresholds.yaml):
      dover_overall: 0.25
      clip_alignment: 0.25
      subject_consistency: 0.15
      temporal_flickering: 0.15
      motion_smoothness: 0.10
      color_consistency: 0.05
      subtitle_sync: 0.05
    """
    score = 0.0
    for check_name, weight in weights.items():
        if check_name in checks:
            score += checks[check_name] * weight
    return score
```

### Decision Logic

| L2 Score | Action |
|----------|--------|
| >= 0.70 | **PASS** -- output directly |
| 0.50 - 0.69 | **UNCERTAIN** -- escalate to Layer 3 (VLM review) |
| < 0.50 | **FAIL** -- retry with same prompt + new seed (cheap retry) |

### Implementation

```python
@dataclass
class L2Result:
    score: float
    dimension_scores: dict  # dimension -> float
    decision: str  # "pass", "uncertain", "fail"
    details: dict

def layer2_check(
    video_path: str, prompt: str, config: dict
) -> L2Result:
    """Run Layer 2 ML model checks."""
    scores = {}

    # DOVER quality assessment
    dover_scores = dover_model.evaluate(video_path)
    scores["dover_overall"] = dover_scores["overall"]
    scores["dover_aesthetic"] = dover_scores["aesthetic"]
    scores["dover_technical"] = dover_scores["technical"]

    # OpenCLIP text-video alignment
    frames = extract_frames(video_path, n_frames=16)
    clip_score = compute_clip_similarity(frames, prompt)
    scores["clip_alignment"] = clip_score

    # VBench subset
    vbench_results = vbench_evaluator.evaluate(
        video_path, prompt,
        dimensions=["subject_consistency", "temporal_flickering",
                     "motion_smoothness"]
    )
    scores.update(vbench_results)

    # Scene detection
    scenes = detect_scenes(video_path)
    expected_scenes = config.get("expected_scenes", len(scenes))
    scores["scene_consistency"] = 1.0 if len(scenes) <= expected_scenes + 1 else 0.5

    # Aggregate
    weights = config.get("l2_weights", DEFAULT_L2_WEIGHTS)
    overall = compute_l2_score(scores, weights)

    # Decision
    if overall >= config.get("l2_pass_threshold", 0.70):
        decision = "pass"
    elif overall >= config.get("l2_uncertain_threshold", 0.50):
        decision = "uncertain"
    else:
        decision = "fail"

    return L2Result(
        score=overall,
        dimension_scores=scores,
        decision=decision,
        details={"weights": weights}
    )
```

---

## Layer 3: VLM Review

**Latency:** 5-30 seconds | **Cost:** Higher (VLM API call) | **Purpose:** Semantic quality assessment and structured feedback generation

Layer 3 is invoked only when Layer 2 returns "uncertain" (score 0.50-0.69). It uses a Vision-Language Model to perform structured qualitative review.

### Frame Sampling Strategy

```python
def sample_frames_for_vlm(video_path: str, n_frames: int = 16) -> list:
    """
    Uniform temporal sampling of frames for VLM input.

    16 frames balances coverage vs token cost:
    - Too few (<8): miss temporal issues
    - Too many (>24): diminishing returns, higher token cost
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total_frames - 1, n_frames, dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames
```

### VLM Choice

| VLM | Latency | Cost per Review | Visual Quality | Structured Output | Recommended |
|-----|---------|----------------|----------------|-------------------|-------------|
| Gemini 2.5 Flash | 3-8s | ~$0.01-0.03 | Excellent (native video) | Good | Primary |
| GPT-4o | 5-15s | ~$0.03-0.10 | Very Good (frame-based) | Excellent | Fallback |
| Claude 3.5 Sonnet | 5-15s | ~$0.03-0.10 | Good (frame-based) | Excellent | Alternative |

**Primary recommendation: Gemini 2.5 Flash** for cost efficiency and native video understanding. Use GPT-4o or Claude as fallback.

### Evaluation Dimensions

| Dimension | What It Assesses | Weight |
|-----------|-----------------|--------|
| Visual Fidelity | Artifacts, distortions, rendering quality | 0.30 |
| Content-Script Alignment | Does the video depict what the script describes? | 0.30 |
| Narrative Coherence | Does the sequence of shots tell a coherent story? | 0.25 |
| Overall Feel | Professional polish, pacing, emotional impact | 0.15 |

### Scoring Protocol

Based on the LLM-as-Judge calibration best practices from [03-self-correction-patterns.md](03-self-correction-patterns.md):

**1. Use discrete labels, not numerical scales:**

```
Labels: EXCELLENT / GOOD / FAIR / POOR
```

Mapping to numeric for aggregation:
- EXCELLENT = 1.0
- GOOD = 0.8
- FAIR = 0.5
- POOR = 0.2

**2. Chain-of-thought reasoning BEFORE scoring:**

The VLM must describe its observations before assigning labels. This prevents snap judgments and improves consistency.

**3. Anchor samples (2-3 examples):**

Include reference examples of GOOD and POOR quality in the prompt to calibrate the VLM's expectations.

**4. Structured JSON output:**

```json
{
  "observations": "The video shows a sequence of 5 shots depicting...",
  "dimension_assessments": {
    "visual_fidelity": {
      "reasoning": "Frame quality is consistent. Minor aliasing on text overlay in shot 3. No major artifacts.",
      "label": "GOOD",
      "issues": ["minor text aliasing in shot 3"]
    },
    "content_alignment": {
      "reasoning": "Script mentions 'a busy coffee shop' but shots 2-3 show an empty room.",
      "label": "FAIR",
      "issues": ["shots 2-3 do not match 'busy coffee shop' description"]
    },
    "narrative_coherence": {
      "reasoning": "Shots flow logically. Transition from intro to body to conclusion is clear.",
      "label": "GOOD",
      "issues": []
    },
    "overall_feel": {
      "reasoning": "Professional-looking but the content mismatch in shots 2-3 is distracting.",
      "label": "FAIR",
      "issues": ["content mismatch reduces overall quality"]
    }
  },
  "overall_label": "FAIR",
  "corrective_feedback": {
    "primary_issue": "Shots 2-3 show an empty room instead of a busy coffee shop",
    "suggested_prompt_changes": "Replace shots 2-3 with: 'Interior of a busy coffee shop, customers at tables, barista making drinks, warm lighting, afternoon'",
    "parameter_adjustments": {
      "shots_to_regenerate": [2, 3],
      "style_guidance": "Increase detail specificity for indoor scenes"
    }
  }
}
```

### RePrompt Mechanism

When the VLM returns FAIR or POOR on any dimension:

1. Extract the `corrective_feedback` from the VLM response
2. Use an LLM to rewrite the generation prompt incorporating the feedback
3. Regenerate only the failed shots (not the entire video)
4. Re-evaluate starting from Layer 1

```python
def reprompt(original_prompt: str, feedback: dict) -> str:
    """Use LLM to generate corrected prompt based on VLM feedback."""
    system = """You are a video generation prompt engineer. Given the
    original prompt and quality feedback, rewrite the prompt to address
    the identified issues. Be specific and concrete."""

    user = f"""Original prompt: {original_prompt}

    Issue: {feedback['primary_issue']}
    Suggested changes: {feedback['suggested_prompt_changes']}

    Rewrite the prompt to fix this issue while preserving the original intent."""

    corrected = llm.generate(system=system, user=user)
    return corrected
```

---

## Correction Loop

### LangGraph State Graph

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

class VideoState(TypedDict):
    # Input
    topic: str
    script: str
    target_duration: float
    style_config: dict

    # Generation
    shot_prompts: list[str]
    video_clips: list[str]  # file paths
    assembled_video: str     # file path

    # Evaluation
    l1_result: dict | None
    l2_result: dict | None
    l3_result: dict | None
    quality_scores: dict

    # Correction
    feedback: str
    corrective_actions: list[dict]
    revision_count: int
    max_revisions: int
    retry_strategy: str  # "cheap", "correction", "degradation"

    # Output
    final_video: str
    quality_report: dict
    warnings: list[str]


def generate_script(state: VideoState) -> VideoState:
    """Generate or refine the video script from topic."""
    # ... LLM script generation
    return state


def generate_shots(state: VideoState) -> VideoState:
    """Generate individual video clips from shot prompts."""
    # ... AI video API calls (Runway/Kling/Sora)
    return state


def assemble_video(state: VideoState) -> VideoState:
    """Assemble clips + audio + subtitles into final video."""
    # ... FFmpeg/MoviePy assembly
    return state


def quality_gate(state: VideoState) -> VideoState:
    """Run three-layer quality gate."""
    # Layer 1
    l1 = layer1_check(state["assembled_video"], state["style_config"])
    state["l1_result"] = l1.__dict__
    if not l1.passed:
        state["retry_strategy"] = "cheap"
        return state

    # Layer 2
    l2 = layer2_check(
        state["assembled_video"],
        state["script"],
        state["style_config"]
    )
    state["l2_result"] = l2.__dict__
    if l2.decision == "pass":
        state["quality_scores"] = l2.dimension_scores
        return state
    elif l2.decision == "fail":
        state["retry_strategy"] = "cheap"
        return state

    # Layer 3 (only if L2 uncertain)
    l3 = vlm_review(state["assembled_video"], state["script"])
    state["l3_result"] = l3
    state["quality_scores"] = {**l2.dimension_scores, "vlm": l3}

    if l3["overall_label"] in ("EXCELLENT", "GOOD"):
        state["retry_strategy"] = "none"
    elif l3["overall_label"] == "FAIR":
        state["retry_strategy"] = "correction"
        state["feedback"] = json.dumps(l3["corrective_feedback"])
    else:  # POOR
        state["retry_strategy"] = "correction"
        state["feedback"] = json.dumps(l3["corrective_feedback"])

    return state


def should_retry(state: VideoState) -> str:
    """Determine next step based on quality gate result."""
    strategy = state.get("retry_strategy", "none")

    if strategy == "none":
        return "output"

    if state["revision_count"] >= state["max_revisions"]:
        return "degrade"

    if strategy == "cheap":
        return "retry_cheap"

    if strategy == "correction":
        return "retry_correct"

    return "output"


def cheap_retry(state: VideoState) -> VideoState:
    """Retry with same prompts but new random seed."""
    state["revision_count"] += 1
    # Regenerate with new seed
    return state


def correction_retry(state: VideoState) -> VideoState:
    """Use VLM feedback to correct prompts, then regenerate."""
    state["revision_count"] += 1
    feedback = json.loads(state["feedback"])

    # Identify which shots to regenerate
    shots_to_redo = feedback.get("parameter_adjustments", {}).get(
        "shots_to_regenerate", list(range(len(state["shot_prompts"])))
    )

    # Rewrite prompts for failed shots
    for shot_idx in shots_to_redo:
        state["shot_prompts"][shot_idx] = reprompt(
            state["shot_prompts"][shot_idx], feedback
        )

    return state


def degrade_output(state: VideoState) -> VideoState:
    """Output best version with quality warning."""
    state["warnings"].append(
        f"Quality target not met after {state['revision_count']} revisions. "
        f"Outputting best available version."
    )
    return state


def output_video(state: VideoState) -> VideoState:
    """Finalize output with quality report sidecar."""
    state["final_video"] = state["assembled_video"]
    state["quality_report"] = {
        "l1": state.get("l1_result"),
        "l2": state.get("l2_result"),
        "l3": state.get("l3_result"),
        "revisions": state["revision_count"],
        "warnings": state["warnings"]
    }
    return state


# Build the graph
graph = StateGraph(VideoState)

graph.add_node("generate_script", generate_script)
graph.add_node("generate_shots", generate_shots)
graph.add_node("assemble", assemble_video)
graph.add_node("quality_gate", quality_gate)
graph.add_node("cheap_retry", cheap_retry)
graph.add_node("correction_retry", correction_retry)
graph.add_node("degrade", degrade_output)
graph.add_node("output", output_video)

graph.set_entry_point("generate_script")
graph.add_edge("generate_script", "generate_shots")
graph.add_edge("generate_shots", "assemble")
graph.add_edge("assemble", "quality_gate")

graph.add_conditional_edges("quality_gate", should_retry, {
    "output": "output",
    "retry_cheap": "cheap_retry",
    "retry_correct": "correction_retry",
    "degrade": "degrade",
})

graph.add_edge("cheap_retry", "generate_shots")
graph.add_edge("correction_retry", "generate_shots")
graph.add_edge("degrade", "output")
graph.add_edge("output", END)

pipeline = graph.compile()
```

### Retry Strategies

| Strategy | Trigger | What Changes | Cost | Expected Improvement |
|----------|---------|-------------|------|---------------------|
| **Cheap retry** | L1 fail or L2 score < 0.50 | Same prompt, new random seed | Low (one regeneration) | 30-50% chance of fixing stochastic failures |
| **Correction retry** | L2 score 0.50-0.69 or L3 FAIR | VLM generates corrected prompt + parameters | Medium (VLM call + regeneration) | 50-70% chance of improvement |
| **Degradation** | Budget exceeded (revision_count >= max_revisions) | Output best version + attach quality warning | Zero (no new generation) | N/A (graceful fallback) |
| **Human escalation** | 3x consecutive POOR from L3 | Stop pipeline, notify human with diagnostic report | Zero compute, human time | Depends on human intervention |

### Retry Budget Management

```python
RETRY_BUDGETS = {
    "stock_footage": {
        "max_revisions": 5,
        "l1_max_retries": 3,    # cheap, just re-select footage
        "l2_max_retries": 2,    # ML re-evaluation
        "l3_max_reviews": 1,    # VLM review is expensive relative to stock
    },
    "ai_video_api": {
        "max_revisions": 3,
        "l1_max_retries": 2,
        "l2_max_retries": 1,
        "l3_max_reviews": 1,
    },
    "local_model": {
        "max_revisions": 2,
        "l1_max_retries": 1,
        "l2_max_retries": 1,
        "l3_max_reviews": 1,
    }
}
```

---

## Configuration

### quality_thresholds.yaml

```yaml
# Quality Gate Configuration
# --------------------------

layer1:
  checks:
    file_integrity: true
    resolution: true
    duration: true
    av_sync: true
    audio_loudness: true
    subtitle_validation: true
    frame_consistency: true
    audio_present: true
    codec_validation: true

  thresholds:
    max_av_sync_ms: 100
    target_loudness_lufs: -23.0
    loudness_tolerance_db: 2.0
    duration_tolerance_pct: 0.10
    frame_hash_threshold: 15

layer2:
  weights:
    dover_overall: 0.25
    clip_alignment: 0.25
    subject_consistency: 0.15
    temporal_flickering: 0.15
    motion_smoothness: 0.10
    color_consistency: 0.05
    subtitle_sync: 0.05

  thresholds:
    pass: 0.70         # >= this: PASS
    uncertain: 0.50    # >= this but < pass: escalate to L3
    # < uncertain: FAIL + cheap retry

layer3:
  vlm:
    provider: gemini       # gemini | openai | anthropic
    model: gemini-2.5-flash
    fallback_provider: openai
    fallback_model: gpt-4o

  frame_sampling:
    n_frames: 16
    method: uniform        # uniform | keyframe | adaptive

  scoring:
    labels: [EXCELLENT, GOOD, FAIR, POOR]
    label_values:
      EXCELLENT: 1.0
      GOOD: 0.8
      FAIR: 0.5
      POOR: 0.2
    dimensions:
      visual_fidelity: 0.30
      content_alignment: 0.30
      narrative_coherence: 0.25
      overall_feel: 0.15

  anchor_samples:
    good: "examples/good_sample.mp4"
    poor: "examples/poor_sample.mp4"

retry:
  max_revisions: 3
  strategies:
    cheap:
      trigger: "l1_fail OR l2_score < 0.50"
      action: "regenerate with new seed"
    correction:
      trigger: "l2_score 0.50-0.69 OR l3_label FAIR/POOR"
      action: "vlm feedback -> reprompt -> regenerate"
    degradation:
      trigger: "revision_count >= max_revisions"
      action: "output best + warning"
    escalation:
      trigger: "3x consecutive POOR"
      action: "stop + notify human"
```

### pipeline.yaml

```yaml
# Pipeline Configuration
# ----------------------

generation:
  providers:
    primary:
      name: kling
      api_key_env: KLING_API_KEY
      model: kling-v3
      default_resolution: "1080x1920"
      default_duration: 5
      timeout_seconds: 120
    fallback:
      name: runway
      api_key_env: RUNWAY_API_KEY
      model: gen-4.5
      default_resolution: "1080x1920"
      default_duration: 5
      timeout_seconds: 180

  concurrency:
    max_parallel_generations: 4
    rate_limit_per_minute: 10

script:
  llm:
    provider: openai     # openai | anthropic | deepseek
    model: gpt-4o
  language: en
  max_shots: 12
  target_duration_seconds: 60

tts:
  provider: edge-tts     # edge-tts | elevenlabs | azure | openai
  voice: en-US-ChristopherNeural
  speed: 1.0
  fallback_provider: openai

subtitles:
  method: stable-ts      # stable-ts | whisperx | whisper
  model_size: large-v3
  word_level: true
  style:
    font: "Montserrat Bold"
    font_size: 48
    color: "#FFFFFF"
    outline_color: "#000000"
    outline_width: 2
    position: bottom     # bottom | center

bgm:
  source: royalty-free   # royalty-free | suno | musicgen
  library_path: "assets/bgm/"
  volume_db: -18         # relative to narration

output:
  format: mp4
  video_codec: h264
  audio_codec: aac
  video_bitrate: "8M"
  audio_bitrate: "192k"
  fps: 30
  sidecar: true          # output quality report JSON alongside video
```

---

## Observability: LangSmith Integration

The correction loop built on LangGraph can leverage **LangSmith** for production observability, debugging, and continuous improvement.

### Why LangSmith

LangSmith provides **LangGraph-native tracing** with step-level (node/edge) scoring. This is critical for:

1. **Debugging retry loops:** See exactly which quality gate layer failed, what score triggered the retry, and how the corrected prompt differs from the original
2. **Performance monitoring:** Track L1/L2/L3 latencies, pass rates, and retry frequencies over time
3. **Evaluation annotation:** Human annotators can score pipeline outputs through LangSmith's annotation queues, building a ground-truth dataset for calibrating thresholds
4. **Regression detection:** Automated evaluation runs can flag when VLM quality judgments drift (e.g., Gemini model update changes scoring behavior)

### Integration Architecture

```
LangGraph Pipeline
    │
    ├── generate_shots ──trace──▶ LangSmith
    │       └── [provider, prompt, latency, cost]
    │
    ├── quality_gate ──trace──▶ LangSmith
    │       ├── L1 results [check_name → pass/fail]
    │       ├── L2 results [dimension_scores, aggregate]
    │       └── L3 results [VLM response, label, critique]
    │
    ├── correction_retry ──trace──▶ LangSmith
    │       └── [original_prompt, corrected_prompt, diff]
    │
    └── output ──trace──▶ LangSmith
            └── [final_scores, retry_count, warnings]
```

### Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| L1 pass rate | quality_gate node | < 90% (infrastructure problem) |
| L2 mean score | quality_gate node | < 0.60 (generation quality drop) |
| L3 invocation rate | quality_gate node | > 40% (L2 threshold may need tuning) |
| Retry rate | conditional edge | > 50% (generator or prompt issue) |
| Mean retries per video | output node | > 2.0 (cost concern) |
| VLM judge consistency | L3 annotations | Cohen's kappa < 0.6 vs human |

### Setup

```python
# Add to orchestrator.py
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
os.environ["LANGCHAIN_PROJECT"] = "videoqa-gate"

# LangGraph pipeline automatically sends traces to LangSmith
# when LANGCHAIN_TRACING_V2 is set
pipeline = graph.compile()
result = pipeline.invoke(initial_state)
```

### Alternative: Self-Hosted Observability

For users who prefer not to use LangSmith, the pipeline outputs a **JSON sidecar** alongside each video containing the full quality report. This can be ingested into any observability stack (Grafana, ELK, etc.).

---

## Validation Plan

### Unit Tests

| Test | What It Validates | Input | Expected Output |
|------|-------------------|-------|----------------|
| `test_l1_valid_video` | L1 passes for well-formed video | Known good MP4 | All checks pass |
| `test_l1_corrupted_file` | L1 catches corrupted files | Truncated MP4 | file_integrity FAIL |
| `test_l1_wrong_resolution` | L1 catches resolution mismatch | 720p video when 1080p expected | resolution FAIL |
| `test_l1_no_audio` | L1 catches missing audio | Video-only MP4 | audio_present FAIL |
| `test_l2_high_quality` | L2 passes good video | Professional stock video | Score >= 0.70 |
| `test_l2_low_quality` | L2 fails bad video | Heavily compressed, artifacted video | Score < 0.50 |
| `test_l2_weight_config` | L2 weights are configurable | Custom weights YAML | Scores shift accordingly |
| `test_l3_structured_output` | L3 VLM returns valid JSON | Video + prompt | Valid JSON with all required fields |
| `test_reprompt_incorporates_feedback` | Corrected prompt addresses issues | Original prompt + feedback | New prompt mentions fix |
| `test_retry_cap` | Pipeline stops after max_revisions | Always-failing video | Exits with degradation after N retries |

### Integration Tests with Known Samples

```
tests/
  fixtures/
    good_sample.mp4         -- professionally produced, all checks should pass
    bad_resolution.mp4      -- wrong resolution
    bad_sync.mp4            -- A/V sync drift
    low_quality.mp4         -- heavy compression artifacts
    no_audio.mp4            -- video only
    flickering.mp4          -- temporal flickering artifacts
    mismatched_content.mp4  -- video does not match prompt
```

### End-to-End Test

1. Input: a topic string ("explain how solar panels work in 60 seconds")
2. Expected: pipeline generates script, creates shots, assembles video, runs quality gate
3. Assertions:
   - Output MP4 exists and is valid
   - Quality report JSON sidecar exists
   - All L1 checks pass
   - L2 score >= 0.50
   - If retries occurred, revision_count is recorded
   - Total pipeline time < 10 minutes (for stock footage) or < 30 minutes (for AI video API)

### Benchmark Comparison

Compare output quality (using VBench full suite) against:
- MoneyPrinterTurbo output (same topic)
- Raw AI video generation (no quality gate)
- Human-curated reference video

Target: quality-gated output should score >= 15% higher than MoneyPrinterTurbo on VBench average across dimensions.

---

## Implementation Roadmap

| Phase | Scope | Duration | Dependencies |
|-------|-------|----------|-------------|
| **Phase 1** | Layer 1 checks + basic pipeline skeleton | 2 weeks | FFmpeg, ffprobe, pysrt, imagehash |
| **Phase 2** | Layer 2 ML checks (DOVER + OpenCLIP) | 2 weeks | DOVER model, OpenCLIP, GPU |
| **Phase 3** | Layer 3 VLM review + RePrompt | 2 weeks | VLM API access (Gemini/OpenAI) |
| **Phase 4** | Correction loop + LangGraph orchestration | 2 weeks | LangGraph, Phase 1-3 |
| **Phase 5** | AI video API integration (Kling/Runway) | 2 weeks | API keys, budget |
| **Phase 6** | VBench subset integration for L2 | 1 week | VBench, GPU |
| **Phase 7** | Configuration externalization + YAML | 1 week | -- |
| **Phase 8** | Testing, benchmarking, documentation | 2 weeks | Known good/bad samples |

Total estimated timeline: **10-13 weeks** for a production-ready MVP.

---

## Video Generation Provider Matrix (Updated 2026-03)

Production-ready AI video generation providers integrated or available:

| Provider | Model | Price/10s | Resolution | Duration | Audio | Status |
|----------|-------|-----------|-----------|----------|-------|--------|
| **Google Veo 3.1** | `veo-3.1-generate-preview` | $1.50 (Fast) / $4.00 (Std) | 4K | 8s | Native | **Default** |
| Google Veo 2 | `veo-2.0-generate` | $3.50 | 4K | 8s | No | Integrated |
| Runway Gen-4 | Gen-4 Turbo | $0.50 | 4K | 16s | No | Integrated |
| Kling 3.0 | Kling API | $0.50-1.50 | 1080p | 5-10s | Yes | Integrated |
| OpenAI Sora | Sora-2 | $1.00 | 1080p | 60s | No | Planned |
| Hailuo (MiniMax) | Hailuo 02 | $0.14-0.28 | 1080p | 6-10s | No | Planned |
| Pexels Stock | — | Free | Varies | Varies | No | Integrated |

### Veo 3.1 Integration Architecture

```python
# google-genai SDK async polling pattern
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Cinematic shot of...",
    config=types.GenerateVideosConfig(
        aspect_ratio="9:16",    # Vertical short video
        number_of_videos=1,
    ),
)

# Poll → Download → Save
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("output.mp4")
```

**Key design decisions:**
- Veo 3.1 as default: best quality-to-price ratio among top-tier models
- Native audio generation eliminates separate BGM/SFX pipeline for Veo clips
- 9:16 aspect ratio native support matches short video format
- Fallback chain: Veo → Kling → Pexels stock footage

---

## Cross-References

- Evaluation tools used in the quality gate: [02-evaluation-tools.md](02-evaluation-tools.md)
- Self-correction patterns that inform the correction loop: [03-self-correction-patterns.md](03-self-correction-patterns.md)
- Gap analysis this architecture addresses: [05-gap-analysis.md](05-gap-analysis.md)
- Open-source landscape this builds on: [01-open-source-landscape.md](01-open-source-landscape.md)
- Commercial benchmarks to compare against: [04-commercial-landscape.md](04-commercial-landscape.md)


<br><br>

---



<!-- FILE: 07-workflow-analysis.md -->
# 07 — AI 短视频自动生成：工具链选型与工作流分析

> 最后更新：2026-03-14 | 基于对 30+ 工具、6 大商业平台、主流开源项目的系统调研

---

## 1. 推荐方案：现在用什么生成视频

### 1.1 一句话结论

> **主力方案：Kling 3.0**（4K/60fps + 原生音频 + 多镜头叙事 + 角色一致性），通过第三方 API 调用，~$0.12-0.15/秒。备选 Seedance 2.0（成本更低但全球 API 受限）。零成本原型用 Pexels + CLIP 语义匹配。

### 1.2 三档工具链

| 档位 | 生成方案 | 管道模式 | 单条成本 | 首次可用率 | 适用场景 |
|------|---------|---------|---------|-----------|---------|
| **入门档** | Pexels 素材 + CLIP 语义排序 + edge-tts + FFmpeg | 传统 6 步 | **$0** | 40-50% | 零成本验证、量产测试 |
| **主力档** | Kling 3.0 API（原生音频+多镜头） | 坍缩 4 步 | **$0.60-1.00** | 60-65% | 日常生产 |
| **精品档** | Kling 3.0 Pro（4K/60fps）或 Veo 3.1 | 坍缩 4 步 | **$3-9** | 60-73% | 旗舰内容 |

### 1.3 管道结构变化（2026.02 之后）

2026 年 2 月之后，顶级模型（Kling 3.0 / Seedance 2.0 / Veo 3.1）原生集成音频生成，管道发生结构性坍缩：

```
传统 6 步（2025）：    脚本 → TTS → 视频素材 → 字幕 → 配乐 → 合成
坍缩 4 步（2026.02+）：脚本 → AI 视频+音频一体生成 → 字幕 → 合成
```

TTS 和 BGM 被模型本身吸收。**这改变了质量评估的粒度** — 从"画面质量"变成"音画整体质量"。

### 1.4 为什么推荐 Kling 3.0 而非其他

| 对比维度 | Kling 3.0 | Seedance 2.0 | Veo 3.1 | Runway Gen-4.5 |
|---------|-----------|-------------|---------|----------------|
| 分辨率 | **4K/60fps** | 2K | 4K | 4K |
| 原生音频 | ✅ | ✅ | ✅ | ❌ |
| 多镜头叙事 | ✅ 15s 多镜头 | ✅ 单 prompt | 有限 | 关键帧 |
| 角色一致性 | ✅ 元素绑定 | ✅ 12 参考文件 | ❌ | ✅ |
| API 可用性 | ✅ 多渠道可用 | ⚠️ 全球 API 推迟 | ✅ 但配额严格 | ✅ |
| API 价格 | $0.12-0.15/s | $0.10-0.14/s（火山引擎） | $0.15/s (Fast) | $0.05/s (Turbo) |
| 免费层 | ✅ 66 daily credits | ✅ 225 daily tokens | ❌ 无免费视频配额 | ✅ 125 credits |
| 风险 | 低 | **高**（版权争议） | 中（配额限制） | 低 |

**Seedance 2.0 全球 API 因版权争议无限期推迟。** 2026.02 生成的含好莱坞演员/受版权保护角色的病毒视频引发迪士尼停止函、派拉蒙指控、MPA 谴责。目前主要通过中国国内应用（即梦/豆包）和少数第三方平台访问。

**Veo 3.1 无免费视频生成配额，** preview 模型限 10 RPM，配额耗尽返回 429。实际首次可用率仅 15-20%，需 4-6 次尝试，真实成本 = 标价 × 3-5。

### 1.5 各档位详细管道

**入门档：Pexels + CLIP 语义匹配**

```
LLM 脚本 → edge-tts → Pexels 搜索(CLIP 余弦排序) → Whisper 字幕 → BGM → FFmpeg
                              ↑
               关键词搜索 → CLIP 语义匹配（解决 #1 质量问题）
```

核心升级点：将 MoneyPrinterTurbo 的关键词搜索替换为 CLIP 语义匹配。成本 $0，解决最常见的"素材-脚本语义失配"问题。

**主力档：Kling 3.0 原生音频**

```
LLM 脚本(含镜头描述) → Kling 3.0(多镜头视频+音频) → Whisper 字幕 → FFmpeg 合成
```

- 第三方 API（ModelsLab/PiAPI）~$0.12-0.15/s，5s 片段 ≈ $0.60-0.75
- 原生音频 + 唇形同步，省去 TTS + BGM
- 多镜头模式：单 prompt 生成最长 15s 连贯多镜头

**精品档：Kling 3.0 Pro 4K/60fps**

```
LLM 结构化脚本 → Kling 3.0 Pro(4K/60fps 多镜头+音频) → Whisper 字幕 → FFmpeg
```

- 原生 4K/60fps，.mov 导出
- Canvas Agent 对话式迭代编辑
- 成本高但质量顶级

---

## 2. 整体局势（2026 年 3 月）

### 2.1 2026.02 大爆发：行业转折点

2026 年 2 月第一周，三大模型同时发布，行业格局剧变：

```
2026.01.05  LTX-2 开源发布（4K/50fps+音频，Apache 2.0）
2026.01.07  Sora 限制免费使用
2026.01.10  Sora 免费层完全停止
2026.02.05  ★ Kling 3.0 发布 — 首个原生 4K/60fps AI 视频模型
2026.02.07  ★ Seedance 2.0 发布 — 原生音频 + 12 文件多模态输入
2026.02.10  ★ Runway Gen-4.5 API 上线
2026.02.12  Seedance 2.0 版权争议爆发
2026.03.04  Seedance 2.0 API 通过火山引擎上线（仅中国）
2026.03.xx  NVIDIA GDC 发布 ComfyUI App View + LTX-2.3 优化
```

### 2.2 行业趋势

```
2025 年常态                        2026.02 之后新常态
─────────────                     ─────────────
单片段生成                         → 多镜头叙事生成
视频/音频分离管道                    → 原生音视频一体生成
1080p 为主流                       → 4K/60fps 成为标杆
文本/图像输入                       → 多模态输入（12+ 参考文件）
手动改 prompt 重试                  → 故事板 + 对话式迭代编辑
生成模型竞争                        → 全创作管道竞争（编辑+导出+发布）
```

### 2.3 市场格局

**商业平台第一梯队（2026.03）：**
- **Kling 3.0**（快手）— 4K/60fps，多镜头，免费层
- **Seedance 2.0**（字节跳动）— 多模态输入最强，但全球受限
- **Veo 3.1**（Google）— 写实感最强，但配额严格且贵
- **Runway Gen-4.5** — 视觉保真最高，专业创作者首选
- **Sora 2**（OpenAI）— 最长视频（25s），但已无免费层

**中国市场双寡头：** 即梦（字节）vs 可灵（快手），海螺（MiniMax）为第三极。

**开源突破：** LTX-2（4K+音频，12GB 可跑）和 Wan 2.2（VBench #1，10GB 可跑）让消费级 GPU 跑 AI 视频成为现实。

### 2.4 核心结论

1. **原生音频是新标配** — 所有顶级模型都原生生成音频，后期配音正在变成可选项
2. **没有任何工具有自动质量门控** — 所有平台、所有开源工具，质量控制完全靠人工
3. **"生成 10 个挑 1 个"是行业通用做法** — 批量生成 + 人工筛选是唯一的"质量策略"
4. **87% 的失败可通过更好的 Prompt 解决** — 但 Prompt 优化目前完全手动
5. **即使最好的模型（Runway 73%），6 片段全合格率也只有 15%** — 开环不可能一次成功
6. **API 价格正在快速商品化** — 第三方定价比官方便宜 85-95%

---

## 3. 首次可用率与真实成本

### 3.1 各平台首次可用率

一次生成即可使用（无需重试）的概率：

```
Runway Gen-4    ████████████████████████████████████░░░░░░░░░░  73%
Pika 2.5        ██████████████████████████████████░░░░░░░░░░░░  68%
Kling 3.0       ████████████████████████████░░░░░░░░░░░░░░░░░░  ~60-65%
Seedance 2.0    ████████████████████████░░░░░░░░░░░░░░░░░░░░░░  ~55-65%
Luma            ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  40-70%
Pexels+CLIP     ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  40-50%
Google Veo 3.1  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  15-20%
```

### 3.2 每 10 秒视频的真实成本（含迭代）

| 方案 | 标价/10s | 迭代次数 | 真实成本/10s | API 来源 |
|------|---------|---------|-------------|---------|
| Pexels 素材 | $0 | 1 | **$0** | [pexels.com](https://www.pexels.com) |
| 开源 LTX-2 | $0（需 GPU） | 1 | **$0** | [github.com/Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) |
| 开源 Wan 2.2 | $0（需 GPU） | 1 | **$0** | [github.com/Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) |
| Hailuo | $0.19 | ~2 | $0.38 | [hailuoai.video](https://hailuoai.video) |
| Runway Turbo | $0.50 | ~2 | $1.00 | [runwayml.com](https://runwayml.com) |
| Kling 3.0 | $0.60-0.75 | ~2 | $1.20-1.50 | [klingai.com](https://klingai.com) / ModelsLab |
| Seedance 2.0 | $0.14/s 官方 | ~2 | $2.80 | 火山引擎 |
| Sora 2 | $1.00 | ~3 | $3.00 | [sora.com](https://sora.com) |
| Veo 3.1 Fast | $1.50 | **4-6** | **$6-9** | [aistudio.google.com](https://aistudio.google.com) |

### 3.3 开环质量基线（6 片段/条）

| 方案 | 首次可用率 | 6 片段全合格概率 | 说明 |
|------|-----------|----------------|------|
| Pexels+CLIP | 45% | 0.8% | 几乎不可能一次成功 |
| Seedance 2.0 | 60% | 4.7% | 20 条里约 1 条一次成功 |
| Kling 3.0 | 65% | 7.5% | 13 条里约 1 条一次成功 |
| Runway Gen-4 | 73% | **15.1%** | 7 条里约 1 条一次成功 |

**关键数字：即使首次可用率 73%（最高），6 片段全合格的概率也只有 15%。这就是为什么需要自动评分和筛选机制。**

---

## 4. 商业平台详细对比

### 4.1 Kling 3.0（快手）— 2026.02.05 发布

```
Text/Image Prompt → 多镜头生成(2-6 shots, 15s/shot) → 原生音频 → 角色绑定
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 原生 2K/4K，30fps（Pro 60fps） |
| 多镜头 | 单 prompt 2-6 镜头，可延展至 ~3 分钟 |
| 原生音频 | 音乐/音效/旁白/对话，跨语言支持 |
| 角色一致性 | Subject Reference（元素绑定）+ 参考驱动 |
| 运动控制 | V3.0 Pro Motion Control，物理感知（重力/惯性/形变） |
| 编辑 | Canvas Agent（故事板+多轮对话编辑） |
| 定价 | Free 66 daily credits; Std $6.99/mo; Pro $25.99/mo; Premier $64.99/mo; Ultra $180/mo |
| API | ModelsLab ~$0.12-0.15/s; PiAPI $10/mo/seat; 企业方案 $4,200/30K units |

### 4.2 Seedance 2.0（字节跳动）— 2026.02.12 中国发布

```
12 参考文件(图片/视频/音频) + Text Prompt → 多镜头叙事 + 原生音频 → 角色/风格一致
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 最高 2K |
| 多模态输入 | **最多 12 个参考文件**（图/视频/音频） |
| 原生音频 | 双声道，对话/环境音/音效/音乐同步 |
| 多语言唇形同步 | 英/中/西精确对齐 |
| 视频编辑 | 角色替换、内容增删、延展/拼接 |
| 定价 | 火山引擎 ~$0.14/s; Atlas Cloud $0.022/s (v1.5 Pro) |
| **风险** | **全球 API 因版权争议无限期推迟**（迪士尼/派拉蒙/MPA） |

### 4.3 Google Veo 3.1

```
Text Prompt → 8s 视频 + 原生音频 → 720p/1080p/4K
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 720p / 1080p / 4K |
| 最长时长 | 8 秒/片段 |
| 原生音频 | 音效/对话/环境音 |
| 竖版视频 | 原生 9:16 |
| 定价 | Fast $0.15/s; Standard $0.40/s |
| 配额 | Preview 10 RPM; Production 50 RPM |
| **问题** | **无免费视频配额；首次可用率仅 15-20%** |

### 4.4 Runway Gen-4 / Gen-4.5 — 2026.02.10 API 上线

```
Text/Image/Video Prompt → 2-60s 视频 → 4K → 关键帧/运动画刷控制
```

| 能力 | 详情 |
|------|------|
| 首次可用率 | **73%（最高）** |
| 分辨率 | 最高 4K |
| 时长 | Gen-4 最长 60s; Gen-4.5 2-10s |
| 原生音频 | ❌（唯一不支持的顶级模型） |
| 特色 | Motion Brush 3.0, Director Mode, 角色/环境一致性 |
| 集成 | Adobe Firefly, Envato VideoGen |
| 定价 | Free 125 credits; Std $12/mo; Pro $28/mo; Unlimited $76/mo |
| API | Gen-4 Turbo $0.05/s（最便宜的商业 API） |

### 4.5 Sora 2（OpenAI）

```
Text/Image Prompt → 5-25s 视频 → 1080p → 故事板/延展
```

| 能力 | 详情 |
|------|------|
| 时长 | 标准 5-15s; Pro 最长 25s（业界最长） |
| 原生音频 | 对话/音效/音乐同步 |
| 特色 | 故事板工具, 视频延展, Character Cameos |
| **限制** | **2026.01.10 免费层完全停止** |
| 定价 | ChatGPT Plus $20/mo (1000 credits); Pro $200/mo |
| API | $0.10/s (base); $0.30/s (Pro 720p); $0.50/s (Pro 1080p) |

### 4.6 Pika 2.5

| 能力 | 详情 |
|------|------|
| 时长 | 5-10 秒 |
| 特色 | Pikaffects 物理效果（粉碎/融化/膨胀/爆破）, 时间线编辑器, 唇形同步 |
| 定价 | Free 80 credits; Std $8/mo; Pro $28/mo; Fancy $76/mo |
| API | fal.ai ~$0.20/5s 720p |

### 4.7 Hailuo / MiniMax

| 能力 | 详情 |
|------|------|
| 特色 | 性价比最高的商业方案，AI 转场，自定义风格 |
| 定价 | Std $9.99/mo; Pro $34.99/mo; Ultra $124.99/mo; Max $199.99/mo |
| API | $0.19-0.56/video |

---

## 5. 开源工具与本地模型

### 5.1 开源视频生成模型

| 模型 | 来源 | 分辨率 | 时长 | 消费级 GPU | 许可证 | 特点 |
|------|------|--------|------|-----------|--------|------|
| **Wan 2.2** (5B) | 阿里巴巴 | 720p@24fps | ~5s | ✅ RTX 3080 (10GB) | MIT | VBench #1, MoE 架构 |
| **Wan 2.2** (27B) | 阿里巴巴 | 720p@24fps | ~5s | ❌ 需 A100 (~60GB) | MIT | 最高质量 |
| **LTX-2** | Lightricks | **4K@50fps** | 10-20s | ✅ RTX 4090 (24GB) | Apache 2.0 | 音频同步, NVIDIA CES 合作 |
| **CogVideoX** (5B) | 智谱 | 720x480 | ~6s | ✅ RTX 4090 (24GB) | Apache 2.0 | 稳定，入门友好 |
| **HunyuanVideo** | 腾讯 | 720p@24fps | ~5s | ❌ 需 A100 (40-80GB) | Open | 13B 参数, 高质量 |
| **Mochi 1** | Genmo | 480p@30fps | ~5.4s | ❌ 需 A100 (40-80GB) | Apache 2.0 | 10B, prompt 遵循强 |

**消费级 GPU 推荐：**
- **RTX 3080/4070 (10-12GB)**：Wan 2.2 (5B) — 720p, ~9 分钟/片段
- **RTX 4090 (24GB)**：LTX-2 — 原生 4K, 音频同步
- **WanGP 工具**声称支持低至 6GB 的旧显卡（RTX 10XX/20XX, AMD）

### 5.2 开源全管道工具

| 工具 | GitHub Stars | 画面来源 | 质量检测 | 最新版本 |
|------|-------------|---------|---------|---------|
| **[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)** | 55k+ | Pexels 关键词搜索 | ❌ | v1.2.6 (2025.05) |
| **[NarratoAI](https://github.com/linyqh/NarratoAI)** | ~5k | 用户上传视频 | ⚠️ VLM 场景分析 | — |
| **[ShortGPT](https://github.com/RayVentura/ShortGPT)** | ~5k | Pexels+YouTube | ❌ | — |
| **[Short Video Maker](https://github.com/gyoridavid/short-video-maker)** | ~1k | Pexels 搜索 | ❌ | — |
| **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** | — | 本地 AI 模型 | ❌ | 持续更新 |

**关键发现：没有任何开源工具实现了自动质量检测或纠错闭环。** 所有工具都是"生成即交付"模式。

### 5.3 MoneyPrinterTurbo 为什么有 55k Stars

不是因为技术强，而是因为：
1. **零成本** — Pexels 免费素材
2. **一键出片** — Web UI，极低使用门槛
3. **批量生成** — 量大取胜
4. **不依赖 GPU** — 任何机器都能跑

**核心瓶颈：** Pexels 关键词搜索太粗糙 → 素材与脚本语义不匹配（质量问题 #1）。用 CLIP 语义匹配替代是最小投入最大回报的升级。

---

## 6. 内容创作者实际工作流

### 6.1 "短视频工厂"标准流程

```
选定垂直领域 → LLM 生成脚本 → TTS 配音 → 画面素材 → 字幕 → 人工快审 → 批量发布
                                           │
                            ┌──────────────┼──────────────┐
                            │              │              │
                       Pexels 搜索    AI 头像/口播    AI 生成视频
                       (最常见)       (次常见)        (高端用户)
```

### 6.2 产量与人工介入

| 创作者类型 | 产量 | 人工介入 |
|-----------|------|---------|
| 内容工厂 | 200-300 条/月（7-10 条/天） | 最小化 |
| 自动化频道 | 30-60 条/月（1-2 条/天） | 15-30 分钟/条 |
| 质量导向 | 1 条/天 | 1-2 小时/条 |
| 混合模式（头部） | 80% AI 量产 + 20% 人工精修 | 视内容类型 |

### 6.3 质量控制现状

| 方式 | 使用率 | 描述 |
|------|-------|------|
| **人工快审** | 最高 | 15-30 秒看一遍 |
| **批量生成+筛选** | 高 | "生成 10 个，挑 1 个" |
| **A/B 测试** | 中 | 发布多版本，让算法选赢家 |
| **自动质量门控** | **无** | 没有任何工具提供 |

### 6.4 中国市场工具链

| 工具 | URL | 定位 |
|------|-----|------|
| **即梦 Dreamina** | [jimeng.jianying.com](https://jimeng.jianying.com) / [dreamina.capcut.com](https://dreamina.capcut.com) | 字节跳动视频生成（Seedance） |
| **可灵 Kling** | [klingai.com](https://klingai.com) | 快手 4K/60fps 视频生成 |
| **海螺 Hailuo** | [hailuoai.video](https://hailuoai.video) | MiniMax 性价比视频生成 |
| **剪映 Jianying** | [jianying.com](https://jianying.com) | 字节跳动编辑器，集成即梦 |
| **豆包 Doubao** | [doubao.com](https://doubao.com) | 字节跳动 AI 助手，内置 Seedance |
| **WaveSpeedAI** | [wavespeed.ai](https://wavespeed.ai) | 多模型聚合平台（600+ 模型） |
| **即创 iClip** | — | RPA 机器人：采集/适配/发布/多账号 |

### 6.5 自动化工作流引擎 (2026 最新基建)

目前商业化团队和极客创作者正在将分散的 API 通过**自动化引擎**串联，实现 "Agentic Workflow"（智能体工作流）：

1. **节点式本地管道（视觉向）：ComfyUI**
   - **定位**：最高自由度的视觉控制管道。
   - **用法**：通过安装 LTX-2, Wan 2.2, 或 HunyuanVideo 的自定义节点，实现从 `Midjourney生图 -> ComfyUI局部重绘 -> ComfyUI视频生成 -> 自动放大(Upscale)` 的全本地自动化。适合有高配 GPU（24GB+ VRAM）的极客工作室。

2. **低代码 Agent 平台（逻辑向）：Coze / Dify / FastGPT**
   - **定位**：LLM 驱动的商业全自动流水线。
   - **用法**：在 Coze 中编排 Agent，触发词为“帮我生成一个助眠枕头广告”。
     - 节点 A（LLM）：解析用户需求，输出 5 段分镜 Prompt。
     - 节点 B（API）：调用 Runway / Seedance 官方或第三方聚合 API 生成视频。
     - 节点 C（API）：调用 ElevenLabs TTS 生成配音。
     - 节点 D（代码）：调用 FFmpeg 脚本或 CapCut API 自动合并。
   - **优势**：极大地降低了人工复制粘贴 Prompt 的成本，实现从“文案到成片”的闭环。

3. **企业级集成：Make.com / n8n / Zapier**
   - **定位**：触发器与多平台分发中心。
   - **用法**：监听 Notion 数据库状态。当内容策划将状态改为“Ready”，n8n 自动抓取内容 -> 调用 Coze 的视频生成 Agent -> 下载成品 -> 自动发布到 YouTube Shorts 和 TikTok。

---

## 7. 十大质量问题

### 7.1 按频率排序

| # | 问题 | 影响工具类型 | 可自动检测？ | 可自动修复？ |
|---|------|------------|------------|------------|
| 1 | **素材-脚本语义失配** | 素材搜索型 | ✅ CLIP 余弦 | ⚠️ 重新搜索 |
| 2 | **音画不协调** | 全类型 | ✅ 节奏分析 | ❌ 需重编排 |
| 3 | **角色一致性差** | AI 生成型 | ⚠️ 人脸嵌入 | ❌ 需 consistent ID |
| 4 | **镜头运动混乱** | AI 生成型 | ✅ 光流分析 | ❌ 需重生成 |
| 5 | **唇形不同步** | 口播/头像型 | ✅ A/V sync | ⚠️ 可重对齐 |
| 6 | **环境不一致** | AI 生成型 | ⚠️ VLM 判断 | ❌ 需重生成 |
| 7 | **压缩伪影** | 合成型 | ✅ NIQE/VMAF | ⚠️ 可重编码 |
| 8 | **内容泛化/重复** | 全类型 | ⚠️ 语义分析 | ❌ 需人工介入 |
| 9 | **AI 痕迹明显** | AI 生成型 | ⚠️ 检测模型 | ❌ 模型能力限制 |
| 10 | **叙事断裂** | 全类型 | ⚠️ VLM 判断 | ❌ 需重编排 |

### 7.2 按工具类型分布

```
素材搜索型（MoneyPrinterTurbo 等）: #1 素材失配 > #2 音画不协调 > #7 压缩伪影
AI 生成型（Veo/Runway/Kling）:     #3 角色一致性 > #4 镜头混乱 > #6 环境不一致
口播/头像型（HeyGen/Synthesia）:   #5 唇形同步 > #8 内容泛化 > #9 AI 痕迹
```

---

## 8. 市场空白与机会

```
已解决（技术成熟）:                   未解决（机会空间）:
─────────────────                   ─────────────────
✅ 脚本生成（LLM）                    ❌ 自动质量评估（所有人靠肉眼）
✅ TTS（Edge-TTS 免费够用）            ❌ 批量生成自动排序/筛选
✅ 字幕（Whisper）                    ❌ 失败后自动 Prompt 纠正
✅ 合成（FFmpeg）                     ❌ 素材-脚本语义匹配（关键词→CLIP）
✅ AI 视频生成（多平台成熟）           ❌ 跨镜头角色/场景一致性
```

> **"AI 视频生成就是掷骰子。"** — Reddit 用户
>
> 87% 的失败内容通过更好的 Prompt 可以成功。但 Prompt 优化目前完全手动。没有任何工具将 Prompt 优化自动化。

---

## 9. 路线决策：先 B 后 A

### 9.1 两条路线

| | 路线 A：质量闭环 | 路线 B：批量筛选 |
|--|----------------|----------------|
| **问题** | "这个视频哪里不好？怎么改？" | "这 N 个里哪个最好？" |
| **方法** | 生成→评估→诊断→改prompt→重试 | 并行生成N个→评分→选最佳 |
| **类比** | 编译器优化 | MapReduce |
| **学术基础** | VISTA 闭环提升 60% | 行业"生成 10 挑 1" |
| **延迟** | 高（串行 ~9 分钟） | 低（并行 ~1 分钟） |
| **差异化** | 强（无竞品） | 中（容易模仿） |

### 9.2 成本模型（Kling 3.0, $0.12/s, 首次可用率 60%, 6 片段/条）

| 维度 | 路线 A | 路线 B (N=3) | **路线 C (B+A)** |
|------|-------|-------------|-----------------|
| 成本/条 | ~$4.60 | ~$8.10 | **~$6.00** |
| 耗时/条 | ~9 分钟 | ~1 分钟 | **~2 分钟** |
| 全通过率 | ~100% | 67.8% | **97%+** |

### 9.3 分阶段计划

```
阶段 1：评分验证（共同基础）
  → 跑 100 条真实视频，验证 L1+L2 评分与人工判断的相关性
  → 交付：经验证的评分模块

阶段 2：路线 B（批量+筛选）
  → 每片段 N=2 候选 → 评分选最佳
  → 副产物：积累 "prompt→视频→评分" 三元组数据

阶段 3：路线 A（数据驱动纠错）
  → 用阶段 2 数据训练 prompt 重写
  → 只对筛选后仍未通过的片段做闭环
```

### 9.4 决策记录

> **决策：采用路线 C（先 B 后 A），分三阶段迭代。**
>
> 理由：评分是共同基础，B 为 A 提供训练数据，风险逐阶段递减。
>
> 默认生成方案：Kling 3.0 第三方 API。
>
> 决策日期：2026-03-14

---

## 10. 完整工具链索引

### 10.1 AI 视频生成

| 工具 | URL | 核心能力 | 定价 | API |
|------|-----|---------|------|-----|
| **Kling 3.0** | [klingai.com](https://klingai.com) | 4K/60fps+多镜头+原生音频 | Free 66 daily; Std $6.99/mo | ✅ ~$0.12/s |
| **Seedance 2.0** | [dreamina.capcut.com](https://dreamina.capcut.com) | 2K+12文件多模态+原生音频 | Free 225 daily; Basic $18/mo | ⚠️ 中国+第三方 |
| **Veo 3.1** | [aistudio.google.com](https://aistudio.google.com) | 4K+原生音频+竖版 | AI Pro $19.99/mo | ✅ $0.15/s Fast |
| **Runway Gen-4.5** | [runwayml.com](https://runwayml.com) | 最高视觉保真+60s长视频 | Free 125 credits; Std $12/mo | ✅ $0.05/s Turbo |
| **Sora 2** | [sora.com](https://sora.com) | 最长视频(25s)+故事板+延展 | Plus $20/mo | ✅ $0.10-0.50/s |
| **Pika 2.5** | [pika.art](https://pika.art) | 物理效果+唇形同步 | Free 80 credits; Std $8/mo | ✅ fal.ai |
| **Hailuo** | [hailuoai.video](https://hailuoai.video) | 性价比最高 | Std $9.99/mo | ✅ $0.19/video |
| **Luma** | [lumalabs.ai](https://lumalabs.ai) | 3D/VFX 专长 | Free 30 gens; Lite $9.99/mo | ⚠️ 有限 |
| **Adobe Firefly** | [firefly.adobe.com](https://firefly.adobe.com) | 商业安全, Premiere 集成 | Creative Cloud | ✅ |
| **LTX Studio** | [ltx.studio](https://ltx.studio) | 全片+故事板+角色控制 | Free 800 credits; Lite $15/mo | ✅ |

### 10.2 视频编辑

| 工具 | URL | 定位 | 定价 |
|------|-----|------|------|
| **CapCut** | [capcut.com](https://capcut.com) | AI 编辑 | Free; Pro $19.99/mo |
| **Descript** | [descript.com](https://descript.com) | 转录即编辑 | Free; Pro $30/mo |
| **OpusClip** | [opus.pro](https://opus.pro) | 长→短提取 | Free; Starter $15/mo |

### 10.3 AI 头像 / 配音

| 工具 | URL | 定位 | 定价 |
|------|-----|------|------|
| **HeyGen** | [heygen.com](https://heygen.com) | AI 头像+175 语言 | Free; Creator $29/mo |
| **Synthesia** | [synthesia.io](https://synthesia.io) | 企业级数字人 | 企业定价 |
| **ElevenLabs** | [elevenlabs.io](https://elevenlabs.io) | 语音生成+克隆 | Free 10K; Pro $99/mo |
| **edge-tts** | [github.com/rany2/edge-tts](https://github.com/rany2/edge-tts) | 免费 TTS | 免费 |

### 10.4 开源项目

| 项目 | GitHub | 特点 |
|------|--------|------|
| **Wan 2.2** | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | VBench #1, 10GB 可跑, MIT |
| **LTX-2** | [Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) | 4K+音频, 12GB+, Apache 2.0 |
| **ComfyUI** | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) | 节点式工作流, GPL-3.0 |
| **CogVideoX** | [zai-org/CogVideo](https://github.com/zai-org/CogVideo) | 智谱, Apache 2.0 |
| **HunyuanVideo** | [Tencent/HunyuanVideo](https://github.com/Tencent/HunyuanVideo) | 腾讯 13B |
| **MoneyPrinterTurbo** | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 55k stars, 一键出片, MIT |
| **NarratoAI** | [linyqh/NarratoAI](https://github.com/linyqh/NarratoAI) | VLM 场景分析+解说 |

### 10.5 素材库

| 平台 | URL | 定价 |
|------|-----|------|
| **Pexels** | [pexels.com](https://www.pexels.com) | 完全免费, 200 req/hr |
| **Pixabay** | [pixabay.com](https://pixabay.com) | 完全免费 |

---

## 附录 A：数据来源

| 来源 | 用途 |
|------|------|
| [Kling AI](https://klingai.com) + [Kuaishou/Nasdaq](https://nasdaq.com) | Kling 3.0 发布确认 |
| [Seedance 2.0 / Dreamina](https://dreamina.capcut.com) | 字节跳动视频生成 |
| [火山引擎](https://volcengine.com) + [Atlas Cloud](https://atlascloud.ai) | Seedance API 定价 |
| [Google AI Studio](https://aistudio.google.com) | Veo 3.1 配额/定价 |
| [Runway ML](https://runwayml.com) + [releasebot.io](https://releasebot.io) | Gen-4.5 确认 |
| [Sora / OpenAI](https://sora.com) + [PCMag](https://pcmag.com) | Sora 2 定价/限制 |
| [Pika](https://pika.art) | Pika 2.5 功能 |
| [NVIDIA CES/GDC 2026](https://nvidia.com) | LTX-2 + ComfyUI 更新 |
| [ModelsLab](https://modelslab.com) + [PiAPI](https://piapi.ai) | 第三方 API 定价 |
| [MoneyPrinterTurbo GitHub](https://github.com/harry0703/MoneyPrinterTurbo) | 开源工具分析 |
| [LTX-2](https://github.com/Lightricks/LTX-2) + [TechPowerUp](https://techpowerup.com) | 本地模型确认 |
| [Wan 2.2](https://github.com/Wan-Video/Wan2.2) + [Stackademic](https://stackademic.com) | 开源模型数据 |
| [WaveSpeedAI](https://wavespeed.ai) | 中国市场多模型聚合 |
| Reddit r/aivideo, r/StableDiffusion | 用户真实反馈/首次可用率 |
| [36kr](https://36kr.com) | 中国 AI 视频市场 |

## 附录 B：术语表

| 术语 | 定义 |
|------|------|
| 首次可用率 | 一次生成即可使用（无需重试）的概率 |
| 管道坍缩 | 原生音频模型将 TTS+BGM 步骤吸收，6 步管道变为 4 步 |
| B-roll | 辅助画面素材，用于覆盖旁白 |
| 素材失配 | 画面内容与脚本/旁白语义不一致 |
| 闭环纠错 | 自动评估 → 诊断 → 改 prompt → 重生成的循环 |
| 开环生成 | 生成后不自动评估和纠正，依赖人工审核 |
| 路线 B | 批量生成 N 个候选 → 自动评分 → 选最佳 |
| 路线 A | 评估 → 诊断 → prompt 重写 → 重生成 → 再评估 |
| 路线 C | 先 B（批量筛选）后 A（纠错），混合策略 |


<br><br>

---



<!-- FILE: 08-best-practices.md -->
# 08 — AI 短视频生产最佳实践指南 (2026.03)

> 这不是分析报告，而是可以直接照着做的实操手册。每个环节给出具体工具、参数、和操作步骤。

---

## 快速开始：三套推荐工作流

### 工作流 A：零成本起步（免费工具链）

```
DeepSeek 写脚本 → Edge-TTS 配音 → Pexels 素材 → CapCut 自动字幕 → YouTube Audio Library 配乐 → CapCut 合成
```

成本：**$0/条** | 用时：~15 分钟/条 | 适合：验证想法、起步阶段

### 工作流 B：性价比生产（~$10/月）

```
GPT-4o-mini 写脚本 → Fish Audio 配音 → Kling 3.0 免费层生成视频 → CapCut 自动字幕+剪辑 → BGM → 发布
```

成本：**~$0.50-1.00/条** | 用时：~10 分钟/条 | 适合：日常量产

### 工作流 C：全自动管道（MoneyPrinterTurbo）

```
输入主题 → 一键生成（脚本+配音+Pexels素材+字幕+BGM+合成）→ 人工快审 → 发布
```

成本：**$0/条** | 用时：~5 分钟/条（含审核） | 适合：批量生产、无人值守
GitHub: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)

---

## 第 1 步：脚本生成

### 用什么 LLM

| 场景 | 推荐 | 理由 |
|------|------|------|
| 中文短视频 | **豆包 / DeepSeek** | 中文语感最好，理解国内短视频风格 |
| 英文短视频 | **GPT-4o / Claude** | 创意写作能力强 |
| 预算为零 | **DeepSeek**（API 免费额度）| 质量接近 GPT-4o，免费 |
| 批量生产 | **GPT-4o-mini / DeepSeek** | 成本低，速度快 |

### 脚本结构公式（Hook-Build-Body-CTA）

**每个视频必须包含这 4 个部分：**

| 部分 | 60 秒视频 | 30 秒视频 | 作用 |
|------|----------|----------|------|
| **Hook（钩子）** | 0-3 秒 | 0-2 秒 | 抓住注意力，阻止划走 |
| **Build（铺垫）** | 3-15 秒 | 2-8 秒 | 建立语境，制造期待 |
| **Body（主体）** | 15-45 秒 | 8-22 秒 | 交付核心价值 |
| **CTA（号召）** | 45-60 秒 | 22-30 秒 | 引导行动（关注/点赞/评论） |

**字数参考：**
- 30 秒视频：80-100 字（中文）/ 80-100 words（英文）
- 60 秒视频：150-200 字（中文）/ 120-150 words（英文）

### 钩子的 6 种写法（前 3 秒决定生死）

观众在 **3 秒内**决定是否继续看。平均注意力已降至 8.25 秒。

| 类型 | 中文示例 | 适合内容 |
|------|---------|---------|
| **反常识** | "99% 的人不知道，手机充电其实不该充到 100%" | 知识科普 |
| **提问** | "你有没有想过，为什么飞机窗户是圆的？" | 教育、好奇 |
| **痛点** | "还在为失眠发愁？试试这个方法" | 实用技巧 |
| **结果前置** | "最终效果是这样的——（展示成品）" | 教程、变身 |
| **强声明** | "这一个习惯，彻底改变了我的生活" | 个人成长 |
| **动态开场** | （直接用动态画面开始，不要静态图） | 任何类型 |

### 给 LLM 的 Prompt 模板

```
你是一位专业短视频编剧，擅长写出高完播率的脚本。

请为以下主题写一个 {30/60} 秒短视频脚本：
主题：{topic}
平台：{抖音/TikTok/YouTube Shorts}
风格：{知识科普/叙事/教程/评测}

要求：
1. 必须包含 Hook(0-3s)、Build、Body、CTA 四部分
2. Hook 必须在前 3 秒抓住注意力，使用{反常识/提问/痛点/结果前置}手法
3. 每个场景标注[场景描述]用于匹配画面
4. 语言自然口语化，避免书面语
5. 字数控制在 {150-200} 字

输出格式：
场景1 [0-3s] Hook：...
场景2 [3-10s] Build：...
场景3 [10-25s] Body：...
场景4 [25-30s] CTA：...
```

---

## 第 2 步：配音（TTS）

### 工具选择

| 预算 | 工具 | 中文推荐声音 | 英文推荐声音 | 怎么用 |
|------|------|------------|------------|--------|
| **$0** | Edge-TTS | `zh-CN-XiaoxiaoNeural`（女，温暖）`zh-CN-YunxiNeural`（男，活力） | `en-US-JennyNeural` | `pip install edge-tts` → `edge-tts --text "内容" --voice zh-CN-XiaoxiaoNeural -o output.mp3` |
| **$5.5/月** | Fish Audio | 丰富声音库 + 50+ 情感标记 | 多语言 | [fish.audio](https://fish.audio) |
| **$5/月** | ElevenLabs | 可用但非最优 | **最佳英文 TTS** | [elevenlabs.io](https://elevenlabs.io) |
| **免费（自部署）** | IndexTTS-2 | **最佳中文自然度** | — | 本地部署，一键安装 |
| **免费（自部署）** | CosyVoice | 18 种方言 + 跨语言克隆 | — | 阿里开源，150ms 延迟 |

### 配音参数调优

| 参数 | 知识科普 | 娱乐/快节奏 | 情感/叙事 |
|------|---------|-----------|----------|
| **语速** | 1.0-1.1x | 1.15-1.25x | 0.95-1.0x |
| **音调** | 默认 | 略高 (+5-10%) | 略低 (-5%) |
| **停顿** | 关键点后 0.3-0.5s | 最小化 | 情感转折处 0.5-1.0s |

### Edge-TTS 注意事项

Edge-TTS 使用逆向工程的微软 API，**无官方 SLA**，可能随时被封。适合原型和低成本生产，不适合商业关键业务。商业用途建议 Azure AI Speech 或 Fish Audio。

---

## 第 3 步：字幕

### 2026 标配：逐字高亮（卡拉 OK 字幕）

这是当前短视频的**标准字幕样式** — 每个词随语音同步变色/变大。

**为什么必须用：**
- 提升完播率 65%（听+读双通道吸收）
- 85% 的社交媒体视频在静音状态下观看
- 更长的观看时长 = 算法给更多推荐

### 字幕参数规范

| 参数 | 推荐值 |
|------|--------|
| 字体 | 无衬线体（思源黑体/Montserrat），**粗体** |
| 大小 | 在手机上清晰可读（必须实机测试！） |
| 每行字数 | 中文 8-12 字，英文 3-5 词 |
| 行数 | 最多 2 行 |
| 位置 | 屏幕中间偏下 1/3（避开平台 UI） |
| 高亮色 | 黄色最常见；必须与文字色有强对比 |
| 时间同步 | 比语音**提前 0.1-0.2 秒**出现 |

### 最佳工具

| 工具 | 优势 | 适合 |
|------|------|------|
| **CapCut / 剪映** | 一键自动生成 + 卡拉 OK 样式，中文最优 | 所有人 |
| **Whisper** | 开源，自部署，词级时间戳 | 开发者 |
| **讯飞听见** | 中文识别准确率最高 | 精品内容 |
| **VEED** | 140 语言自动翻译 | 跨国内容 |

### CapCut 字幕操作流程

1. 导入带旁白音频的视频
2. 文本 → 自动字幕 → 选择语言
3. 选择字幕样式（推荐卡拉 OK 高亮）
4. 自定义字体、颜色、位置
5. 逐条检查修正识别错误
6. 导出

---

## 第 4 步：配乐与音效

### 混音音量标准（关键数字）

| 音频类型 | 音量 (dBFS) | 说明 |
|---------|------------|------|
| **旁白/对话** | -10 至 -12 | 主音频，必须清晰 |
| **BGM（有对话时）** | -20 至 -30 | 比旁白低至少 20dB |
| **BGM（无对话时）** | -10 至 -14 | 过渡段可以适当提高 |
| **音效** | -12 至 -18 | 点状的，不要持续 |

**经验法则：BGM 在有旁白时降到旁白音量的 15-20%。用音量自动化（ducking）在旁白段压低 BGM、在停顿段提高。**

### 免费音乐来源

| 来源 | URL | 特点 |
|------|-----|------|
| **YouTube Audio Library** | YouTube Studio 内置 | YouTube Shorts 安全 |
| **Pixabay Music** | [pixabay.com/music](https://pixabay.com/music) | 完全免费 |
| **Fesliyan Studios** | [fesliyanstudios.com](https://fesliyanstudios.com) | 有专门的"对话背景音乐"分类 |
| **爱给网** | [aigei.com](https://aigei.com) | 中文最全的免费音效/BGM 库 |
| **Uppbeat** | [uppbeat.io](https://uppbeat.io) | 创作者免费层 |

### AI 生成音乐

| 工具 | URL | 特点 |
|------|-----|------|
| **Soundraw** | [soundraw.io](https://soundraw.io) | 自定义心情/时长/风格 |
| **BGM 猫** | [bgmcat.com](https://bgmcat.com) | AI 生成 BGM |

### 必备音效库

短视频常用的 6 类音效（建议提前收集）：

| 类型 | 用途 | 获取 |
|------|------|------|
| **Whoosh（嗖）** | 场景切换 | Pixabay/爱给网 |
| **Riser（渐强）** | 制造期待 | Pixabay/爱给网 |
| **Hit/Impact（撞击）** | 重点强调 | Pixabay/爱给网 |
| **Pop/Ding（叮）** | 文字出现、要点 | Pixabay/爱给网 |
| **Click（咔）** | UI 操作、指向 | Pixabay/爱给网 |
| **Bubble（咕噜）** | 轻松/趣味内容 | Pixabay/爱给网 |

---

## 第 5 步：视频合成与剪辑

### 分辨率与画幅

| 平台 | 画幅 | 分辨率 | 说明 |
|------|------|--------|------|
| 抖音/TikTok | 9:16 竖屏 | 1080×1920 | **必须竖屏，不要从横屏裁切** |
| YouTube Shorts | 9:16 竖屏 | 1080×1920 | 同上 |
| Instagram Reels | 9:16 竖屏 | 1080×1920 | 同上 |
| B 站 | 16:9 或 9:16 | 1920×1080 或 1080×1920 | 16:9 仍然主流 |
| YouTube 长视频 | 16:9 横屏 | 1920×1080 | 保留横版母版用于复用 |

**核心原则：从一开始就按 9:16 竖版制作。从 16:9 裁切到 9:16 效果一定很差。**

### 剪辑节奏

| 内容类型 | 每个镜头时长 | 节奏感 |
|---------|------------|--------|
| 快节奏/娱乐 | 0.5-2 秒 | 密集跳切 |
| 教程/展示 | 2-5 秒 | 适中 |
| 叙事/故事 | 3-8 秒 | 稳重 |
| 所有类型 | — | **删掉所有空白、停顿、废镜头** |

**2026 趋势：** 干净极简的转场。花哨的特效转场已经过时。有目的的、微妙的转场才是当前风格。

### 转场选择

| 转场 | 何时用 | 频率 |
|------|-------|------|
| **直接切** | 默认，大部分场景 | 80%+ |
| **交叉溶解** | 情绪变化、时间跳跃 | 10% |
| **滑动/推移** | 列表、并列内容 | 5% |
| **匹配剪辑** | 同形状/动作跨场景 | 5%（高级技巧） |

### 色彩调校

1. **先校正**：白平衡、曝光（修正主镜头）
2. **再匹配**：所有其他镜头匹配到主镜头
3. **最后调色**：应用 LUT 或手动调整设定风格
4. **保持一致**：系列视频用相同调色方案建立品牌识别

---

## 第 6 步：发布与分发

### 最佳发布时间

| 平台 | 最佳时段 | 次优时段 |
|------|---------|---------|
| **抖音** | 18:00-22:00 | 7:30-8:30（通勤）, 12:00-13:00（午休） |
| **TikTok** | 10:00-11:00 (EST) 周二-四 | 19:00-21:00 |
| **YouTube Shorts** | 14:00-16:00 (EST) | 20:00-22:00 |
| **Instagram Reels** | 11:00-13:00 | 19:00-21:00 |

### 多平台分发策略

**不要直接把同一个视频搬运到所有平台。** 每个平台的算法、用户行为不同：

| 维度 | 抖音/TikTok | YouTube Shorts | Instagram Reels |
|------|-----------|---------------|-----------------|
| 内容生命周期 | 24-48 小时 | **数周到数月** | 24-48 小时 |
| 算法首轮测试 | 第 1 小时 | 前 2 小时 | 第 1 小时 |
| SEO/搜索 | 日益重要 | **最强（Google 搜索）** | 标签驱动 |
| 音频策略 | 热门音乐加分 | 原创音频即可 | 热门音乐加分 |

### 抖音 SEO（2025 算法更新后）

抖音推荐引擎升级为"兴趣图谱 + 场景匹配"双引擎模型：

- **关键词布局**：账号名、视频标题、字幕文字、文案、话题标签
- **关键词结构**：痛点 + 解决方案（如"零基础健身跟练"）
- **搜索 GMV** 大幅增长——必须优化搜索排名
- **评论区 SEO**：评论关键词影响搜索排名。设计互动引导（"评论区交作业"）
- **算法同时考虑**"情感共鸣"和"AI 识别匹配"（标签准确度、创新指数）

### 封面设计

- **视觉冲击力**：第一帧/封面必须有极高吸引力
- **固定封面风格 + 高对比色** 强化账号视觉识别
- **教程类**：前 5 秒展示大纲；**评测类**：首帧突出产品；**娱乐类**：用热门 BGM

---

## 完整工作流详解

### 工作流 A：一人工作室（半自动，已验证）

这是个人创作者最成熟的工作流，已被验证可以产生百万级播放量：

```
第 1 步：脚本生成（AI，2 分钟）
  ├── 工具：ChatGPT / 豆包 / DeepSeek
  ├── 输入：主题 + Prompt 模板（见第 1 步）
  └── 输出：带场景标注的结构化脚本

第 2 步：配音（TTS，1 分钟）
  ├── 工具：Edge-TTS（免费）或 Fish Audio（$5.5/月）
  ├── 参数：语速 1.0-1.15x，关键点后加停顿
  └── 输出：narration.mp3

第 3 步：画面素材（AI/素材库，5 分钟）
  ├── 方案 A：Pexels 搜索 + CLIP 语义排序（$0）
  ├── 方案 B：Kling 3.0 免费层生成（$0，每天 66 积分）
  ├── 方案 C：MidJourney/DALL-E 生成图片（~$0.05/张）
  └── 输出：每场景对应的视频/图片文件

第 4 步：组装剪辑（CapCut/剪映，5 分钟）
  ├── 导入画面 + 音频
  ├── 对齐时间线
  ├── 自动生成卡拉 OK 字幕
  ├── 添加 BGM（旁白段 ducking 到 15-20%）
  ├── 添加转场音效
  └── 输出：初稿视频

第 5 步：人工审核（2-3 分钟）
  ├── 检查前 3 秒钩子是否有力
  ├── 修正字幕识别错误
  ├── 调整节奏/时间
  ├── 快速调色
  └── 输出：终稿视频

第 6 步：发布（1 分钟）
  ├── 按平台导出版本
  ├── 写 SEO 优化的标题/话题标签
  ├── 选择最佳发布时间
  └── 发布
```

**总用时：~15 分钟/条 | 成本：$0-1/条 | 一人可完成原本 3 人团队的工作量**

### 工作流 B：MoneyPrinterTurbo 全自动

```
第 1 步：输入主题
  └── Web UI 填入主题/关键词

第 2 步：配置参数
  ├── LLM 提供商（OpenAI/DeepSeek/Gemini/Ollama）
  ├── TTS 引擎（Edge-TTS/GPT-SoVITS/Azure）
  ├── 视频比例（9:16 或 16:9）
  ├── 字幕样式（字体/颜色/位置/大小）
  └── BGM 设置（随机/指定/音量）

第 3 步：一键生成
  └── 系统自动完成：脚本→配音→Pexels 素材→字幕→BGM→FFmpeg 合成

第 4 步：人工快审（2-3 分钟）
  ├── 检查素材是否与脚本匹配
  ├── 检查画质是否可接受
  └── 确认字幕无明显错误

第 5 步：发布
```

**总用时：~5 分钟/条 | 成本：$0 | 适合批量生产**

### 工作流 C：n8n / Make 自动化管道（高级）

```
n8n/Make 工作流编排：
  ├── Trigger：Notion/Airtable 状态变更
  ├── Step 1：LLM（Claude/GPT-4o）→ 脚本 + Prompt 优化
  ├── Step 2：AI 视频（Kling/Runway/Seedance via API）→ 视觉素材
  ├── Step 3：TTS（ElevenLabs/Fish Audio）→ 旁白
  ├── Step 4：FFmpeg（custom code node）→ 合成 + 动态场景切割
  ├── Step 5：Whisper.cpp → 字幕生成
  └── Step 6：平台 API → 多平台发布（TikTok/Instagram/YouTube/Facebook）
```

**适合：** 技术型创作者，需要完全自定义管道。

### 工作流 D：Agentic Workflow (Coze / Dify 智能体流，2026 前沿)

```
第 1 步：创建智能体 (Agent)
  └── 在 Coze 或 Dify 中搭建，设定身份为“全能短视频制作人”。

第 2 步：配置工作流节点
  ├── 意图识别节点：分析输入主题。
  ├── 创意发散节点：调用 DeepSeek 输出 5 个分镜。
  ├── 并行生成节点：调用生图 API (Midjourney) 和 生视频 API (Seedance)。
  ├── 配音节点：调用 TTS API。
  └── 合成输出节点：返回合并后的 MP4 下载链接。

第 3 步：对话式生产
  └── 用户只需输入：“帮我做一个智能助眠枕头广告，主打物理减压”。Agent 自动跑通全流程。
```

**适合：** 团队协作，极大地降低了人工在各网页端切换复制粘贴的成本。

### 工作流 E：AI 原生视频（Kling 3.0 / Seedance 2.0 多镜头，2026 新范式）

```
第 1 步：结构化脚本
  └── LLM 输出多镜头描述（含角色、场景、动作、情感、音效提示）

第 2 步：Kling/Seedance 多镜头生成
  ├── 单 prompt 输入结构化脚本 / 导入多张垫图
  ├── 自动生成 2-6 个连贯镜头 + 原生音频
  ├── 角色 Subject Reference (`@`标签系统) 保持一致性
  └── 输出：一条完整的多镜头视频+音频

第 3 步：微调
  └── 快速调色，配上卡拉 OK 字幕。
```

**这是 2026.02 之后的新范式** — 管道从 6 步坍缩为 3-4 步，AI 模型一次生成视频+音频+多镜头叙事。

---

## 按预算选工具

| 预算 | 脚本 | 配音 | 字幕 | 视频/画面 | 配乐 | 剪辑 |
|------|------|------|------|----------|------|------|
| **$0** | DeepSeek | Edge-TTS | CapCut 自动 | Pexels + CapCut | Pixabay / YouTube 音乐库 | CapCut |
| **~$10/月** | GPT-4o-mini | Fish Audio | CapCut 自动 | Kling 免费层 | Uppbeat | CapCut |
| **~$50/月** | Claude / GPT-4o | ElevenLabs | CapCut + 人工 QA | Runway $28 / Kling $26 | Envato Elements | CapCut / Premiere |
| **自部署** | Ollama 本地 | IndexTTS-2 / CosyVoice | Whisper 本地 | Wan 2.2 / LTX-2 本地 | Soundraw | FFmpeg |

---

## 核心原则

### 1. 高频更新 > 极致特效

> 对于流量增长，**频繁发布**质量合格的内容，远好于偶尔发布完美的内容。先优化产量，再打磨最佳表现者。

### 2. 3 秒定生死

> 第一帧就必须有动态画面和强吸引力。永远不要用静态图开场。

### 3. 手机测试

> 所有内容必须在手机上预览。桌面上好看的字幕在手机上可能看不清。

### 4. 音频比画面更重要

> 73% 的爆款视频靠音画协调成功。宁可画面一般但音频精致，不要画面华丽但配音刺耳。

### 5. 结构化 > 随意

> 每一步都用固定结构（脚本公式、Prompt 模板、字幕规范、混音标准）。固定结构 = 稳定质量 = AI 可自动化。

### 6. 长镜头“接力”与一致性锁定 (2026 进阶法则)

> 超过 10 秒的视频极易出现“身份漂移”和背景崩坏。对于长镜头，请使用“首尾帧接力法（Recursive Extension）”——提取上一段最后一帧作为下一段首帧。对于角色，务必利用 Seedance 的 `@` 标签系统或 Runway 的 Act-One 功能进行强行锁定。详情见《全景解析》。

---

## 附录：数据来源

| 来源 | 内容 |
|------|------|
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 开源全自动工具 |
| [Fish Audio](https://fish.audio) | TTS 平台 |
| [ElevenLabs](https://elevenlabs.io) | TTS 平台 |
| [Edge-TTS](https://github.com/rany2/edge-tts) | 免费 TTS |
| [IndexTTS-2](https://github.com/indexteam/indextts2) | 中文 TTS |
| [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) | 阿里开源 TTS |
| [CapCut](https://capcut.com) / [剪映](https://jianying.com) | 视频编辑+字幕 |
| [Kling AI](https://klingai.com) | AI 视频生成 |
| [Pexels](https://pexels.com) | 免费素材 |
| [Pixabay Music](https://pixabay.com/music) | 免费音乐 |
| [爱给网](https://aigei.com) | 中文音效/BGM |
| [Fesliyan Studios](https://fesliyanstudios.com) | 免费 BGM |
| [n8n](https://n8n.io) | 工作流自动化 |
| Reddit r/aivideo | 创作者实践 |
| CSDN / 抖音创作者分享 | 中国市场实践 |


<br><br>

---



<!-- FILE: 09-commercial-production-guide.md -->
# 商业广告短视频 AI 制作方案（落地版）

> 面向传媒/广告从业者 | 质量优先，成本不作为主要考量 | 2026.03

---

## 写在前面：工具选型的"反投毒"说明

**以下推荐基于独立盲测数据，非厂商营销。**

很多"AI 视频工具推荐"文章受厂商 SEO 和付费软文影响。本方案的工具推荐来自：
- [Artificial Analysis](https://artificialanalysis.ai) 盲测 Elo 排名（人类评审盲投票）
- [Video Arena](https://videoarena.tv) 双盲对比投票
- Reddit/知乎独立用户真实反馈（负面评价几乎不可能被赞助）

**独立盲测排名（2026.03）：**

| 排名 | 模型 | Elo | 来源 |
|------|------|-----|------|
| 1 | **Runway Gen-4.5** | 1247 | Artificial Analysis 盲测 |
| 2 | **Seedance 2.0** (即梦) | 1235 | 综合口碑（特别是角色一致性与物理规律） |
| 3 | Veo 3.1 | 1386 | SiliconFlow Arena (擅长写实与原生音频) |
| — | Kling 3.0 | 竞争力强但非 #1 | 营销暗示 #1，盲测不支持 |

> **Kling 3.0 的"4K/60fps"是其高端付费层功能，Reddit 用户反馈实际主要使用 1080p，且渲染经常失败或排队数小时。**

---

## 方案总览

### 定位

为**商业广告客户**制作高品质 AI 短视频（15-60 秒），包括：
- 产品广告片
- 品牌形象短片
- 社交媒体投放素材（抖音/小红书/微信视频号/TikTok/Instagram）
- 电商主图视频
- 活动预告/倒计时

### 核心工具链

```
策划         脚本          画面                  配音          字幕         配乐          剪辑          交付
 │            │            │                     │            │            │             │            │
Claude    Claude/GPT-4o   Runway Gen-4.5        ElevenLabs   CapCut      Musicbed     Premiere    多平台
 策略        结构化脚本    / Seedance 2.0 (即梦) 中英文       卡拉OK      商用授权      精修调色     自适应
 洞察        + Prompt      Veo 3.1 (写实/音频)    克隆声音     自动+人工   /Artlist      +特效       导出
             工程         (根据场景三选一)                    校对                     DaVinci
```

---

## 第 1 步：策划与创意（AI 辅助，人把控方向）

### 工具

| 用途 | 工具 | 说明 |
|------|------|------|
| 创意策略 | **Claude** | 分析品牌调性、目标受众、竞品视频，输出创意方向 |
| 竞品分析 | **Claude + Web Search** | 搜索同行业近期投放素材，总结什么风格有效 |
| 脚本大纲 | **Claude / GPT-4o** | 结构化输出（见 Prompt 模板） |

### 给 Claude 的策划 Prompt

```
你是一位资深广告创意总监，服务过快消、科技、美妆等行业的头部品牌。

客户信息：
- 品牌：{品牌名}
- 行业：{行业}
- 产品：{具体产品/服务}
- 目标受众：{年龄/性别/兴趣}
- 投放平台：{抖音/小红书/朋友圈/TikTok}
- 视频时长：{15s/30s/60s}
- 核心诉求：{提升品牌认知/促进转化/新品发布/活动宣传}

请输出：
1. 3 个不同风格的创意方向（各 2-3 句概述）
2. 推荐的视觉风格参考（描述画面调性、色彩、节奏）
3. 每个方向的 Hook（前 3 秒钩子）

格式：使用 Markdown，每个方向包含【创意主题】【视觉调性】【Hook】【场景概述】。
```

---

## 第 2 步：脚本撰写

### 工具

| 用途 | 工具 | 说明 |
|------|------|------|
| 脚本撰写 | **Claude / GPT-4o** | 结构化脚本（含镜头指示和画面描述） |
| 脚本打磨 | **人工审核** | 确认品牌调性、法律合规、事实准确 |

### 广告脚本 Prompt 模板

```
基于以下创意方向，写一个 {30} 秒的商业广告视频脚本。

创意方向：{第 1 步选定的方向}
品牌/产品：{品牌名} - {产品}
视觉风格：{电影感/高端简约/活力时尚/温暖治愈}

脚本要求：
1. 严格按照以下结构输出，包含精确到秒的时间码：
   [00:00-00:03] Hook — 画面描述 | 旁白文案 | 音效/配乐提示
   [00:03-00:08] Build — 同上
   [00:08-00:23] Body — 同上（可分多个子场景）
   [00:23-00:30] CTA — 同上

2. 每个场景包含：
   - 【镜头】：镜头类型（特写/中景/远景/航拍/推拉摇移）
   - 【画面】：详细的英文视觉描述（用于 AI 视频生成，60-80 words）
   - 【旁白】：中文旁白文案
   - 【音效】：配乐/音效提示
   - 【情感】：该场景的情感基调

3. 画面描述必须是英文，用电影化语言，包含：
   - 具体的视觉元素和构图
   - 光照方向和色温（如 "warm golden hour lighting"）
   - 镜头运动（如 "slow dolly forward"）
   - 景深和焦点（如 "shallow depth of field, focus on product"）

4. 全片需有一致的视觉语言和情绪弧线
```

### 脚本审核清单（人工）

- [ ] Hook 是否在 3 秒内制造足够好奇/冲击？
- [ ] 品牌/产品是否在前 5 秒内出现？
- [ ] 旁白是否自然口语化，避免书面腔？
- [ ] 画面描述是否足够详细，AI 能理解？
- [ ] CTA 是否清晰明确？
- [ ] 是否有法律风险（夸大宣传、未授权肖像等）？

---

## 第 3 步：AI 视频画面生成

**视觉大模型呈“三足鼎立”态势，商业制片不再依赖单一工具。请根据具体的脚本需求，选择最合适的模型。**

### 视频大模型横向对比与选型指南

| 维度 | Runway Gen-4.5 | Seedance 2.0 (即梦) | Veo 3.1 |
|------|----------------|---------------------|---------|
| **核心优势** | 视觉保真度极高、微观质感无敌 | 角色一致性（`@`系统）、动作迁移 | 极致写实人类动作、物理光影、原生音频 |
| **最佳场景** | 微距特写、流体/织物、氛围意境 | 剧情连贯、固定模特换装/转场 | 日常生活实拍感、带环境音效的镜头 |
| **控制方式** | Motion Brush、Director Mode | 垫图控制、`@`标签系统 | 强语义理解、基于物理引擎生成 |
| **首帧可用率** | ~73% (Image-to-Video可达85%) | ~90% (前5-8秒极高) | ~20% (需多次抽卡) |
| **隐患/缺点** | 强动作容易变形 | "10秒衰减定律"（10秒后易崩坏）| 抽卡成本高、偶有光影跳跃 |

### 主力工具 1：Runway Gen-4.5 (适用于氛围与质感表达)
**最佳实践：** 适合“抽象隐喻”、“微观世界”（如水波纹、琴弦崩断）和高端产品意境展示。
- **图生视频为主**：用 MidJourney/DALL-E 垫首帧图。
- **Motion Brush**：利用运动画笔精细控制局部运动。
- **Prompt结构**：`[镜头类型], [主体描述], [动作/运动], [环境/场景], [光照], [色调/氛围], [镜头运动]. [风格参考]`

### 主力工具 2：Seedance 2.0 / 即梦 (适用于角色连贯与复杂调度)
**最佳实践：** 具备“导演级”控制能力，是国内最成熟的商业级工具。
- **“10秒法则”**：将长镜头拆分为 **5-8秒** 的短片段拼接，避免 10 秒后的形态崩坏。
- **`@` 引用系统（杀手锏）**：上传模特照片标记为 `@Image1`，动作视频标记为 `@Video1`，实现极强的一致性（如：`@Image1 performs the motion from @Video1`）。
- **“导演制”提示词 6 元素**：`[主体], [动作], [运镜], [环境], [光影], [画质风格]`。
- **控制幅度**：在后台将动态幅度（Motion Strength）拉低至 30%-40%，微动效果更具电影感。

### 补充工具：Veo 3.1 (适用于写实剧情与原生声音)
**最佳实践：** 适合生成真实人脸细微表情、写实动作，以及需要环境声的镜头。
- **原生音频融合**：Prompt 结尾加入 `"with ambient café sounds, soft jazz music..."`，Veo 会同时生成视频与匹配音效。

### 订阅方案参考

| 工具 | 套餐 | 月费 | 说明 |
|------|------|------|------|
| **Runway** | Unlimited | $76/月 | 无限生成，Gen-4/4.5 全访问 |
| **即梦 (Seedance)** | 商业版 | ~￥399/月 | 满足高频商用导出，国内网络友好 |
| **Veo 3.1** | Google AI Ultra | $249.99/月 | 最高配额，4K 输出 |

### 画面生成工作流 (通用)

```
脚本每个场景（控制在 5-8 秒内）：
  │
  ├── Step A：MidJourney 生成首帧参考图（确保全片色彩/主角一致）
  │
  ├── Step B：选择模型进行 Image-to-Video
  │     ├─ 追求质感与微距 → Runway Gen-4.5
  │     ├─ 追求动作连贯/IP一致性 → Seedance 2.0 (即梦)
  │     └─ 追求极致写实/声音 → Veo 3.1
  │
  ├── Step C：应用提示词框架（如 Seedance 的 6 元素结构）
  │     生成 3-5 个候选（按需调低 Motion Strength 以增加稳定性）
  │
  └── 输出：选出最佳视频片段
```

---

## 第 4 步：配音

### 主力工具：ElevenLabs

**为什么选 ElevenLabs：**
- 英文 TTS 质量业内公认第一
- 中文支持可用（Multilingual v2 模型）
- 声音克隆：30 秒音频即可克隆声音，适合品牌固定代言人声线
- 情感控制精细
- 商用授权清晰

| 套餐 | 月费 | 字符数 | 说明 |
|------|------|--------|------|
| Creator | $22/月 | 100K 字符 | 中小项目 |
| Pro | $99/月 | 500K 字符 | 日常生产 |
| Scale | $330/月 | 2M 字符 | 大量需求 |

### 中文配音备选

| 场景 | 工具 | 说明 |
|------|------|------|
| 最佳中文自然度 | **Fish Audio** ($5.5/月) | 50+ 情感标记，多音字消歧 |
| 品牌声音克隆 | **ElevenLabs** / **CosyVoice**（开源） | 30s 音频克隆，150ms 延迟 |
| 预算型 | **Edge-TTS** `zh-CN-XiaoxiaoNeural` | 免费但无商业 SLA |

### 配音参数（广告片标准）

| 参数 | 商业广告推荐 | 说明 |
|------|------------|------|
| 语速 | **0.95-1.05x** | 略慢于日常语速，增加权威感和品质感 |
| 音调 | 根据品牌调性 | 高端品牌用偏低沉的声线；活力品牌用明亮声线 |
| 停顿 | 关键卖点后 **0.5-1.0 秒** | 留出消化时间 |
| 录制 | 分段录制 | 每个场景单独录，便于后期调整时间 |

---

## 第 5 步：字幕

### 广告片字幕规范

| 参数 | 推荐 | 说明 |
|------|------|------|
| 风格 | **品牌定制字体** 或 **无衬线粗体** | 与品牌 VI 一致 |
| 大小 | 屏幕宽度的 60-70% | 手机端清晰可读 |
| 位置 | 底部 1/4（避开平台 UI 元素） | 抖音底部有用户名/音乐信息 |
| 颜色 | 白色 + 半透明黑色描边/底板 | 保证在任何背景上可读 |
| 关键词高亮 | **品牌名/产品名/价格用品牌色高亮** | 引导视觉焦点 |
| 动画 | 逐字出现（卡拉 OK 式） | 2026 标配 |

### 工具

- **CapCut Pro / 剪映专业版**：自动生成 + 卡拉 OK + 品牌字体导入
- **Premiere Pro + MOGRT 模板**：最精细控制

---

## 第 6 步：配乐与音效

### 商用音乐授权（广告必须用正版）

| 平台 | URL | 月费 | 说明 |
|------|-----|------|------|
| **Artlist** | [artlist.io](https://artlist.io) | ~$16.60/月 | 全版权，无限下载，含音效 |
| **Musicbed** | [musicbed.com](https://musicbed.com) | 按项目授权 | 高端广告专用，独家曲库 |
| **Epidemic Sound** | [epidemicsound.com](https://epidemicsound.com) | $15/月 | 社交媒体商用，全球覆盖 |

**不要用免费 BGM 做商业广告** — 版权风险不值得省这点钱。

### 混音标准（广告片级）

| 音频层 | 音量 | 说明 |
|--------|------|------|
| 旁白 | **-10 至 -12 dBFS** | 主通道，必须水晶般清晰 |
| BGM（旁白段） | **-24 至 -30 dBFS** | 比旁白低 15-20 dB |
| BGM（无旁白段） | **-12 至 -16 dBFS** | 情绪过渡段可适当提高 |
| 音效 | **-14 至 -20 dBFS** | 点缀，不抢旁白 |
| 整体响度 | **-14 LUFS** | 社交媒体平台标准 |

### 音效使用要点

- **产品出场**：subtle whoosh + shimmer
- **标语/slogan**：短促 hit/impact
- **场景切换**：soft whoosh
- **价格/数字**：ding/pop
- **Logo 结尾**：品牌音效 sonic logo（如果有的话）

---

## 第 7 步：精修剪辑

### 工具

| 用途 | 工具 | 说明 |
|------|------|------|
| 主力剪辑 | **Premiere Pro** 或 **DaVinci Resolve** | 专业级控制 |
| 快速出片 | **CapCut Pro** | 适合社交平台短片 |
| 调色 | **DaVinci Resolve** | 业界标准调色工具，免费版即够用 |
| 特效/合成 | **After Effects** | Logo 动画、文字特效 |

### 广告片剪辑节奏

| 广告类型 | 剪辑节奏 | 每镜时长 |
|---------|---------|---------|
| 高端品牌 | 舒缓、优雅 | 3-6 秒 |
| 快消/促销 | 快节奏、密集信息 | 1-3 秒 |
| 科技产品 | 节奏递进，先慢后快 | 2-5 秒 |
| 美妆/时尚 | 中等偏快，细节特写多 | 1.5-4 秒 |

### 调色参考

| 品牌调性 | 色彩方向 | LUT 参考 |
|---------|---------|---------|
| 高端奢华 | 低饱和、金色/暗色调 | 类 Teal & Orange 变体 |
| 活力年轻 | 高饱和、明亮暖色 | 日系/韩系清新 |
| 科技专业 | 冷色调、蓝灰 | 科技蓝 |
| 温暖治愈 | 暖黄、柔光 | 柯达胶片感 |

---

## 第 8 步：多平台交付

### 导出规格

| 平台 | 画幅 | 分辨率 | 帧率 | 码率 | 编码 |
|------|------|--------|------|------|------|
| 抖音 | 9:16 | 1080×1920 | 30fps | 12-15 Mbps | H.264 |
| 小红书 | 9:16 或 3:4 | 1080×1920 或 1080×1440 | 30fps | 10-15 Mbps | H.264 |
| 微信视频号 | 9:16 | 1080×1920 | 30fps | 10 Mbps | H.264 |
| TikTok | 9:16 | 1080×1920 | 30fps | 12 Mbps | H.264 |
| Instagram Reels | 9:16 | 1080×1920 | 30fps | 10 Mbps | H.264 |
| YouTube Shorts | 9:16 | 1080×1920 | 30fps | 12 Mbps | H.264 |
| 横版备份 | 16:9 | 1920×1080 | 30fps | 15-20 Mbps | H.264 |

### 文案适配

每个平台的标题/话题/描述需要单独优化：

| 平台 | 标题策略 | 话题标签 |
|------|---------|---------|
| 抖音 | 痛点+解决方案，带互动引导 | #品牌名 #行业热词 #活动话题 |
| 小红书 | 种草体，带 emoji，像笔记 | 行业词 + 场景词 + 品牌词 |
| TikTok | 英文 hook，简洁直接 | 3-5 个相关 hashtags |

---

## 完整工作流清单

### 单条广告视频制作（~2 小时）

```
□ 1. 策划（15 分钟）
  □ Claude 分析客户 Brief，输出 3 个创意方向
  □ 与客户确认方向

□ 2. 脚本（20 分钟）
  □ Claude/GPT-4o 生成结构化脚本（含英文画面描述）
  □ 人工审核：钩子/品牌/合规/调性

□ 3. 画面生成（40 分钟）
  □ 每个场景：MidJourney 生成首帧参考图
  □ Runway Gen-4.5 Image-to-Video，每场景 2-3 个候选
  □ 选最佳候选
  □ 需要原生音效的场景用 Veo 3.1

□ 4. 配音（10 分钟）
  □ ElevenLabs 分段录制每个场景旁白
  □ 调整语速/停顿

□ 5. 粗剪（15 分钟）
  □ CapCut/Premiere 导入所有素材
  □ 对齐时间线
  □ 自动字幕 + 品牌字体/颜色
  □ BGM + 音效

□ 6. 精修（15 分钟）
  □ 调色（全片一致的色彩风格）
  □ 转场优化
  □ Logo/结尾画面
  □ 混音（旁白 -10dBFS，BGM -24dBFS）
  □ 手机端预览检查

□ 7. 交付（5 分钟）
  □ 按平台规格导出多版本
  □ 写各平台文案/标题/话题
```

### 月度投入预估

| 项目 | 月费 | 说明 |
|------|------|------|
| Runway / 即梦商业版 | ~$55-76 | 主力视频生成（根据需求二选一即可） |
| ElevenLabs Pro | $99 | 高品质配音 |
| MidJourney Standard | $30 | 首帧参考图 |
| Artlist | $17 | 商用音乐授权 |
| CapCut Pro | $20 | 剪辑+字幕 |
| Veo 3.1 按需 | ~$30-50 | 特殊写实/原生音频场景 |
| **合计** | **~$251-292/月** | |

**用这套工具链，一人可完成原本需要 4-5 人团队（编导+摄像+剪辑+调色+后期）的工作，且画面质量达到商业广告标准。**

---

## 品质保障要点

### 广告片 vs 日常短视频的差异

| 维度 | 日常短视频 | 商业广告 |
|------|----------|---------|
| 画面质量 | 够用就行 | **每一帧都要经得起审视** |
| 音频质量 | Edge-TTS 凑合 | **ElevenLabs + 正版 BGM** |
| 色彩一致性 | 不太在意 | **全片统一调色，匹配品牌 VI** |
| 字幕 | 自动生成即可 | **品牌定制字体 + 人工校对** |
| 版权 | 用免费素材 | **所有素材必须正版授权** |
| 审核流程 | 自己看一遍 | **至少过 2 轮：创作者 + 客户** |

### AI 生成内容的合规注意事项

1. **不要生成真人面部** — 避免肖像权纠纷（除非有授权或用 AI 头像）
2. **标注 AI 生成** — 部分平台/地区要求标注
3. **不要复制受版权保护的品牌/角色** — Seedance 2.0 的版权争议是前车之鉴
4. **产品画面用实拍** — AI 生成的产品特写可能有细节错误，产品本身用实拍更安全
5. **广告法合规** — AI 写的文案也要遵守广告法，避免"最"/"第一"等极限词

---

## 进阶：AI + 实拍混合工作流

对于最高品质的商业广告，推荐 AI + 实拍混合：

```
AI 负责（省时省钱）：          实拍负责（保证真实）：
├── 环境/场景建立镜头           ├── 产品特写
├── 氛围/意境画面               ├── 模特/代言人镜头
├── 转场/过渡画面               ├── 产品使用演示
├── 概念/想象力画面             └── 品牌 Logo 结尾
└── 背景/辅助视觉
```

**AI 做"画布"，实拍做"焦点"。** 这是目前最高品质、最高效率的商业广告制作方式。


<br><br>

---



<!-- FILE: 10-comprehensive-automated-workflow.md -->
# 10 — 全景解析：2026 AI 短视频自动化工作流体系与模型最佳实践

> **更新时间**：2026.03
> **文档定位**：综合性纲领文件。融合《07-工具链与工作流分析》、《08-最佳实践指南》、《09-商业广告 AI 落地指南》，以及最新的《智能减压枕头实战案例》。

---

## 摘要 (Executive Summary)

在 2026 年第一季度的“模型大爆发”之后，AI 短视频的生产范式已经从**“散件工具的来回切换”**演变为了**“三足鼎立的大模型基建 + 自动化 Agent 工作流”**。本指南旨在全景式地展示当前的最新生产力形态，帮助创作者和商业团队构建无需人工干预或仅需极少人工干预的高效管道。

---

## 一、 “三足鼎立”的视频大模型基建

在底层能力上，我们已经告别了单一片面的“文生视频”时代。目前的最高水准商业视频（如产品广告、微电影）必须根据具体场景，在以下三大模型中**“因地制宜”**：

### 1. Runway Gen-4.5 —— “质感与意境大师”
*   **绝对优势**：视觉保真度极高。极其擅长**微距摄影 (Macro shot)**、液体/粉末/织物等复杂的物理纹理，以及抽象隐喻。
*   **最佳工作流**：Midjourney 垫图 ➔ Runway 生成 ➔ Motion Brush (局部运动画笔) 细调。
*   **实战应用**：在“智能减压枕头”案例中，用于生成“琴弦崩断”和“流沙 50Hz 振动波纹”，带来极致的 ASMR 解压感。

### 2. Seedance 2.0 (即梦) —— “导演级调度与角色一致性”
*   **绝对优势**：首创的 `@` 引用系统和多模态输入（最多支持 12 个参考文件）。它能真正做到**“同一个模特在不同场景里做指定的动作”**，且首帧一致性高达 95%。
*   **核心法则**：**“10 秒衰减定律”**。必须将长镜头拆分为 5-8 秒的短片段拼接。在提示词上，严格遵循“导演制 6 元素”：`[主体], [动作], [运镜], [环境], [光影], [画质风格]`。
*   **实战应用**：适合“全系列产品宣传矩阵”，或需要同一个产品在极简卧室、自然环境等多个场景中保持形态不崩坏的连贯叙事。

### 3. Google Veo 3.1 —— “极致写实与原生音频”
*   **绝对优势**：人类真实面部微表情、逼真的物理光影、以及原生的“音画同步”。
*   **实战应用**：在“智能减压枕头”的写实版案例中，Veo 能完美表现“一个 35 岁高压职场精英躺下后，面部肌肉彻底松弛放松”的逼真过程，同时自带衣服摩擦、呼吸等环境音效。

---

## 二、 工作流管道的进化 (The Evolution of Pipelines)

传统的视频生产管道是串行的 6 个步骤（脚本 → TTS → 搜索画面 → 自动字幕 → 配乐 → 剪辑合成）。而在 2026 年，管道发生了两次重大“坍缩”和“升级”：

### 1. 模型的内部坍缩：原生音视频一体化
最新的 Kling 3.0、Seedance 2.0 和 Veo 3.1 已经原生吸收了 TTS（配音）和 BGM（配乐）。这意味着，通过高质量的结构化 Prompt，**AI 可以直接吐出一段带有完美环境音效、背景音乐甚至角色台词的成片片段**。这极大降低了剪辑软件里的混音成本。

### 2. 管道的外部升级：Agentic Workflow（智能体自动化）
目前最前沿的商业打法，不再是由人类运营逐个打开网页去复制粘贴。所有的操作都在**自动化工作流引擎**中静默完成。

---

## 三、 三大自动化工作流引擎 (The Automation Engines)

为了实现批量、高质的“无人值守”或“半自动对话式生产”，推荐以下三种自动化架构：

### 架构 A：Coze / Dify（低代码 Agent 流水线）—— 推荐给内容团队
这是目前性价比最高、也是落地最快的“全能短视频制作人”智能体模式。
*   **工作机制**：在 Coze 中编排一个多节点 Agent。
*   **节点流转**：
    1.  **用户输入**：一句简单的话，例如“做个卖智能枕头的 30 秒短视频”。
    2.  **LLM 拆解**：DeepSeek/GPT-4o 节点自动输出结构化脚本（包含 4 段英文画面描述）。
    3.  **并行调用**：通过官方 API 或聚合平台（如 PiAPI/ModelsLab），同时调用 Midjourney 生首帧图 ➔ 喂给 Seedance API 生成 4 段视频。
    4.  **TTS & 合成**：同时调用 ElevenLabs API 配音，最后由 Python 脚本节点或 FFmpeg 服务合成视频。
*   **交付形态**：在对话框里直接向用户返回一条完整的 MP4 视频链接。

### 架构 B：ComfyUI 节点网络（本地极客全自动）—— 推荐给视觉工作室
*   **适用群体**：拥有本地 24GB+ 显存（如 RTX 4090 / 5090）的高端工作室。
*   **工作机制**：将开源的最强视频大模型（如 LTX-2, Wan 2.2, HunyuanVideo）节点化。
*   **全自动链路**：`LLM 提示词节点` ➔ `SDXL/Flux 首帧生成节点` ➔ `视频生成大模型节点 (LTX-2)` ➔ `Upscaler 放大节点` ➔ `视频保存节点`。
*   **优势**：零 API 成本，绝对的数据安全，通过工作流可以直接出超清 4K 素材。

### 架构 C：n8n / Make.com / Zapier（中台与分发总枢纽）
*   **定位**：连接内容策划库（如 Notion / Airtable）和社交媒体分发终端。
*   **工作机制**：
    *   **触发器**：监听 Notion 里的“选题库”。当某个选题状态变为“Ready”时自动触发。
    *   **组装调度**：通过 HTTP Request 调用架构 A 的 Coze API 获取视频成品。
    *   **自动分发**：调用 TikTok、YouTube Shorts、Instagram Reels 的 API 进行自动发布。

---

## 四、 商业级落地质量把控（避坑指南）

无论是手动还是全自动，**“垃圾进，垃圾出 (GIGO)”** 的定律在 AI 视频中依然适用。以下是目前唯一有效的质量控制手段：

1.  **图生视频绝对至上 (Image-to-Video is King)**：不要试图用纯文字生成包含特定产品的连贯视频。**必须在工作流的第一步加入高质量的 AI 垫图（Midjourney/DALL-E 3）**。
2.  **控制 Motion 幅度**：在所有 API 调用或控制台中，将动态幅度参数控制在 30%-40%。越是商业大片，越强调用**“微小的光影变化”**（如灯光由冷蓝转为琥珀暖黄）来展现高级感，而不是剧烈的运镜。
3.  **批量生成 + 大浪淘沙**：目前业内最高模型（Runway）的首帧可用率约为 73%。要连续通过 6 个分镜头，一次成功的概率极低（约 15%）。**任何自动化工作流，必须设计“并行生成 3-5 个版本”的节点**，最终环节引入人工审批（Human-in-the-loop）挑选最佳。
4.  **3 秒定生死与卡拉 OK 字幕**：这是平台算法的核心标准。钩子必须在前 3 秒留人（视觉奇观或直击痛点），并且必须带有逐字高亮的字幕（提升 65% 的阅读完播率）。

---

## 五、 深度解析：长镜头生成与角色一致性保持策略 (Long-Take & Character Consistency)

2026 年，AI 视频的痛点已经从“单帧画质”转移到了**“长时间轴上的连贯性”**。生成超过 10 秒的长视频极易出现“身份漂移 (Identity Drift)”或背景融化。为了解决这一痛点，工业界目前沉淀了以下核心策略：

### 1. 角色一致性的“锚点”策略 (The Anchor Strategy)
如果你需要同一个主角贯穿全片，绝对不能仅凭文字描述（如“一个穿红衬衫的 30 岁男人”），AI 每次生成的脸都会不一样。
*   **多角度参考集 (Look Bible)**：在开机前，用 Midjourney 为主角生成一个包含 6-10 张高清照片的“参考集”（正面、侧面、3/4 侧面、各种情绪）。
*   **原生元素锁定**：使用 Seedance 2.0 独家的 `@` 标签系统或 Kling 3.0 的 `Elements` 功能，上传参考集作为 `@Actor1`。在后续的所有提示词中，只需写 `@Actor1 is walking`。
*   **面部动作捕捉 (Act-One)**：若对微表情要求极高，使用 Runway 的 **Act-One** 功能。你只需用电脑摄像头录制自己的表情表演，AI 会将这段表演的“灵魂” 1:1 映射到你设定的虚拟角色脸上，甚至能保持嘴型一致。

### 2. 突破“10秒定律”的帧接力法 (Recursive Extension)
目前所有大模型在 10 秒后的物理规律都会开始崩坏。要生成长达 1 分钟甚至更长的连续叙事或“一镜到底”，必须使用**接力法**：
*   **Step 1**：生成第一段优质视频（如 0-5 秒）。
*   **Step 2**：提取这 5 秒视频的**最后一帧 (Last Frame)** 保存为高清图片。
*   **Step 3**：将这张“尾帧”作为下一段视频（5-10 秒）的**首帧垫图 (First Frame Prompt)**，并配合顺延的运动提示词（如“摄影机继续向前推进”）。
*   **组装**：在剪映中将这几段视频紧密拼接，观众视觉上会认为这是一个不间断的完美长镜头。

### 3. 首尾帧插值法 (Keyframe Interpolation)
针对顶级模型（如 Google Veo 3.1）：
*   你可以同时上传“首帧图 (Start Frame)”和“尾帧图 (End Frame)”。
*   输入指令要求 AI 生成这中间的过渡过程。这种方式能强制 AI 锁定场景，确保环境从 A 演变到 B 时，不发生任何失控的形态突变（Morphing）。

### 4. 锁定环境光影与物理属性
*   **固定种子 (Fixed Seed)**：如果你对当前生成的光影满意但主角动作差一点，一定要锁定当前的 Seed 值进行重新抽卡。
*   **故事板模式 (Storyboard)**：利用 Sora 2 或 Kling 3.0 的全局故事板功能，让大模型“提前读取”接下来的分镜剧本，从而在多个独立镜头中保持相同的时间线、季节和光照条件。

---

## 结语

2026 年，AI 短视频的红利不再属于“比拼谁能写出更长的提示词”，而是属于**能用自动化 Agent 将最强垂类模型（Runway 的质感、Seedance 的连贯、Veo 的写实）丝滑串联起来的架构师**。从产品企划、自动化工作流调度，到最终分发，“降维打击”式的生产模式已经完全成型。

<br><br>

---



<!-- FILE: 10-ultimate-guide.md -->
# 10 — AI 短视频制作终极指南 (2026.03)

> 本指南整合了 4 轮独立调研 + 10 份文档审查的成果。所有工具推荐基于独立盲测数据（Artificial Analysis / Video Arena），而非厂商营销。
>
> 适用对象：个人创作者 / 内容团队 / 商业广告制作 / 技术开发者

---

## 目录

1. [30 秒速查：现在该用什么](#1-30-秒速查现在该用什么)
2. [完整工作流（4 套，按场景选）](#2-完整工作流)
3. [第 1 步：脚本生成](#3-脚本生成)
4. [第 2 步：AI 视频生成 + Prompt 工程](#4-ai-视频生成--prompt-工程)
5. [第 3 步：配音（TTS）](#5-配音tts)
6. [第 4 步：字幕](#6-字幕)
7. [第 5 步：配乐与音效](#7-配乐与音效)
8. [第 6 步：剪辑合成](#8-剪辑合成)
9. [第 7 步：质量检查](#9-质量检查)
10. [第 8 步：发布与数据反馈](#10-发布与数据反馈)
11. [自动化工作流引擎](#11-自动化工作流引擎)
12. [成本与 ROI 计算](#12-成本与-roi-计算)
13. [常见坑与避雷指南](#13-常见坑与避雷指南)

---

## 1. 30 秒速查：现在该用什么

### 视频生成模型选型（基于独立盲测，非营销）

| 场景 | 首选 | 备选 | 不推荐 |
|------|------|------|--------|
| **氛围/质感/微距** | Runway Gen-4.5（盲测 Elo #1） | — | — |
| **角色一致/剧情连贯** | Seedance 2.0（@系统） | Kling 3.0（Subject Ref） | — |
| **极致写实/带对话** | Veo 3.1（原生音频+物理引擎） | — | — |
| **性价比量产** | 即梦 Jimeng（国内最便宜） | Hailuo（$0.19/video） | — |
| **零成本** | Pexels + CLIP 语义排序 | Wan 2.2 本地（10GB GPU） | — |
| **开源本地 4K** | LTX-2（Apache 2.0, 12GB+） | Wan 2.2 5B（MIT, 10GB+） | — |

### 按预算速查

| 月预算 | 脚本 | 视频 | 配音 | 字幕 | 配乐 | 剪辑 |
|--------|------|------|------|------|------|------|
| **$0** | DeepSeek | Pexels+CLIP | Edge-TTS | CapCut 自动 | Pixabay Music | CapCut |
| **~$30** | GPT-4o-mini | 即梦免费层 | Fish Audio | CapCut | Uppbeat | CapCut |
| **~$100** | Claude | Runway Std $28 | ElevenLabs $22 | CapCut Pro $20 | Artlist $17 | CapCut Pro |
| **~$300** | Claude | Runway $76 + Veo | ElevenLabs $99 | CapCut Pro | Artlist | Premiere |
| **自部署** | Ollama 本地 | Wan 2.2 / LTX-2 | CosyVoice / IndexTTS-2 | Whisper | 本地库 | FFmpeg |

---

## 2. 完整工作流

### 工作流 A：一人工作室（15 分钟/条，$0-1）

最成熟的个人创作者工作流。

```
① DeepSeek 写脚本 (Hook-Build-Body-CTA)
     ↓
② Edge-TTS 配音（zh-CN-XiaoxiaoNeural）
     ↓
③ Pexels 搜索素材 + CLIP 余弦排序（或即梦/Kling 免费层生成）
     ↓
④ CapCut 导入 → 自动卡拉 OK 字幕 → BGM（Pixabay）→ 音效
     ↓
⑤ 人工快审（3 秒钩子？字幕对？画面匹配？）
     ↓
⑥ 导出 9:16 → 发布
```

### 工作流 B：AI 原生视频（管道坍缩，~$1-3/条）

2026.02 之后的新范式 — AI 模型一次生成视频+音频+对话。

```
① LLM 写结构化脚本（含镜头、动作、对话、音效提示）
     ↓
② MidJourney 生成首帧参考图（锁定视觉风格）
     ↓
③ Runway/Seedance/Veo Image-to-Video（每场景 5-8 秒，2-3 候选选最佳）
     ↓
④ Whisper 转录 → CapCut 卡拉 OK 字幕
     ↓
⑤ Premiere/DaVinci 精修（调色+转场+Logo）
     ↓
⑥ 质量检查 → 多平台导出 → 发布
```

### 工作流 C：Agentic 自动化（Coze/Dify 智能体）

对话式生产 — 输入一句话，Agent 跑完全流程。

```
Coze/Dify 智能体配置：
  ├── 意图识别节点：分析输入主题
  ├── LLM 节点：DeepSeek 生成 5 个分镜 Prompt
  ├── 并行 API 节点：
  │   ├── SiliconFlow → Wan 2.2 视频生成
  │   ├── 或 Runway/Seedance API → 视频生成
  │   └── ElevenLabs/Fish Audio → TTS
  ├── 代码节点：FFmpeg 合成 + 字幕
  └── 输出节点：MP4 下载链接

用户输入："帮我做一个智能枕头广告"
Agent 自动输出：成片 MP4
```

**搭建步骤（Dify + SiliconFlow）：**
1. 注册 [SiliconCloud](https://siliconflow.cn)，获取 API Key
2. 在 Dify 插件市场安装 SiliconFlow 插件
3. 创建 Workflow，添加 SiliconFlow Video Generate 节点
4. 配置模型 `Wan-AI/Wan2.2-I2V-A14B`，设置 prompt 和 image 输入
5. 连接 End 节点输出视频 URL

### 工作流 D：ComfyUI 本地管道（极客/工作室）

全本地化，不依赖云 API，需 24GB+ GPU。

```
ComfyUI 节点流：
  Load Image → Upscale → LTX-2 Video Node → Audio Generation → Concat → Export MP4
```

- NVIDIA GDC 2026 发布 ComfyUI App View + LTX-2.3 NVFP4 优化
- Wan 2.2 和 LTX-2 均有 ComfyUI 自定义节点
- 适合需要完全控制、离线运行的团队

---

## 3. 脚本生成

### LLM 选择

| 场景 | 推荐 | 理由 |
|------|------|------|
| 中文短视频 | **豆包 / DeepSeek** | 中文语感最好 |
| 英文短视频 | **GPT-4o / Claude** | 创意写作强 |
| 零成本 | **DeepSeek** | 免费额度 |
| 批量 | **GPT-4o-mini** | 便宜快速 |

### 脚本公式：Hook-Build-Body-CTA

| 部分 | 60s | 30s | 作用 |
|------|-----|-----|------|
| **Hook** | 0-3s | 0-2s | 抓注意力（前 3 秒定生死） |
| **Build** | 3-15s | 2-8s | 建语境 |
| **Body** | 15-45s | 8-22s | 交付核心价值 |
| **CTA** | 45-60s | 22-30s | 引导行动 |

### 6 种 Hook 写法

| 类型 | 示例 | 适合 |
|------|------|------|
| 反常识 | "99% 的人不知道..." | 知识科普 |
| 提问 | "你有没有想过..." | 教育 |
| 痛点 | "还在为 X 发愁？" | 实用技巧 |
| 结果前置 | "最终效果是这样的——" | 教程/变身 |
| 强声明 | "这一个习惯彻底改变了我" | 个人成长 |
| 动态开场 | （直接动态画面，不要静态图） | 所有类型 |

### Prompt 模板

```
你是专业短视频编剧。请为以下主题写一个 {30/60} 秒脚本：
主题：{topic}
平台：{抖音/TikTok/YouTube Shorts}
风格：{知识科普/叙事/教程/评测}

要求：
1. Hook(0-3s) + Build + Body + CTA 四段式
2. Hook 使用{反常识/提问/痛点}手法
3. 每场景标注 [镜头描述]（英文，60-80 words）
4. 控制在 {150-200} 字

输出格式：
[00:00-00:03] Hook：旁白 | [镜头描述] | 音效提示
[00:03-00:10] Build：旁白 | [镜头描述] | 音效提示
...
```

---

## 4. AI 视频生成 + Prompt 工程

### 核心原则：Image-to-Video > Text-to-Video

**首帧图片引导法**是当前最佳实践：
1. 用 MidJourney/DALL-E 生成一张首帧参考图
2. 上传到 Runway/Seedance/Veo 做 Image-to-Video
3. 成功率从 ~60-73% 提升到 **~85-90%**

### 平台特定 Prompt 结构

#### Runway Gen-4.5

```
[镜头类型], [主体], [动作], [环境], [光照], [色调], [镜头运动]. [风格参考].

示例：
Close-up shot, a woman's hand placing a luxury bottle on marble, warm golden
hour lighting, shallow depth of field with bokeh, slow dolly-in. Cinematic
commercial, anamorphic lens flare.
```

**规则：**
- ❌ 不支持 negative prompt（只描述你想要的）
- ❌ 不要重复描述首帧图片已有的内容
- ✅ Image-to-Video 时只描述运动和镜头变化
- ✅ 一个 prompt 一个镜头，不要塞多个场景

#### Seedance 2.0（即梦）

```
主体 + 动作 + 场景 + 光线 + 镜头 + 风格 + 画质 + 约束

示例：
@图片1 作为首帧，一位女性缓缓转身面向镜头，五官清晰无变形，面部稳定，
柔和逆光，浅景深虚化背景，缓慢推进镜头，日系治愈风格，4K超高清细节丰富，
无模糊无残影画面稳定
```

**杀手锏 — @ 引用系统：**
- `@图片1 作为首帧` — 锁定首帧
- `@图片2 作为角色参考` — 角色一致性
- `@视频1 参考镜头语言` — 复制运动风格
- 最多 12 个参考文件

**关键参数：**
- 动态幅度拉低到 30-40%（微动更有电影感）
- 每段控制在 **5-8 秒**（10 秒后易崩坏 — "10 秒衰减定律"）
- 稳定性关键词：五官清晰、面部稳定、无变形、角色一致、服装一致

#### Veo 3.1

```
[镜头] [主体] in [场景], [动作], [光照], [运动]. 对话: "台词". 音频: [音效描述].
No subtitles, no text overlay.

示例：
Interior cafe, late afternoon. Medium two-shot at window table.
One line of dialogue from Person A: 'Are you ready?'
Camera: gentle dolly-in. Ambient: clinking cups, soft chatter.
No subtitles, no text overlay.
```

**Veo 独特能力：**
- 原生对话生成（prompt 末尾加对话文本）
- 三层音频：环境音 + 音效 + 音乐
- ✅ 必须加 "No subtitles, no text overlay"（否则自动加字幕）
- 镜头语言权重最高（prompt 开头放镜头描述）

### 跨平台速查

| 要素 | Runway | Seedance | Veo |
|------|--------|----------|-----|
| 语言 | 英文 | 中文优先 | 英文 |
| Negative prompt | ❌ | 约束词 | "No..." 有效 |
| 原生音频 | ❌ | ✅ | ✅ |
| 最长 | 60s (Gen-4) | 5-12s | ~8s |
| 首帧引导 | ✅（最佳实践） | ✅（@系统） | ✅ |
| Prompt 优先级 | 镜头类型在前 | 主体+动作在前 | 镜头在前+风格在前 |

---

## 5. 配音（TTS）

### 工具矩阵

| 工具 | 质量 | 中文 | 英文 | 成本 | 声音克隆 |
|------|------|------|------|------|---------|
| **Edge-TTS** | 7/10 | ✅ 晓晓/云希 | ✅ Jenny | $0 | ❌ |
| **Fish Audio** | 9/10 | ✅ 50+情感标记 | ✅ | $5.5/月 | ✅ |
| **ElevenLabs** | 9.5/10 | ⚠️ 可用 | ✅ 最佳 | $22-330/月 | ✅ 30s 音频 |
| **IndexTTS-2** | 9/10 | ✅ 最佳自然度 | — | 免费自部署 | ✅ |
| **CosyVoice** | 9/10 | ✅ 18 方言 | ✅ | 免费自部署 | ✅ 跨语言 |

### 配音参数

| 内容类型 | 语速 | 音调 | 停顿 |
|---------|------|------|------|
| 知识科普 | 1.0-1.1x | 默认 | 关键点后 0.3-0.5s |
| 娱乐/快节奏 | 1.15-1.25x | 略高 +5% | 最小化 |
| 商业广告 | 0.95-1.05x | 根据品牌调性 | 卖点后 0.5-1.0s |

### Edge-TTS 快速使用

```bash
pip install edge-tts
edge-tts --text "你好世界" --voice zh-CN-XiaoxiaoNeural --rate "+10%" -o output.mp3
```

⚠️ Edge-TTS 使用逆向工程微软 API，**无官方 SLA**，不适合商业关键业务。

---

## 6. 字幕

### 2026 标配：逐字卡拉 OK 高亮

| 参数 | 推荐值 |
|------|--------|
| 字体 | 无衬线粗体（思源黑体/Montserrat） |
| 每行 | 中文 8-12 字，英文 3-5 词 |
| 行数 | 最多 2 行 |
| 位置 | 屏幕中下 1/3（避开平台 UI） |
| 高亮色 | 黄色（与文字色强对比） |
| 时间 | 比语音**提前 0.1-0.2s** 出现 |
| 动画 | 逐字出现（卡拉 OK 式） |

### CapCut 字幕流程

```
导入视频+音频 → 文本 > 自动字幕 → 选卡拉 OK 样式 → 自定义字体/颜色 → 检查修正 → 导出
```

---

## 7. 配乐与音效

### 混音音量标准

| 音频层 | 音量 (dBFS) |
|--------|------------|
| 旁白/对话 | **-10 至 -12** |
| BGM（有旁白时） | **-24 至 -30**（比旁白低 15-20dB） |
| BGM（无旁白段） | **-12 至 -16** |
| 音效 | **-14 至 -20** |
| 整体响度 | **-14 LUFS** |

### 免费音乐来源

| 来源 | URL | 说明 |
|------|-----|------|
| YouTube Audio Library | YouTube Studio 内置 | YouTube Shorts 安全 |
| Pixabay Music | [pixabay.com/music](https://pixabay.com/music) | 完全免费 |
| 爱给网 | [aigei.com](https://aigei.com) | 中文最全免费音效+BGM |
| Fesliyan Studios | [fesliyanstudios.com](https://fesliyanstudios.com) | 有"对话背景音乐"分类 |
| Uppbeat | [uppbeat.io](https://uppbeat.io) | 创作者免费层 |

### 商用授权（广告必须正版）

| 平台 | 月费 | 说明 |
|------|------|------|
| **Artlist** | ~$17/月 | 全版权，无限下载，含音效 |
| **Epidemic Sound** | ~$15/月 | 社交媒体商用 |
| **Musicbed** | 按项目 | 高端广告 |

### 必备音效清单

| 类型 | 用途 | 获取 |
|------|------|------|
| Whoosh | 场景切换 | Pixabay / 爱给网 |
| Riser | 制造期待 | Pixabay / 爱给网 |
| Hit/Impact | 重点强调 | Pixabay / 爱给网 |
| Pop/Ding | 文字出现 | Pixabay / 爱给网 |

---

## 8. 剪辑合成

### 画幅规格

| 平台 | 画幅 | 分辨率 |
|------|------|--------|
| 抖音/TikTok/Shorts/Reels | 9:16 竖屏 | 1080×1920 |
| B 站 | 16:9 或 9:16 | 1920×1080 |
| YouTube 长视频 | 16:9 横屏 | 1920×1080 |

**核心原则：从一开始就按 9:16 竖版制作，不要从横版裁切。**

### 剪辑节奏

| 类型 | 每镜时长 |
|------|---------|
| 快节奏/娱乐 | 0.5-2s |
| 教程/展示 | 2-5s |
| 高端品牌广告 | 3-6s |

### 转场

| 类型 | 使用频率 |
|------|---------|
| 直接切 | 80%+ |
| 交叉溶解 | 10% |
| 滑动/推移 | 5% |
| 匹配剪辑 | 5% |

**2026 趋势：干净极简。花哨特效转场已过时。**

---

## 9. 质量检查

**这是全行业最大的空白 — 没有任何主流工具提供自动质量检查。以下是可用的方法：**

### 人工快审清单（60 秒内完成）

| # | 检查项 | 合格标准 |
|---|--------|---------|
| 1 | 前 3 秒钩子 | 有足够吸引力，不想划走 |
| 2 | 画面-脚本匹配 | 画面内容与旁白语义一致 |
| 3 | 字幕准确 | 无错字、时间同步 |
| 4 | 音量平衡 | 旁白清晰，BGM 不抢 |
| 5 | 画质 | 无明显模糊/伪影/闪烁 |
| 6 | 手机预览 | 在手机上字幕清晰、画面填满 |

### 自动化质量检测工具

| 工具 | 用途 | 安装 | 类型 |
|------|------|------|------|
| **VMAF** (Netflix) | 编码质量 vs 原始 | `ffmpeg`（内置 libvmaf） | 有参考 |
| **DNSMOS** (Microsoft) | 语音/音频质量 | `pip install torchmetrics[audio]` | 无参考 |
| **SyncNet** | 唇形同步检测 | `pip install syncnet-python` | 无参考 |
| **VBench** | AI 视频 16 维度评估 | `pip install vbench` | 无参考 |

### VMAF 快速使用

```bash
# 比较编码后 vs 原始（需要两个视频）
ffmpeg -i encoded.mp4 -i original.mp4 \
  -filter_complex libvmaf=model_path=vmaf_v0.6.1.json:log_path=log.json:log_fmt=json \
  -f null -
```

| 分数 | 质量 |
|------|------|
| 95+ | 过度（浪费带宽） |
| 84-92 | 好（UGC 目标） |
| 70-84 | 一般（可接受） |
| <70 | 差（不可接受） |

### DNSMOS 音频质量

```python
import torch
from torchmetrics.functional.audio import dnsmos
scores = dnsmos(preds=audio_tensor, fs=16000)
# 返回 [P808_MOS, MOS_SIG, MOS_BAK, MOS_OVR]
# 目标：MOS_OVR >= 3.5（可接受），>= 4.0（生产级）
```

### A/V 同步标准

| 偏移 | 感知 |
|------|------|
| ±20ms | 不可感知 |
| ±45ms | 训练有素的观众可察觉 |
| ±80ms+ | 明显干扰 |

---

## 10. 发布与数据反馈

### 最佳发布时间

| 平台 | 最佳时段 | 次优 |
|------|---------|------|
| 抖音 | 18:00-22:00 | 7:30-8:30, 12:00-13:00 |
| TikTok | 10-11 AM EST 周二-四 | 7-9 PM |
| YouTube Shorts | 2-4 PM EST | 8-10 PM |

### 多平台导出规格

| 平台 | 分辨率 | 帧率 | 码率 | 编码 |
|------|--------|------|------|------|
| 抖音 | 1080×1920 | 30fps | 12-15 Mbps | H.264 |
| 小红书 | 1080×1920 或 1080×1440 | 30fps | 10-15 Mbps | H.264 |
| TikTok | 1080×1920 | 30fps | 12 Mbps | H.264 |
| YouTube Shorts | 1080×1920 | 30fps | 12 Mbps | H.264 |

### 抖音 SEO（2025 算法更新后）

推荐引擎升级为"兴趣图谱 + 场景匹配"双引擎：
- **关键词布局**：标题 + 字幕 + 话题标签 + 评论区
- **关键词结构**：痛点 + 解决方案（如"零基础健身跟练"）
- **评论区 SEO**：评论关键词影响搜索排名 → 设计互动引导

### A/B 测试方法

**单变量法则：每次只改一个元素。**

| 优先级 | 测试项 | 衡量指标 |
|--------|--------|---------|
| 1 | Hook（前 3 秒） | 3 秒留存率 > 30% |
| 2 | 视频时长（15s/30s/60s） | 完播率 > 40% |
| 3 | 封面/缩略图 | 点击率 |
| 4 | CTA 措辞和位置 | 转化率 |

**测试协议：**
- 同一天上传两个版本
- 每个版本积累 1000+ 播放后再比较
- TikTok 看 48-72 小时数据，YouTube Shorts 看 1-2 周

### 发布后关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 3 秒留存率 | Hook 有效性 | > 30% |
| 平均观看时长 | 内容吸引力 | > 50% 视频时长 |
| 完播率 | 整体质量信号 | > 40% (30s 以下) |
| 互动率 | 点赞+评论+分享/播放 | > 5% (TikTok) |
| 分享率 | 病毒性信号 | 越高越好 |

### 分析工具

| 工具 | 用途 | 成本 |
|------|------|------|
| 平台原生分析 | 自己账号数据 | 免费 |
| **Virlo** | AI 趋势发现 + 竞品分析 | 中等 |
| **Exolyt** | TikTok 实时趋势 | 中等 |
| **Brand24** | 情感分析 + 提及监控 | 入门 |

---

## 11. 自动化工作流引擎

### 三层架构

```
第 1 层：视觉控制（本地 GPU）
  └── ComfyUI — 节点式本地管道，接 Wan 2.2 / LTX-2

第 2 层：智能体编排（低代码）
  └── Coze / Dify — LLM 驱动的全自动流水线

第 3 层：企业集成（触发器+分发）
  └── n8n / Make — 监听 Notion → 触发生成 → 自动发布
```

### Coze（扣子）智能体搭建

```
1. 创建 Bot → 添加 Workflow 节点
2. Start 节点：用户输入主题
3. LLM 节点：DeepSeek 解析需求 → 输出分镜 JSON
4. Plugin 节点：调用 Runway/Seedance/SiliconFlow API → 视频
5. Plugin 节点：调用 TTS API → 配音
6. Code 节点：FFmpeg 合成
7. End 节点：返回 MP4 下载链接
```

### Dify + SiliconFlow 视频生成

```
1. 注册 SiliconCloud → 获取 API Key
2. Dify 插件市场安装 SiliconFlow 插件
3. 创建 Workflow → 添加 SiliconFlow Video Generate 节点
4. 配置模型：Wan-AI/Wan2.2-I2V-A14B
5. 设置 prompt + image 输入 + video_size (1280x720)
6. End 节点输出视频 URL
```

### n8n 多平台分发

```
Notion 数据库状态变更 → n8n Webhook 触发
  → 调用 Coze Agent API → 获取成片
  → 下载 MP4
  → 并行发布：
    ├── TikTok API
    ├── YouTube Shorts API
    └── Instagram Reels API
```

### Pixelle-Video：全开源一键出片（阿里 AIDC-AI）

**GitHub:** [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) | 许可证: Apache 2.0

输入主题 → 自动脚本 → AI 图片/视频 → TTS 旁白 → BGM → 合成出片。

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video
# 配置 LLM 后端（GPT/DeepSeek/Ollama/通义千问）
# 配置图像生成模型
# 运行：输入主题字符串，系统自动跑通全流程
```

支持：自定义素材上传、动作迁移、数字人口播、多语言 TTS、image-to-video。

### MCP Server：让 Claude/Cursor 直接生成视频

| MCP Server | 能力 | 安装 |
|------------|------|------|
| **Kling AI MCP** | 13+ 工具：文生视频、图生视频、特效、唇形同步 | [GitHub](https://github.com/chuanky/kling-ai-mcp-server) |
| **Remotion MCP** | React 编程式视频创作，3D/字幕/动画 | [remotion.dev](https://remotion.dev) |
| **Remotion Video Gen** | Claude 直接创建和渲染视频 | [MCP Market](https://mcpmarket.com) |

```json
// Claude Desktop MCP 配置示例（Kling AI）
{
  "mcpServers": {
    "kling-ai": {
      "command": "node",
      "args": ["path/to/kling-mcp/index.js"],
      "env": { "KLING_ACCESS_KEY": "...", "KLING_SECRET_KEY": "..." }
    }
  }
}
```

### ComfyUI Wan 2.2 具体配置

**模型文件：**
```
models/diffusion_models/
  └── wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors  (Image-to-Video 14B)
models/clip/ 或 models/text_encoders/
  └── umt5_xxl_fp8_e4m3fn_scaled.safetensors
models/vae/
  └── wan2.2_vae.safetensors
models/loras/
  └── wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors  (加速 LoRA)
```

**必装自定义节点：** ComfyUI-GGUF, ComfyUI-KJNodes, ComfyUI-VideoHelperSuite, ComfyUI-mxToolkit, ComfyUI-Frame-Interpolation, ComfyUI-wanBlockswap, ComfyUI-MagCache

**参数：** Steps 15-30, Guidance Scale 6, 分辨率 720p

### 中国市场批量工具

| 工具 | 定位 | 优势 |
|------|------|------|
| **红鸦AI** | 小红书矩阵批量图文 | 20 条/天，全套风格一致 |
| **豆包** | 抖音优化脚本+视频 | 理解"黄金 3 秒"规则 |
| **即梦** | 低成本视频生成 | CapCut 深度集成 |
| **Pixelle-Video** | 全开源全自动出片 | Apache 2.0，可商用 |

---

## 12. 成本与 ROI 计算

### 单条视频成本对比（30s，6 片段）

| 方案 | 生成成本 | 配音 | 字幕 | 配乐 | 合计 |
|------|---------|------|------|------|------|
| **Pexels+Edge-TTS** | $0 | $0 | $0 | $0 | **$0** |
| **即梦免费层** | $0 | $0 | $0 | $0 | **$0** |
| **Runway Std** | ~$3.00 | $0.01 | $0 | $0 | **~$3** |
| **Runway+候选筛选(N=2)** | ~$6.00 | $0.01 | $0 | $0 | **~$6** |
| **传统拍摄** | $500-2000 | $50-200 | $20-50 | $30-100 | **$600-2350** |

### 月度 ROI（以自动化频道为例）

```
假设：每天 2 条，每条广告收入 $5-20
月产量：60 条
月工具成本：~$100（Runway Std + ElevenLabs + CapCut）
月收入：$300-1200
ROI：200-1100%
```

---

## 13. 常见坑与避雷指南

### ❌ 不要做的事

| 坑 | 说明 |
|----|------|
| 用横版裁切做竖版 | 画面信息丢失严重，永远不会好看 |
| 静态图开场 | 前 3 秒必须有动态 |
| 把 prompt 当作文写 | AI 视频模型需要具体物理描述，不是抽象概念 |
| 信 Kling "4K/60fps" 营销 | Reddit 用户反馈实际常用 1080p，渲染常失败 |
| 用免费 BGM 做商业广告 | 版权风险不值得 |
| Seedance 片段超过 10 秒 | "10 秒衰减定律"——10 秒后角色/场景易崩坏 |
| 依赖单一 AI 视频工具 | 混合使用 2-3 个工具，按场景选最合适的 |

### ✅ 关键法则

| 法则 | 说明 |
|------|------|
| **高频 > 极致** | 频繁发布合格内容 > 偶尔发布完美内容 |
| **3 秒定生死** | 前 3 秒决定一切，投入 50% 精力在 Hook |
| **手机测试** | 所有内容必须在手机上预览 |
| **音频 > 画面** | 73% 爆款靠音画协调（来源：行业实践共识） |
| **结构化 > 随意** | 固定结构 = 稳定质量 = 可自动化 |
| **Image-to-Video > Text-to-Video** | 首帧图片引导成功率从 60% 提升到 85%+ |
| **5-8 秒片段拼接** | 超过 10 秒的单镜头易崩坏，拆分为短片段 |

---

## 附录：数据来源与可信度

| 来源 | 类型 | 可信度 |
|------|------|--------|
| [Artificial Analysis](https://artificialanalysis.ai) | 独立盲测 Elo | ★★★★★ |
| [Video Arena](https://videoarena.tv) | 双盲人类投票 | ★★★★☆ |
| Reddit r/aivideo | 独立用户反馈 | ★★★★☆（负面评价几乎不可能被赞助） |
| 知乎/CSDN | 中文用户反馈 | ★★★☆☆（部分软文） |
| GitHub Stars/Issues | 开源项目真实数据 | ★★★★★ |
| 厂商官方文档 | 产品规格 | ★★★☆☆（可能夸大） |
| YouTube 对比视频 | 视觉对比 | ★★☆☆☆（多为付费/联盟） |
| 36kr/TechCrunch | 行业分析 | ★★★☆☆ |


<br><br>

---



<!-- FILE: 11-one-click-best-practices.md -->
# 11 — 一键出片最佳实践：工具、技巧与工作流 (2026.03.14)

> 基于 GitHub 项目分析（10 个活跃项目）+ YouTube/Bilibili 创作者实战教程深度调研。
> 只收录 2026 年 1-3 月仍在活跃维护的项目和被真实创作者验证过的工作流。

---

## 核心发现

> **没有人只用一个工具。** 最佳实践是混合使用 5-7 个专用工具，按场景选最强的那个。
>
> 2026 年 3 月真正的一键出片不是"一个按钮出成片"，而是**一条自动化管道串联多个最强工具**。

---

## 一、开源一键出片项目排名（2026.03 活跃度验证）

| # | 项目 | Stars | 最后提交 | 画面来源 | 许可证 | 定位 |
|---|------|-------|---------|---------|--------|------|
| 1 | **[Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video)** | 3.1k | 2026-02-04 (push 03-08) | **AI 生成**（FLUX+Wan 2.1） | Apache 2.0 | 最完整一键出片 |
| 2 | **[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)** | 50.2k | 2025-12-14 ⚠️ | Pexels 素材库 | MIT | 社区最大，开发放缓 |
| 3 | **[NarratoAI](https://github.com/linyqh/NarratoAI)** | 8.3k | **2026-03-10** ✅ | 用户上传视频 | 非商用 | 视频解说/混剪 |
| 4 | **[KrillinAI](https://github.com/krillinai/KrillinAI)** | 9.7k | 2026-02-08 | 原视频翻译 | GPL-3.0 | 视频翻译/配音 |
| 5 | **[Wan 2.1](https://github.com/Wan-Video/Wan2.1)** | 15.6k | **2026-03-05** ✅ | AI 生成 | Apache 2.0 | 最强开源视频模型 |
| 6 | **[LTX-Video](https://github.com/Lightricks/LTX-Video)** | 9.6k | 2026-01-05 | AI 生成 | Apache 2.0 | 最快开源模型+4K |
| 7 | **[SkyReels-V2](https://github.com/SkyworkAI/SkyReels-V2)** | 6.6k | 2026-01-29 | AI 生成 | Custom | 无限长度视频 |
| 8 | **[HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo)** | 11.8k | 2025-11-21 | AI 生成 | Custom | 高质量但重 |

### 关键判断

- **MoneyPrinterTurbo 开发已放缓**（3 个月无更新），但仍可用
- **Pixelle-Video 是当前最佳一键出片方案** — AI 生成画面（非素材库）+ Apache 2.0 + Windows 一键安装
- **NarratoAI 最活跃**但做的是解说/混剪，不是从零生成
- **Wan 2.1 是底层引擎之王** — VBench 超越 Sora（86.22% vs 84.28%），1.3B 版本仅需 8GB 显存

---

## 二、真实创作者的 4 种工作流模式

### 模式 1："The Frankenstein"（专业创作者主流）

> **混合 5-7 个工具，每个场景选最强的那个。** 这是 YouTube 上百万粉创作者的实际做法。

```
① Claude / GPT-4o → 脚本（结构化 JSON 分镜）
② Flux 2 / MidJourney → 首帧关键图（锁定视觉风格）
③ 按场景选模型生成视频：
   ├── 微距/质感/氛围 → Runway Gen-4.5（Motion Sketch 精细控制）
   ├── 角色连贯/剧情 → Seedance 2.0（@ 引用系统）
   ├── 写实/对话/唇形同步 → Veo 3.1（原生音频）
   └── 动作/运动/物理 → Kling 2.6/3.0（Motion Control）
④ ElevenLabs → 配音（或用 Veo 原生对话）
⑤ CapCut / Premiere → 剪辑+字幕+调色
⑥ Suno / Artlist → 配乐
```

**关键技巧：**
- **Image-to-Video 永远优于 Text-to-Video** — 先生成首帧图再动画化，成功率从 ~60% 升到 ~85%+
- **Kling "Leap-Frog" 无限延长法** — 提取最后一帧 → 放大 → 作为下一段 I2V 的首帧 → 无限长度
- **Veo "音频卫生"** — prompt 加 "no background music"，先获取干净对话+唇形同步，配乐后期加
- **每段控制在 5-8 秒** — 超过 10 秒角色/场景易崩坏

### 模式 2："The Factory"（量产工作流）

> **n8n/Make 自动化管道，一人日产 10+条。**

```
Google Sheet 内容队列
  → n8n Schedule Trigger
  → ChatGPT/Claude → 脚本 JSON
  → PiAPI(Flux) → 首帧图
  → PiAPI(Kling) → Image-to-Video
  → ElevenLabs → 配音
  → Creatomate → 视频模板渲染
  → OpenAI → 字幕生成
  → Blotato/upload-post → 自动发布到 5 个平台
  → Discord Webhook → 通知
```

**关键工具：**
| 节点 | 工具 | 作用 |
|------|------|------|
| 触发 | n8n Schedule | 定时/手动触发 |
| 脚本 | OpenAI/Claude 节点 | JSON 分镜 |
| 图像 | PiAPI (Flux 2) | 首帧生成 |
| 视频 | PiAPI (Kling) | I2V 动画 |
| 配音 | ElevenLabs 节点 | TTS |
| 渲染 | Creatomate | 模板合成 |
| 发布 | Blotato 社区节点 | 多平台 |

**设置步骤：**
1. `npx n8n` 或 Docker 安装 n8n
2. 安装社区节点：`n8n-nodes-blotato`
3. 注册 Creatomate → 设计视频模板 → 记录 Template ID
4. 导入 n8n 模板 JSON（n8n.io/workflows 有现成模板）
5. 填入所有 API Key → 连接 Google Sheet → 开跑

### 模式 3："The Aggregator"（省事但有效）

> **用一个聚合平台同时调用多个模型，选最好的。**

**[Higgsfield AI](https://higgsfield.ai)** — 2026 年的专业创作者首选聚合平台：
- 集成 15+ 模型（Sora 2, Kling 2.6, Veo 3.1, FLUX.2 等）
- **Cinema Studio 2.0**：模拟真实摄影机机身（ARRI, RED, Sony）和镜头特性（35mm, 50mm, 85mm）
- **Character ID / Soul ID**：跨无限生成锁定角色面部+个性+体态+服装
- **Shots 工具**：同一 prompt 自动生成多机位镜头
- 同一 prompt → 同时跑 Sora + Veo + Kling → 挑最好的（就是我们说的 Route B）

### 模式 4："The Local Studio"（本地全开源）

> **ComfyUI + 开源模型，不依赖任何云 API。需 RTX 4090。**

```
ComfyUI 节点流：
  ├── FLUX 2 → 首帧图生成
  ├── Wan 2.1 14B → Image-to-Video（高质量）
  │   或 LTX-2 → Image-to-Video（快速迭代）
  ├── Frame Interpolation → 补帧到 60fps
  ├── NVFP4 量化 → 60% 显存节省
  ├── RTX Video Super Resolution → 一键 4K 放大
  └── Export → MP4/WebM/ProRes
```

**2026.03 ComfyUI 更新要点：**
- NVIDIA RTX Video Super Resolution 节点 — 一键 4K 放大
- NVFP4/FP8 量化 — 2.5x 性能提升，60% 显存节省
- App View — 简化界面（底层仍是节点图）
- LTX-2.3 优化版本可用

**开源全自动：Pixelle-Video**
```bash
git clone https://github.com/AIDC-AI/Pixelle-Video
# 配置 LLM（GPT/DeepSeek/Ollama/通义千问）
# 配置图像模型（FLUX/Qwen）+ 视频模型（Wan 2.1）
# 输入主题 → 自动：脚本→图片→视频→配音→BGM→合成
# Windows 一键安装包可用
```

---

## 三、突破性技巧（YouTube 调研，文章里找不到的）

### 1. Kling "Leap-Frog" 无限长度法

```
生成 5s 视频 → 提取最后一帧 → Topaz 放大 → 作为下一段 I2V 首帧 → 再生成 5s → 循环
```

可以生成任意长度的连续镜头，角色和场景保持一致。

### 2. Veo 3.1 "音频卫生"

```
Prompt: "...No background music. Only natural ambient sounds and dialogue."
```

先获取干净的对话+唇形同步，配乐在后期 Premiere/DaVinci 中加。混合效果远优于 Veo 自动配乐。

### 3. Runway Motion Sketch

在静态图片上直接**画运动轨迹**（箭头、路径、形状），AI 按你画的方向运动。不需要复杂的 prompt 描述运动——直接画出来。

### 4. Higgsfield "Soul ID"

不只是锁定面部（Character ID），还锁定**个性**——体态语言、表情习惯、穿衣风格都跨生成保持一致。其他工具的 "character consistency" 只锁脸，这个锁全身。

### 5. Seedance 多模态同时输入

**唯一**支持 图片+视频+音频+文本 四路同时输入的模型。例如：
```
@Image1（角色照片）+ @Video1（参考动作视频）+ @Audio1（背景音乐）+ 文字描述
```

### 6. 首尾帧接力法（连续镜头标配）

```
场景 1 → 提取最后 1 帧 → 作为场景 2 的首帧 → 生成场景 2 → 提取最后 1 帧 → ...
```

所有工具都应该用这个方法做连续镜头。在 Kling 叫 "Leap-Frog"，在 Seedance 叫 "首尾帧接力"。

---

## 四、按需求选工具

| 我要... | 用这个 | 为什么 |
|---------|--------|--------|
| **零成本一键出片** | Pixelle-Video + Ollama | 全开源，Apache 2.0 |
| **零成本素材库出片** | MoneyPrinterTurbo | 50k stars，最大社区 |
| **视频解说/混剪** | NarratoAI | 最活跃（2026.03.10），VLM 场景分析 |
| **视频翻译/配音** | KrillinAI | 100+ 语言，声音克隆 |
| **量产自动化** | n8n + PiAPI + Creatomate | 日产 10+ 条，自动发布 |
| **最高画质商业广告** | Higgsfield + Runway + Veo | 聚合 15+ 模型 |
| **本地全开源 4K** | ComfyUI + Wan 2.1 + LTX-2 | RTX 4090 跑全流程 |
| **中国市场矩阵** | Coze + 即梦 + CapCut | 深度平台集成 |
| **无限长度视频** | SkyReels-V2 | 自回归架构，无长度限制 |

---

## 五、工具活跃度监控（截至 2026-03-14）

| 项目 | 最后提交 | 趋势 | 建议 |
|------|---------|------|------|
| Wan 2.1 | 2026-03-05 ✅ | 活跃 | 推荐作为底层引擎 |
| NarratoAI | 2026-03-10 ✅ | 非常活跃 | 解说类首选 |
| KrillinAI | 2026-02-08 ✅ | 活跃 | 翻译类首选 |
| Pixelle-Video | 2026-02-04 ✅ | 活跃 | 一键出片首选 |
| SkyReels-V2 | 2026-01-29 ✅ | 活跃 | 长视频关注 |
| LTX-Video | 2026-01-05 ✅ | 活跃 | 速度王 |
| MoneyPrinterTurbo | 2025-12-14 ⚠️ | 放缓 | 仍可用但关注后续 |
| HunyuanVideo | 2025-11-21 ⚠️ | 放缓 | 质量好但更新慢 |

---

## 附录：数据来源

| 来源 | 类型 |
|------|------|
| GitHub API 直接查询（stars, commits, dates） | 一手数据 |
| YouTube 创作者教程（2026.02-03） | 实战验证 |
| Reddit r/aivideo | 独立用户反馈 |
| n8n.io/workflows | 自动化模板 |
| Higgsfield AI 官方文档 | 功能确认 |
| ComfyUI 社区 + NVIDIA GDC 2026 | 技术更新 |
| Bilibili AI 视频教程 | 中国市场实践 |


<br><br>

---



<!-- FILE: 11-the-ultimate-ai-video-handbook.md -->
# 2026 AI 短视频工业化生产全书 (The Ultimate AI Video Handbook)

> **版本**：2026.03 最终版
> **定位**：这是一本面向内容创作者、商业团队与技术极客的“实用先行”红宝书。从宏观的行业格局，到微观的开源工具选型，再到保姆级的自动化工作流 SOP，本文档融汇了 AI 视频领域的所有核心知识。

---

## 目录
1. [第一卷：顶层视觉大模型格局 (The Landscape)](#第一卷顶层视觉大模型格局-the-landscape)
2. [第二卷：自动化工作流与高价值开源引擎 (Automation & Repos)](#第二卷自动化工作流与高价值开源引擎-automation--repos)
3. [第三卷：MoneyPrinterTurbo 升级版 —— 结合 Seedance 的全自动 SOP](#第三卷moneyprinterturbo-升级版--结合-seedance-的全自动-sop)
4. [第四卷：商业制片标准流程与参数 (Best Practices)](#第四卷商业制片标准流程与参数-best-practices)
5. [第五卷：高级进阶：长镜头与角色一致性 (Advanced Techniques)](#第五卷高级进阶长镜头与角色一致性-advanced-techniques)
6. [第六卷：实战拆解：智能减压枕头广告投流大片](#第六卷实战拆解智能减压枕头广告投流大片)

---

## 第一卷：顶层视觉大模型格局 (The Landscape)

2026 年初，AI 视频行业发生了“大坍缩”：顶级模型不仅能生成 4K 画面，还原生集成了配音（TTS）和音效（SFX）。目前行业呈**“三足鼎立”**态势：

1. **Runway Gen-4.5（质感与意境大师）**
   - **特点**：视觉保真度目前行业第一，微距摄影、流体、物理纹理无敌。
   - **绝招**：Motion Brush（局部运动画笔）精细控流。
   - **痛点**：强动作容易变形，不支持原生音频。

2. **Seedance 2.0 / 即梦（调度与连贯王者）**
   - **特点**：国内最成熟的商业级工具。
   - **绝招**：`@` 标签引用系统（角色一致性）和最多 12 个参考文件的多模态输入。
   - **痛点**：“10秒定律”——超过 10 秒易崩坏，需通过短镜头拼接。

3. **Google Veo 3.1（写实与原生音频专家）**
   - **特点**：写实人脸微表情、逼真的环境光影。
   - **绝招**：完美的音画同步（如输入“咖啡倒入杯中的声音”）。
   - **痛点**：配额严格，首帧可用率低（约 20%），需高频抽卡。

**一句话总结**：如果你拍的是微观产品/意识流大片，选 **Runway**；如果你拍的是剧情连贯/固定模特的广告，选 **Seedance**；如果你拍的是需要环境音的写实生活流，选 **Veo**。

---

## 第二卷：自动化工作流与高价值开源引擎 (Automation & Repos)

### 1. MoneyPrinterTurbo (MPT) 是最佳实践吗？
*   **结论**：MPT（55k+ Stars）是**“入门级低成本起号”**的最佳实践，但**不是“高质量商业转化”**的最佳实践。
*   **痛点**：MPT 默认依赖 Pexels 的免费素材（由于关键词匹配极差，经常出现“图文不符”），且它只做缝合，不具备 AI 视频的生成能力。在 2026 年，仅靠混剪无版权素材已经很难获取自然流量。

### 2. 除了 MPT，还有哪些高价值的自动化 Repo？
为了实现真正的“Agentic Workflow（智能体流水线）”，目前 GitHub 和社区跑通的顶级方案有：

*   **[Short Video Maker (gyoridavid) / MCP 协议]**
    *   **定位**：极速自动化的现代版 MPT。
    *   **亮点**：基于最新模型上下文协议 (MCP)，可以被 Claude 或 n8n 直接当作 API 随时调用。集成 Kokoro TTS 和 Remotion 渲染，极客首选。
*   **[AI-Faceless-Video-Generator (SamurAIGPT)]**
    *   **定位**：数字人/解说类视频自动发电机。
    *   **亮点**：内置 SadTalker，可以全自动生成脚本 ➔ 语音 ➔ 并且让一张静态图片“开口说话”完成唇形同步，非常适合科普、历史、新闻类账号。
*   **[Wan 2.6 + n8n 工作流]**
    *   **定位**：高画质本地化全闭环。
    *   **亮点**：阿里开源的 Wan 模型（10GB 显存可跑 720p）。通过 n8n 触发 `GPT-4o 脚本 ➔ 本地 Wan GPU 节点生视频 ➔ FFmpeg 合成`，是目前能替代 Runway 的最高质量免费开源方案。
*   **ComfyUI (节点化基建)**
    *   **定位**：高阶视觉工作室的终极武器。
    *   **亮点**：将 LTX-2 或 HunyuanVideo 以节点形式接入。实现从“Midjourney 生图 ➔ 局部重绘 ➔ 视频生成 ➔ Topaz 放大”的全链路本地自动化，数据绝对安全。

---

## 第三卷：MoneyPrinterTurbo 升级版 —— 结合 Seedance 的全自动 SOP

既然 MPT 原版的 Pexels 画面太粗糙，我们如何将其改造为**“调用 Seedance 2.0 生成独家商业级画面”**的高级工作流？

建议放弃 MPT 臃肿的底层代码，直接使用 **Coze/Dify + 聚合 API（如 PiAPI）** 搭建现代版智能体流。以下是标准操作程序 (SOP)：

### SOP：构建“Seedance + 自动化”的高转化工作流
1. **基建搭建**：
   - 登录 Coze 或 Dify，创建一个名为“高奢短视频发电机”的 Agent。
2. **编排 LLM 节点（剧本与提示词工程）**：
   - 输入：`{用户主题}`
   - 提示词设定：让 LLM 输出 5 个短镜头的 **Seedance 6元素提示词** `[主体], [动作], [运镜], [环境], [光影], [画质风格]`。
3. **编排视频生成节点（Seedance API）**：
   - 接入火山引擎的 Seedance API（或第三方中转 API）。
   - 将 LLM 输出的 5 个提示词，作为并发请求发送给 Seedance 进行“文生视频”。
   - *(进阶：为了角色一致性，在此节点中固定传入一张产品的首帧图作为参考图。)*
4. **编排配音节点（TTS API）**：
   - 将 LLM 生成的旁白，发送给 ElevenLabs 或 Fish Audio API，获取 `voice.mp3`。
5. **代码节点（合并合成）**：
   - 编写一段 Python 脚本（利用 `moviepy` 或 FFmpeg）。
   - 按顺序拼接 Seedance 返回的 5 个 MP4，叠加 `voice.mp3`，自动居中添加卡拉 OK 样式的字幕，压低旁白时的背景音乐。
6. **最终输出**：Agent 直接在对话框回复成品视频的下载链接，或通过 n8n 节点自动分发至 TikTok/小红书。

---

## 第四卷：商业制片标准流程与参数 (Best Practices)

如果你采用手动或半自动精修，必须死守以下行业“公理”：

1. **3秒钩子 (Hook)**：
   - 短视频前 3 秒定生死。绝对不要用静态图开场。必须用反常识、直击痛点或剧烈动态（如东西掉落、瞬间变色）作为第一帧。
2. **卡拉 OK 逐字高亮字幕**：
   - **硬性指标**：必须配有逐字变色/放大的字幕，这能提升 65% 的完播率。使用无衬线粗体，置于屏幕中下部。
3. **音频比画面重要**：
   - 商业级配音：推荐使用 ElevenLabs (英文) 或 Fish Audio (中文)。
   - 混音标准：旁白 (`-10dBFS`)，带旁白的 BGM (`-24dBFS`，压低以突出人声)，音效 (`-15dBFS`)。
4. **全竖版制作**：
   - 永远以 `9:16` (1080x1920) 原生尺寸进行视频生成和剪辑。从横版裁切是最低级的做法。

---

## 第五卷：高级进阶：长镜头与角色一致性 (Advanced Techniques)

2026 年，解决 AI 视频“形态崩坏（身份漂移）”的两大核心技术：

### 1. “锚点”法则 (The Anchor Strategy)
绝对不要用自然语言（如“一个短发女孩”）去控制主角，必须锁定视觉锚点：
- **Seedance 做法**：上传 6 张人物多角度参考图到 `@` 标签库，命名为 `@Actor1`。在提示词中写 `@Actor1 正在喝水`，脸部一致性高达 95%。
- **Runway 做法**：使用 **Act-One** 功能，上传人物图后，用你自己的电脑摄像头演一段表情，AI 会 1:1 把你的神态精准克隆到人物脸上。

### 2. 突破“10秒崩坏定律”：首尾帧接力 (Recursive Extension)
- **原理**：大模型生成超过 10 秒必糊。
- **解法**：生成 0-5 秒的 A 片段 ➔ 提取 A 的**最后一帧**截图 ➔ 用这张截图作为垫图，生成 5-10 秒的 B 片段（提示词写“继续向前推运镜”）。
- **效果**：在剪辑软件里把 A 和 B 拼起来，就是一场视觉连贯、物理形态不崩的“一镜到底”。

---

## 第六卷：实战拆解：智能减压枕头广告投流大片

> **背景**：某硬件项目（VCM 体感 1-50Hz 振动枕头）。产品不主打医疗，而是面向“高压精英”提供“沉浸式减压舱”般的物理爽感体验。预算充分，要求极高画质。

### 阶段一：策划与降维打击（使用 LLM）
不讲“拯救失眠”，只讲“极致解压”。
- **创意 Hook**：使用“一根紧绷快断裂的琴弦”隐喻高压的大脑。
- **视觉定调**：电影感、冷蓝光向温暖琥珀色过渡、极其丝滑的慢动作。

### 阶段二：分镜生成（Runway/Seedance 图生视频）
放弃文生视频，全流程采用 **Midjourney 生图 ➔ Runway Gen-4.5 动效**：
1. **[0-5s 痛点]** `特写：一根在冷蓝光下紧绷颤抖的粗弦`。（Runway 运动笔刷：高频微动）
2. **[5-10s 瓦解]** `弦突然崩断，陷入极度柔软的深灰色记忆棉，光线变暖黄`。（绝佳的解压 ASMR 画面）
3. **[10-15s 爽感]** `深色流体沙滩荡起完美的 50Hz 物理同心波纹`。（隐喻 VCM 振动穿透肌肉）
4. **[15-20s 产品]** `极其高级的产品展示定格，左侧留白`。（用于后期添加品牌字幕）

### 阶段三：听觉注入（ElevenLabs）
- **人声**：生成极致低沉、具有磁性的男低音。语速放慢 0.9x。配音词：“触碰它的瞬间，一切开始瓦解”。
- **音效**：加入沉闷的 `Bass Drop`（重低音轰鸣）和舒缓的白噪音脉冲声。

### 阶段四：合成与转化（CapCut / PR）
将画面与极品音效对齐，当那句“一切开始瓦解”话音刚落，重低音砸下的瞬间，紧绷的绳子断裂。加上极简的白色高级字幕，导出多平台发布。

---
> **总结**：AI 视频的护城河不再是“魔法咒语”，而是**工程化的流水线**。善用自动化中台（n8n/Coze），锁定一致性技术（首尾接力、@标签），再结合高审美的策划策略，即可在这个时代实现高质量的商业变现与降维打击。

<br><br>

---

