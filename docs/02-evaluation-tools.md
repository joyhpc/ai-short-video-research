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
