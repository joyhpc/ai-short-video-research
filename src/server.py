"""VideoQA REST API — FastAPI server for video generation and evaluation."""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Job storage (in-memory for simplicity)
_jobs: dict[str, dict[str, Any]] = {}


def create_app():
    """Create and configure the FastAPI application."""
    try:
        from fastapi import FastAPI, HTTPException, BackgroundTasks
        from fastapi.responses import FileResponse, JSONResponse
        from pydantic import BaseModel
    except ImportError:
        raise RuntimeError(
            "FastAPI is not installed. Install with: pip install 'videoqa-gate[web]'"
        )

    app = FastAPI(
        title="VideoQA API",
        description="AI Short Video Generator + Quality Gate System",
        version="0.1.0",
    )

    class GenerateRequest(BaseModel):
        topic: str
        duration: float = 60.0
        style: str = "informative"
        language: str = "zh"
        voice: str = "zh-CN-XiaoxiaoNeural"
        tts_provider: str = "edge-tts"
        llm_provider: str | None = None
        skip_eval: bool = False

    class EvaluateRequest(BaseModel):
        video_path: str
        prompt: str = ""
        layers: list[int] = [1, 2]

    class JobResponse(BaseModel):
        job_id: str
        status: str
        message: str = ""

    def _run_generate(job_id: str, req: GenerateRequest):
        """Background task for video generation."""
        try:
            _jobs[job_id]["status"] = "running"
            _jobs[job_id]["progress"] = "Generating script..."

            from src.pipeline.generators.script import ScriptGenerator
            from src.pipeline.generators.tts import TTSGenerator
            from src.pipeline.generators.subtitles import SubtitleGenerator

            output_dir = Path(f"./output/{job_id}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Script
            script_gen = ScriptGenerator(provider=req.llm_provider)
            script = script_gen.generate(
                topic=req.topic, duration=req.duration,
                style=req.style, language=req.language,
            )
            script_path = output_dir / "script.json"
            with open(script_path, "w", encoding="utf-8") as f:
                json.dump(script.to_dict(), f, ensure_ascii=False, indent=2)

            _jobs[job_id]["progress"] = "Generating narration..."
            _jobs[job_id]["script"] = script.to_dict()

            # TTS
            tts = TTSGenerator(default_provider=req.tts_provider, default_voice=req.voice)
            narration = "\n".join(s.narration for s in script.scenes)
            audio_path = str(output_dir / "narration.mp3")
            audio_clip = tts.generate(narration, output_path=audio_path)

            _jobs[job_id]["progress"] = "Generating subtitles..."

            # Subtitles
            sub_gen = SubtitleGenerator()
            srt_path = str(output_dir / "subtitles.srt")
            sub_gen.generate(audio_path, output_path=srt_path)

            _jobs[job_id]["progress"] = "Complete"
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["result"] = {
                "output_dir": str(output_dir),
                "script_path": str(script_path),
                "audio_path": audio_path,
                "srt_path": srt_path,
                "audio_duration": audio_clip.duration,
                "num_scenes": len(script.scenes),
            }

        except Exception as e:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = str(e)
            logger.exception("Job %s failed", job_id)

    @app.post("/api/generate", response_model=JobResponse)
    async def generate(req: GenerateRequest, bg: BackgroundTasks):
        """Start video generation job."""
        job_id = str(uuid.uuid4())[:8]
        _jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "topic": req.topic,
            "created_at": time.time(),
            "progress": "Queued",
        }
        bg.add_task(_run_generate, job_id, req)
        return JobResponse(job_id=job_id, status="queued", message="Job created")

    @app.post("/api/evaluate")
    async def evaluate_video(req: EvaluateRequest):
        """Evaluate video quality."""
        from src.quality_gate import evaluate

        if not os.path.isfile(req.video_path):
            raise HTTPException(404, f"Video not found: {req.video_path}")

        result = evaluate(
            video_path=req.video_path,
            prompt=req.prompt,
            layers=req.layers,
        )

        response = {
            "video_path": result.video_path,
            "layers": result.layers_run,
            "passed": result.passed,
        }
        if result.decision:
            response["verdict"] = result.decision.verdict
            response["confidence"] = result.decision.confidence
            response["reasons"] = result.decision.reasons

        return JSONResponse(response)

    @app.get("/api/jobs")
    async def list_jobs():
        """List all jobs."""
        return JSONResponse([
            {
                "id": j["id"],
                "status": j["status"],
                "topic": j.get("topic", ""),
                "progress": j.get("progress", ""),
            }
            for j in _jobs.values()
        ])

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: str):
        """Get job status and result."""
        if job_id not in _jobs:
            raise HTTPException(404, f"Job not found: {job_id}")
        return JSONResponse(_jobs[job_id])

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    return app


def main():
    """Run the server."""
    try:
        import uvicorn
    except ImportError:
        print("uvicorn is not installed. Install with: pip install uvicorn")
        return 1

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    main()
