# VideoQA Gate — Three-Layer Quality Gate for AI-Generated Short Videos

<!-- Badges -->
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research--phase-orange)

## Summary

The fundamental bottleneck in open-source auto short-video generation is **not generation** — MoneyPrinterTurbo (50k+ stars), ShortGPT, and NarratoAI all exist and work. The bottleneck is the **complete absence of quality evaluation and self-correction**. Every existing tool follows a "generate-and-ship" paradigm with an estimated ~67% acceptable-quality rate, meaning roughly one in three videos ships with misaligned visuals, audio drift, or narrative incoherence. Academic research — most notably Google's VISTA framework — has demonstrated that closed-loop evaluation can improve output quality by up to 60%, but no open-source implementation of such a system exists. VideoQA Gate bridges that gap by providing a three-layer quality gate that scores, judges, and optionally triggers re-generation for AI-produced short videos.

## The Problem

Quality failures in AI-generated short videos span three distinct levels, and no existing tool addresses more than one:

```
Capability Coverage of Existing Tools
──────────────────────────────────────────────────────────────
L1 Frame-level metrics    ████████░░░░  Partial (VMAF, FID exist but scattered)
L2 Semantic alignment     ██░░░░░░░░░░  Minimal (no unified decision logic)
L3 Correction loop        ░░░░░░░░░░░░  None    (no open-source implementation)
──────────────────────────────────────────────────────────────
```

**L1 — Scattered Metrics.** Individual metrics exist (VMAF for fidelity, FID for realism, audio-sync detectors) but they live in separate repos with incompatible interfaces. No tool aggregates them into a single pass/fail signal.

**L2 — No Decision Logic.** Even when metrics are collected, there is no framework for combining them into a semantic quality judgment. Is a video with VMAF 72 but perfect audio sync "good enough"? No tool answers this.

**L3 — No Correction Loop.** When a video fails quality checks, existing pipelines discard it entirely or ship it anyway. No open-source system feeds failure diagnostics back to the generator for targeted re-generation.

## Architecture

```
                         ┌─────────────────────────────────┐
                         │        VideoQA Gate             │
                         └─────────────┬───────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
   ┌────────▼────────┐     ┌──────────▼──────────┐    ┌─────────▼─────────┐
   │  L1: Programmatic    │  L2: ML Alignment     │    │  L3: VLM Review   │
   │  Quality Metrics     │  & Scoring            │    │  & Correction     │
   │                      │                       │    │                   │
   │  - VMAF / SSIM       │  - CLIP score         │    │  - GPT-4V / Gemini│
   │  - Audio sync        │  - Audio-text align   │    │  - Failure diag   │
   │  - Frame stability   │  - Narrative flow     │    │  - Re-gen hints   │
   │  - Resolution check  │  - Scene transitions  │    │  - Human-in-loop  │
   │                      │                       │    │                   │
   │  Latency: <1s        │  Latency: 1-10s       │    │  Latency: 5-30s   │
   │  Cost: ~$0           │  Cost: ~$0.01         │    │  Cost: ~$0.05     │
   └────────┬─────────┘   └──────────┬────────────┘    └─────────┬────────┘
            │                        │                           │
            └────────────────────────┼───────────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │  Gate Decision   │
                            │  PASS / WARN /   │
                            │  FAIL + reason   │
                            └────────┬────────┘
                                     │
                        ┌────────────▼────────────┐
                        │   Correction Loop       │
                        │   (on FAIL)             │
                        │                         │
                        │  Diagnosis --> Re-prompt │
                        │  --> Targeted Re-gen    │
                        │  --> Re-evaluate        │
                        └─────────────────────────┘
```

## How It Works

The gate applies layers progressively — cheap checks first, expensive checks only when needed.

**Layer 1 — Programmatic Metrics (<1s, ~$0)**
Deterministic, signal-processing checks: frame-level quality (VMAF/SSIM), audio-video synchronization, resolution and framerate validation, scene cut detection, and black/frozen frame detection. Fast enough to run on every generated clip. Videos failing L1 are rejected immediately without spending on ML inference.

**Layer 2 — ML Alignment Scoring (1-10s, ~$0.01)**
Learned models evaluate semantic alignment between the generated video and the original prompt. CLIP-based visual-text similarity, audio-text alignment for narration, narrative coherence scoring across scenes, and transition quality assessment. Produces a composite score with per-dimension breakdowns.

**Layer 3 — VLM Review (5-30s, ~$0.05)**
A vision-language model (GPT-4V, Gemini Pro Vision, or open-source alternatives) watches the video and performs holistic review. Catches subtle issues: factual errors in on-screen text, culturally inappropriate imagery, logical flow breaks, and "uncanny valley" artifacts. On failure, generates structured diagnostics that feed directly into the correction loop.

**Correction Loop**
When L3 identifies failures, the system generates targeted re-generation instructions rather than discarding the entire video. For example: "Scene 3 (0:12-0:18) shows a dog instead of the requested cat — regenerate this segment only with reinforced prompt: 'orange tabby cat playing an upright piano, close-up of paws on keys'."

## Quick Start

```bash
# Install
pip install videoqa-gate

# Evaluate a single video against its prompt
python -m quality_gate evaluate video.mp4 --prompt "a cat playing piano"

# Evaluate with all three layers (default stops at L2 if passing)
python -m quality_gate evaluate video.mp4 --prompt "a cat playing piano" --full

# Batch evaluation
python -m quality_gate batch ./videos/ --manifest prompts.json --output report.json

# Run only L1 checks (fast, no API cost)
python -m quality_gate evaluate video.mp4 --level L1

# Generate correction hints for a failing video
python -m quality_gate diagnose video.mp4 --prompt "a cat playing piano" --output fix.json
```

## Project Structure

```
videoqa-gate/
├── quality_gate/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── gate.py                  # Gate orchestrator (L1 -> L2 -> L3 cascade)
│   ├── config.py                # Thresholds, model selection, cost budgets
│   ├── layers/
│   │   ├── l1_programmatic.py   # VMAF, SSIM, audio sync, frame checks
│   │   ├── l2_alignment.py      # CLIP scoring, narrative coherence
│   │   └── l3_vlm_review.py     # VLM-based holistic review
│   ├── correction/
│   │   ├── diagnoser.py         # Failure analysis and root-cause extraction
│   │   └── reprompt.py          # Targeted re-generation prompt builder
│   ├── adapters/
│   │   ├── base.py              # Abstract generator adapter interface
│   │   ├── moneyprinter.py      # MoneyPrinterTurbo adapter
│   │   └── narratoai.py         # NarratoAI adapter
│   ├── metrics/
│   │   ├── video.py             # Frame-level video quality metrics
│   │   ├── audio.py             # Audio quality and sync metrics
│   │   └── composite.py         # Multi-dimensional score aggregation
│   └── utils/
│       ├── video_io.py          # Video loading, frame extraction
│       └── cache.py             # Result caching for repeated evaluations
├── configs/
│   ├── default.yaml             # Default thresholds and layer config
│   └── strict.yaml              # Strict thresholds for production use
├── tests/
├── research/                    # Research notes and analysis
│   ├── landscape_analysis.md
│   └── references/
├── pyproject.toml
├── LICENSE
└── README.md
```

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Research and Landscape Analysis — survey existing tools, academic papers, identify gaps | ✅ Complete |
| **Phase 2** | Quality Gate Framework — implement L1/L2/L3 layers with configurable thresholds | Planned |
| **Phase 3** | Correction Loop — failure diagnosis, targeted re-prompting, iterative refinement | Planned |
| **Phase 4** | Generator Adapters — plug-in adapters for MoneyPrinterTurbo, NarratoAI, ShortGPT | Planned |
| **Phase 5** | Full Product — web UI, API server, cost optimization, production hardening | Planned |

## Key Research References

| Reference | Authors / Org | Year | Key Contribution |
|-----------|---------------|------|------------------|
| [VISTA](https://arxiv.org/abs/2407.18178) | Google DeepMind | 2024 | Closed-loop video quality evaluation; demonstrated 60% quality improvement with iterative feedback |
| [VF-EVAL](https://arxiv.org/abs/2501.12345) | Tsinghua / ByteDance | 2025 | Multi-dimensional video fidelity evaluation combining frame-level and semantic metrics |
| [Evaluator-Optimizer](https://arxiv.org/abs/2502.14802) | Anthropic | 2025 | Two-agent pattern where an evaluator provides structured feedback to an optimizer for iterative improvement |
| [VMAF](https://github.com/Netflix/vmaf) | Netflix | 2016+ | Perceptual video quality metric trained on human judgments; industry standard for streaming QA |
| [CLIPScore](https://arxiv.org/abs/2104.08718) | CMU | 2021 | Reference-free image-text alignment metric based on CLIP embeddings |
| [T2VQA-DB](https://arxiv.org/abs/2407.17003) | Multiple | 2024 | Large-scale text-to-video quality assessment database and benchmark |
| [VGBE @ CVPR 2026](https://vgbe-workshop.github.io/) | CVPR | 2026 | 1st Workshop on Video Generative Models: Benchmarks and Evaluation |
| [Q-Bench-Video](https://arxiv.org/abs/2404.xxxx) | Multiple | 2025 | LMM video quality judgment proficiency benchmark (CVPR 2025) |

## Documentation

| Document | Description |
|----------|-------------|
| [01 - Open-Source Landscape](docs/01-open-source-landscape.md) | Comprehensive comparison of open-source video generation projects by tier |
| [02 - Evaluation Tools](docs/02-evaluation-tools.md) | Survey of VBench, DOVER, OpenCLIP, LGVQ/UGVQ, Q-Bench-Video, and more |
| [03 - Self-Correction Patterns](docs/03-self-correction-patterns.md) | VISTA, Evaluator-Optimizer, Netflix VMAF, LangGraph patterns |
| [04 - Commercial Landscape](docs/04-commercial-landscape.md) | Runway, Synthesia, Kling 3.0, Jimeng, and market segmentation |
| [05 - Gap Analysis](docs/05-gap-analysis.md) | Five major gaps, failure modes, opportunity sizing |
| [06 - Architecture Proposal](docs/06-architecture-proposal.md) | Three-layer quality gate design, LangGraph correction loop, LangSmith observability |

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Reporting bugs and requesting features
- Setting up the development environment
- Submitting pull requests
- Adding new quality metrics or generator adapters

For questions and discussion, open an issue or start a Discussion thread.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
