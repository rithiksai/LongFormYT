"""Asset manager for downloading and managing video clips."""

import os
import hashlib
import json
from pathlib import Path
from typing import Optional

import yt_dlp

from .config import DEFAULT_CONFIG, ensure_directories


class AssetManager:
    """Manages downloading and caching of video clips from YouTube."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the asset manager.

        Args:
            cache_dir: Directory to cache downloaded clips
        """
        self.cache_dir = Path(cache_dir or DEFAULT_CONFIG["clips_dir"])
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        """Load cached clip metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save clip metadata to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key from a query string."""
        return hashlib.md5(query.encode()).hexdigest()[:12]

    def is_cached(self, query: str) -> bool:
        """Check if a clip is already cached."""
        cache_key = self._get_cache_key(query)
        if cache_key in self.metadata:
            file_path = Path(self.metadata[cache_key]["file_path"])
            return file_path.exists()
        return False

    def get_cached_path(self, query: str) -> Optional[str]:
        """Get the path to a cached clip if it exists."""
        cache_key = self._get_cache_key(query)
        if cache_key in self.metadata:
            file_path = self.metadata[cache_key]["file_path"]
            if Path(file_path).exists():
                return file_path
        return None

    def download_clip(
        self,
        query: str,
        duration: int = 10,
        force: bool = False
    ) -> str:
        """
        Search YouTube and download a clip.

        Args:
            query: Search query (e.g., "attack on titan action scene")
            duration: Target duration in seconds (used for search)
            force: Force re-download even if cached

        Returns:
            Path to the downloaded clip
        """
        # Check cache first
        if not force and self.is_cached(query):
            cached_path = self.get_cached_path(query)
            if cached_path:
                print(f"Using cached clip for: {query}")
                return cached_path

        cache_key = self._get_cache_key(query)
        output_path = str(self.cache_dir / f"{cache_key}.mp4")

        # yt-dlp options for search and download
        ydl_opts = {
            "format": "best[height<=1080][ext=mp4]/best[height<=1080]/best",
            "outtmpl": output_path,
            "quiet": False,  # Show output for debugging
            "no_warnings": False,
            "extract_flat": False,
            "noplaylist": True,
        }

        search_query = f"ytsearch1:{query}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Searching and downloading: {query}")
                info = ydl.extract_info(search_query, download=True)

                if info and "entries" in info:
                    if len(info["entries"]) == 0:
                        raise Exception(f"No results found for query: {query}")
                    info = info["entries"][0]

                # Store metadata
                self.metadata[cache_key] = {
                    "query": query,
                    "file_path": output_path,
                    "duration": info.get("duration", 0),
                    "source_url": info.get("webpage_url", ""),
                    "title": info.get("title", ""),
                }
                self._save_metadata()

                print(f"Downloaded: {info.get('title', 'Unknown')}")
                return output_path

        except Exception as e:
            print(f"Error downloading clip: {e}")
            raise

    def download_from_url(
        self,
        url: str,
        start_time: float = 0,
        duration: float = 10,
        output_name: Optional[str] = None
    ) -> str:
        """
        Download a specific clip from a YouTube URL.

        Args:
            url: YouTube video URL
            start_time: Start time in seconds
            duration: Duration to download in seconds
            output_name: Optional custom output filename

        Returns:
            Path to the downloaded clip
        """
        cache_key = output_name or self._get_cache_key(f"{url}_{start_time}_{duration}")
        output_path = str(self.cache_dir / f"{cache_key}.mp4")

        # Check if already exists
        if Path(output_path).exists():
            print(f"Using cached clip: {output_path}")
            return output_path

        ydl_opts = {
            "format": "best[height<=1080][ext=mp4]/best[height<=1080]/best",
            "outtmpl": output_path,
            "quiet": True,
            "no_warnings": True,
            # Download section
            "download_ranges": yt_dlp.utils.download_range_func(
                None, [(start_time, start_time + duration)]
            ),
            "force_keyframes_at_cuts": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading from URL: {url} ({start_time}s - {start_time + duration}s)")
                info = ydl.extract_info(url, download=True)

                # Store metadata
                self.metadata[cache_key] = {
                    "query": url,
                    "file_path": output_path,
                    "duration": duration,
                    "source_url": url,
                    "title": info.get("title", ""),
                    "start_time": start_time,
                }
                self._save_metadata()

                return output_path

        except Exception as e:
            print(f"Error downloading from URL: {e}")
            raise

    def clear_cache(self):
        """Clear all cached clips."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = {}
        self._save_metadata()
        print("Cache cleared")

    def get_cache_size(self) -> int:
        """Get total size of cached clips in bytes."""
        total_size = 0
        for file in self.cache_dir.glob("*.mp4"):
            total_size += file.stat().st_size
        return total_size


if __name__ == "__main__":
    # Test the asset manager
    manager = AssetManager()

    # Test search and download
    clip_path = manager.download_clip("anime action scene short", duration=10)
    print(f"Downloaded clip: {clip_path}")
