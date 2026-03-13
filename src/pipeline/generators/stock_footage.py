"""Stock footage generator — search and download from stock video APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


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
        # TODO: implement provider-specific API search
        raise NotImplementedError

    def download(self, url: str, output_path: str) -> str:
        """Download a video clip to a local path.

        Args:
            url: Remote URL of the video clip.
            output_path: Local file path to save the downloaded clip.

        Returns:
            The output_path on success.
        """
        # TODO: implement HTTP download with progress tracking
        raise NotImplementedError
