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
