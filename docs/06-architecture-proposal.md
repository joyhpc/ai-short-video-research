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
|                                    Runway / Kling     MoviePy]    |
|                                    / Sora / local                 |
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

## Cross-References

- Evaluation tools used in the quality gate: [02-evaluation-tools.md](02-evaluation-tools.md)
- Self-correction patterns that inform the correction loop: [03-self-correction-patterns.md](03-self-correction-patterns.md)
- Gap analysis this architecture addresses: [05-gap-analysis.md](05-gap-analysis.md)
- Open-source landscape this builds on: [01-open-source-landscape.md](01-open-source-landscape.md)
- Commercial benchmarks to compare against: [04-commercial-landscape.md](04-commercial-landscape.md)
