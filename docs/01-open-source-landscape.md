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
