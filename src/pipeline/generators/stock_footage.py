"""Stock footage generator — search and download from stock video APIs."""

from __future__ import annotations

import json
import logging
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class VideoClip:
    """Metadata and local path for a downloaded video clip."""

    url: str
    local_path: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class StockFootageGenerator:
    """Search and download stock footage clips.

    Supports pluggable backends (Pexels, Pixabay, etc.).

    Args:
        provider: Stock footage API provider name.
        api_key: API key for the provider.
    """

    SUPPORTED_PROVIDERS = ("pexels", "pixabay")

    def __init__(
        self,
        provider: str = "pexels",
        api_key: str | None = None,
    ) -> None:
        self.provider = provider
        self.api_key = api_key or ""

    def search(
        self, query: str, count: int = 5
    ) -> list[VideoClip]:
        """Search for stock video clips matching a query.

        Args:
            query: Search query string (e.g. "ocean sunset drone").
            count: Maximum number of results to return.

        Returns:
            List of VideoClip objects with URLs populated (not yet
            downloaded).
        """
        if self.provider == "pexels":
            return self._search_pexels(query, count)
        elif self.provider == "pixabay":
            return self._search_pixabay(query, count)
        else:
            raise ValueError(
                f"Unsupported provider '{self.provider}'. "
                f"Choose from: {self.SUPPORTED_PROVIDERS}"
            )

    # ------------------------------------------------------------------
    # Provider-specific search implementations
    # ------------------------------------------------------------------

    def _search_pexels(self, query: str, count: int) -> list[VideoClip]:
        """Search the Pexels Videos API.

        Docs: https://www.pexels.com/api/documentation/#videos-search
        """
        params = urllib.parse.urlencode({"query": query, "per_page": count})
        url = f"https://api.pexels.com/videos/search?{params}"

        req = urllib.request.Request(url)
        req.add_header("Authorization", self.api_key)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            logger.exception("Pexels API request failed for query=%r", query)
            return []

        clips: list[VideoClip] = []
        for video in data.get("videos", []):
            # Pick the best-quality video file available.
            video_files = video.get("video_files", [])
            if not video_files:
                continue

            # Sort by width descending; pick the largest rendition.
            best = max(video_files, key=lambda f: f.get("width", 0) or 0)

            clips.append(
                VideoClip(
                    url=best.get("link", ""),
                    duration=float(video.get("duration", 0)),
                    width=int(best.get("width", 0) or 0),
                    height=int(best.get("height", 0) or 0),
                    metadata={
                        "provider": "pexels",
                        "id": video.get("id"),
                        "quality": best.get("quality"),
                        "file_type": best.get("file_type"),
                    },
                )
            )

        logger.info(
            "Pexels search query=%r returned %d clips", query, len(clips)
        )
        return clips

    def _search_pixabay(self, query: str, count: int) -> list[VideoClip]:
        """Search the Pixabay Videos API.

        Docs: https://pixabay.com/api/docs/#api_search_videos
        """
        params = urllib.parse.urlencode({
            "key": self.api_key,
            "q": query,
            "per_page": count,
        })
        url = f"https://pixabay.com/api/videos/?{params}"

        req = urllib.request.Request(url)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            logger.exception("Pixabay API request failed for query=%r", query)
            return []

        clips: list[VideoClip] = []
        for hit in data.get("hits", []):
            videos = hit.get("videos", {})
            # Prefer "large" rendition, fall back through smaller ones.
            for size_key in ("large", "medium", "small", "tiny"):
                rendition = videos.get(size_key)
                if rendition and rendition.get("url"):
                    break
            else:
                continue

            clips.append(
                VideoClip(
                    url=rendition.get("url", ""),
                    duration=float(hit.get("duration", 0)),
                    width=int(rendition.get("width", 0) or 0),
                    height=int(rendition.get("height", 0) or 0),
                    metadata={
                        "provider": "pixabay",
                        "id": hit.get("id"),
                        "tags": hit.get("tags", ""),
                        "size_key": size_key,
                    },
                )
            )

        logger.info(
            "Pixabay search query=%r returned %d clips", query, len(clips)
        )
        return clips

    def download(self, url: str, output_path: str) -> str:
        """Download a video clip to a local path.

        Args:
            url: Remote URL of the video clip.
            output_path: Local file path to save the downloaded clip.

        Returns:
            The output_path on success.

        Raises:
            OSError: If the download or file write fails.
        """
        # Ensure parent directories exist.
        parent_dir = os.path.dirname(output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        logger.info("Downloading %s -> %s", url, output_path)

        try:
            urllib.request.urlretrieve(url, output_path)
        except Exception:
            logger.exception("Failed to download %s", url)
            raise

        logger.info(
            "Download complete: %s (%.2f MB)",
            output_path,
            os.path.getsize(output_path) / (1024 * 1024),
        )
        return output_path
