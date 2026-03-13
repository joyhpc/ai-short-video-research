"""AI video generator — dispatch to AI video generation APIs."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VideoClip:
    """Generated video clip with metadata."""

    local_path: str
    prompt: str
    provider: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    generation_params: dict[str, Any] = field(default_factory=dict)


class AIVideoGenerator:
    """Generate video clips using AI video generation models.

    Supports multiple providers: Kling, Runway, Pika, etc.

    Args:
        default_provider: Default generation provider.
        api_keys: Mapping of provider names to API keys.
        output_dir: Directory for downloaded videos. Uses tempdir if None.
        poll_interval: Initial polling interval in seconds.
        poll_max_interval: Maximum polling interval in seconds.
        poll_timeout: Total timeout for polling in seconds.
    """

    SUPPORTED_PROVIDERS = ("veo", "kling", "runway", "pika", "hailuo")

    # Base URLs per provider
    _BASE_URLS: dict[str, str] = {
        "kling": "https://api.klingai.com",
        "runway": "https://api.runwayml.com",
    }

    def __init__(
        self,
        default_provider: str = "kling",
        api_keys: dict[str, str] | None = None,
        output_dir: str | None = None,
        poll_interval: float = 5.0,
        poll_max_interval: float = 60.0,
        poll_timeout: float = 300.0,
    ) -> None:
        self.default_provider = default_provider
        self.api_keys = api_keys or {}
        self.output_dir = output_dir
        self.poll_interval = poll_interval
        self.poll_max_interval = poll_max_interval
        self.poll_timeout = poll_timeout

        self._dispatch: dict[str, Any] = {
            "veo": self._generate_veo,
            "kling": self._generate_kling,
            "runway": self._generate_runway,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        provider: str | None = None,
        duration: float = 5.0,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> VideoClip:
        """Generate a video clip from a text prompt.

        Args:
            prompt: Text description of the desired video.
            provider: Override the default provider.
            duration: Desired clip duration in seconds.
            width: Output width in pixels.
            height: Output height in pixels.
            seed: Random seed for reproducibility.
            **kwargs: Provider-specific generation parameters.

        Returns:
            VideoClip with local_path set to the downloaded output.

        Raises:
            ValueError: If the provider is unsupported or has no API key.
            RuntimeError: If generation fails or times out.
        """
        provider = (provider or self.default_provider).lower()

        if provider not in self._dispatch:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Available: {list(self._dispatch.keys())}"
            )

        if provider not in self.api_keys and provider != "veo":
            raise ValueError(
                f"No API key configured for provider '{provider}'. "
                f"Pass it via api_keys['{provider}']."
            )

        logger.info(
            "Generating video via %s — prompt=%r, duration=%.1fs, %dx%d",
            provider,
            prompt[:80],
            duration,
            width,
            height,
        )

        handler = self._dispatch[provider]
        return handler(
            prompt=prompt,
            duration=duration,
            width=width,
            height=height,
            seed=seed,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Provider: Veo 3.1  (Google Gemini API)
    # ------------------------------------------------------------------

    def _generate_veo(
        self,
        prompt: str,
        duration: float,
        width: int,
        height: int,
        seed: int | None,
        **kwargs: Any,
    ) -> VideoClip:
        """Generate video using Google Veo 3.1 via the google-genai SDK."""
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise RuntimeError(
                "google-genai is not installed. Run: pip install google-genai"
            )

        api_key = (
            self.api_keys.get("veo")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or ""
        )
        if not api_key:
            raise ValueError(
                "No API key for Veo. Set GEMINI_API_KEY or GOOGLE_API_KEY env var."
            )

        client = genai.Client(api_key=api_key)
        model = kwargs.pop("model", "veo-3.1-generate-preview")

        # Map dimensions to aspect ratio
        aspect_ratio = "9:16" if height > width else "16:9"

        # Veo supports 4, 6, 8 second durations
        veo_duration = 8
        if duration <= 4:
            veo_duration = 4
        elif duration <= 6:
            veo_duration = 6

        # Map to resolution
        resolution = "720p"
        if width >= 3840 or height >= 2160:
            resolution = "4k"
        elif width >= 1920 or height >= 1080:
            resolution = "1080p"

        logger.info(
            "[veo] Generating: model=%s, aspect=%s, resolution=%s, duration=%ds",
            model, aspect_ratio, resolution, veo_duration,
        )

        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            number_of_videos=1,
        )

        operation = client.models.generate_videos(
            model=model,
            prompt=prompt,
            config=config,
        )

        # Poll until done
        elapsed = 0.0
        while not operation.done:
            logger.info("[veo] Waiting... elapsed=%.0fs", elapsed)
            time.sleep(self.poll_interval)
            elapsed += self.poll_interval
            if elapsed > self.poll_timeout:
                raise RuntimeError(
                    f"[veo] Generation timed out after {self.poll_timeout:.0f}s"
                )
            operation = client.operations.get(operation)

        logger.info("[veo] Generation complete after %.0fs", elapsed)

        # Download result
        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)

        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            local_path = os.path.join(
                self.output_dir, f"veo_{int(time.time())}.mp4"
            )
        else:
            fd, local_path = tempfile.mkstemp(suffix=".mp4", prefix="veo_")
            os.close(fd)

        generated_video.video.save(local_path)

        file_size = os.path.getsize(local_path)
        logger.info("[veo] Saved: %s (%.1f MB)", local_path, file_size / 1024 / 1024)

        return VideoClip(
            local_path=local_path,
            prompt=prompt,
            provider="veo",
            duration=float(veo_duration),
            width=width,
            height=height,
            generation_params={
                "model": model,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "seed": seed,
                **kwargs,
            },
        )

    # ------------------------------------------------------------------
    # Provider: Kling  (https://api.klingai.com)
    # ------------------------------------------------------------------

    def _generate_kling(
        self,
        prompt: str,
        duration: float,
        width: int,
        height: int,
        seed: int | None,
        **kwargs: Any,
    ) -> VideoClip:
        """End-to-end Kling text-to-video generation."""
        base = self._BASE_URLS["kling"]
        api_key = self.api_keys["kling"]

        # -- 1. Submit task --
        submit_url = f"{base}/v1/videos/text2video"
        payload: dict[str, Any] = {
            "prompt": prompt,
            "duration": str(duration),
            "aspect_ratio": _aspect_ratio(width, height),
        }
        if seed is not None:
            payload["seed"] = seed
        # Merge any provider-specific overrides (e.g. model, cfg_scale)
        payload.update(kwargs)

        task_data = self._submit_task(
            url=submit_url,
            payload=payload,
            api_key=api_key,
            provider="kling",
        )

        task_id = task_data.get("task_id") or task_data.get("id")
        if not task_id:
            raise RuntimeError(f"Kling submit returned no task_id: {task_data}")

        logger.info("Kling task submitted — task_id=%s", task_id)

        # -- 2. Poll until complete --
        poll_url = f"{base}/v1/videos/text2video/{task_id}"
        result_data = self._poll_task(
            url=poll_url,
            api_key=api_key,
            provider="kling",
            done_statuses=("completed", "succeed", "success"),
            fail_statuses=("failed", "error", "cancelled"),
            status_path=("status",),
        )

        # -- 3. Download video --
        video_url = _deep_get(result_data, "output", "video_url") or _deep_get(
            result_data, "result", "video_url"
        )
        if not video_url:
            # Try flat key
            video_url = result_data.get("video_url")
        if not video_url:
            raise RuntimeError(
                f"Kling completed but no video_url found in response: {result_data}"
            )

        local_path = self._download_result(
            video_url, provider="kling", suffix=".mp4"
        )

        return VideoClip(
            local_path=local_path,
            prompt=prompt,
            provider="kling",
            duration=duration,
            width=width,
            height=height,
            generation_params={
                "task_id": task_id,
                "seed": seed,
                **kwargs,
            },
        )

    # ------------------------------------------------------------------
    # Provider: Runway  (https://api.runwayml.com)
    # ------------------------------------------------------------------

    def _generate_runway(
        self,
        prompt: str,
        duration: float,
        width: int,
        height: int,
        seed: int | None,
        **kwargs: Any,
    ) -> VideoClip:
        """End-to-end Runway text-to-video generation."""
        base = self._BASE_URLS["runway"]
        api_key = self.api_keys["runway"]

        # Runway supports both image_to_video and text_to_video.
        # Use text_to_video when no reference image is provided.
        ref_image: str | None = kwargs.pop("reference_image", None)

        if ref_image:
            submit_url = f"{base}/v1/image_to_video"
            payload: dict[str, Any] = {
                "prompt": prompt,
                "image": ref_image,
                "duration": duration,
                "resolution": f"{width}x{height}",
            }
        else:
            submit_url = f"{base}/v1/text_to_video"
            payload = {
                "prompt": prompt,
                "duration": duration,
                "resolution": f"{width}x{height}",
            }

        if seed is not None:
            payload["seed"] = seed
        payload.update(kwargs)

        task_data = self._submit_task(
            url=submit_url,
            payload=payload,
            api_key=api_key,
            provider="runway",
        )

        task_id = task_data.get("id") or task_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Runway submit returned no task id: {task_data}")

        logger.info("Runway task submitted — id=%s", task_id)

        # -- Poll --
        poll_url = f"{base}/v1/tasks/{task_id}"
        result_data = self._poll_task(
            url=poll_url,
            api_key=api_key,
            provider="runway",
            done_statuses=("completed", "succeeded", "success"),
            fail_statuses=("failed", "error", "cancelled"),
            status_path=("status",),
        )

        # -- Download --
        video_url = (
            _deep_get(result_data, "output", "url")
            or _deep_get(result_data, "artifacts", 0, "url")
            or result_data.get("url")
        )
        if not video_url:
            raise RuntimeError(
                f"Runway completed but no video URL found in response: {result_data}"
            )

        local_path = self._download_result(
            video_url, provider="runway", suffix=".mp4"
        )

        return VideoClip(
            local_path=local_path,
            prompt=prompt,
            provider="runway",
            duration=duration,
            width=width,
            height=height,
            generation_params={
                "task_id": task_id,
                "seed": seed,
                "reference_image": ref_image,
                **kwargs,
            },
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _submit_task(
        self,
        url: str,
        payload: dict[str, Any],
        api_key: str,
        provider: str,
    ) -> dict[str, Any]:
        """POST a generation task to the provider and return the parsed response.

        Raises:
            RuntimeError: On HTTP or JSON errors.
        """
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        logger.debug("POST %s payload=%s", url, payload)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise RuntimeError(
                f"[{provider}] Submit failed — HTTP {exc.code}: {error_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"[{provider}] Submit failed — network error: {exc.reason}"
            ) from exc

        try:
            data: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"[{provider}] Submit returned invalid JSON: {raw[:500]}"
            ) from exc

        # Some APIs wrap the result under a "data" key
        if "data" in data and isinstance(data["data"], dict):
            return data["data"]
        return data

    def _poll_task(
        self,
        url: str,
        api_key: str,
        provider: str,
        done_statuses: tuple[str, ...],
        fail_statuses: tuple[str, ...],
        status_path: tuple[str, ...] = ("status",),
    ) -> dict[str, Any]:
        """Poll task status with exponential backoff until done or timeout.

        Args:
            url: GET endpoint to poll.
            api_key: Bearer token.
            provider: Provider name (for log messages).
            done_statuses: Status values that indicate completion.
            fail_statuses: Status values that indicate failure.
            status_path: Nested key path to extract status from response.

        Returns:
            The final response dict when the task is complete.

        Raises:
            RuntimeError: On failure, timeout, or HTTP errors.
        """
        headers = {"Authorization": f"Bearer {api_key}"}
        interval = self.poll_interval
        elapsed = 0.0

        while elapsed < self.poll_timeout:
            time.sleep(interval)
            elapsed += interval

            req = urllib.request.Request(url, headers=headers, method="GET")

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                logger.warning(
                    "[%s] Poll HTTP %d — retrying", provider, exc.code
                )
                interval = min(interval * 2, self.poll_max_interval)
                continue
            except urllib.error.URLError as exc:
                logger.warning(
                    "[%s] Poll network error: %s — retrying", provider, exc.reason
                )
                interval = min(interval * 2, self.poll_max_interval)
                continue

            try:
                data: dict[str, Any] = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("[%s] Poll returned invalid JSON — retrying", provider)
                interval = min(interval * 2, self.poll_max_interval)
                continue

            # Unwrap "data" envelope if present
            inner = data
            if "data" in data and isinstance(data["data"], dict):
                inner = data["data"]

            # Extract status using the key path
            status_val = inner
            for key in status_path:
                if isinstance(status_val, dict):
                    status_val = status_val.get(key)
                else:
                    status_val = None
                    break

            status_str = str(status_val).lower() if status_val else "unknown"

            logger.info(
                "[%s] Poll — status=%s, elapsed=%.0fs/%.0fs",
                provider,
                status_str,
                elapsed,
                self.poll_timeout,
            )

            if status_str in done_statuses:
                return inner

            if status_str in fail_statuses:
                error_msg = inner.get("error") or inner.get("message") or str(inner)
                raise RuntimeError(
                    f"[{provider}] Task failed — status={status_str}: {error_msg}"
                )

            # Exponential backoff
            interval = min(interval * 2, self.poll_max_interval)

        raise RuntimeError(
            f"[{provider}] Task timed out after {self.poll_timeout:.0f}s"
        )

    def _download_result(
        self,
        video_url: str,
        provider: str,
        suffix: str = ".mp4",
    ) -> str:
        """Download a video from *video_url* and save to a local file.

        If ``self.output_dir`` is set the file goes there; otherwise a
        temporary file is created.

        Returns:
            Absolute path to the downloaded file.

        Raises:
            RuntimeError: On download errors.
        """
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            filename = f"{provider}_{int(time.time())}{suffix}"
            local_path = os.path.join(self.output_dir, filename)
        else:
            fd, local_path = tempfile.mkstemp(suffix=suffix, prefix=f"{provider}_")
            os.close(fd)

        logger.info("[%s] Downloading video → %s", provider, local_path)

        req = urllib.request.Request(video_url, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                with open(local_path, "wb") as fout:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        fout.write(chunk)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            raise RuntimeError(
                f"[{provider}] Download failed for {video_url}: {exc}"
            ) from exc

        file_size = os.path.getsize(local_path)
        logger.info(
            "[%s] Download complete — %s (%.1f MB)",
            provider,
            local_path,
            file_size / (1024 * 1024),
        )

        return local_path


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _aspect_ratio(width: int, height: int) -> str:
    """Return a human-friendly aspect-ratio string (e.g. '9:16')."""
    from math import gcd

    g = gcd(width, height)
    return f"{width // g}:{height // g}"


def _deep_get(d: Any, *keys: Any) -> Any:
    """Traverse nested dicts/lists by a sequence of keys/indices.

    Returns ``None`` if any step fails.
    """
    current = d
    for k in keys:
        try:
            if isinstance(current, dict):
                current = current[k]
            elif isinstance(current, (list, tuple)) and isinstance(k, int):
                current = current[k]
            else:
                return None
        except (KeyError, IndexError, TypeError):
            return None
    return current
