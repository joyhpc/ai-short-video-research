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
