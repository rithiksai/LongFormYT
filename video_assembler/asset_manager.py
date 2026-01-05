"""Asset manager for managing local video clips."""

import random
from pathlib import Path
from typing import Optional, List

from .config import DEFAULT_CONFIG


class AssetManager:
    """Manages local video assets for video generation."""

    # Supported video extensions
    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']

    def __init__(self, assets_dir: Optional[str] = None):
        """
        Initialize the asset manager.

        Args:
            assets_dir: Directory containing video assets
        """
        self.assets_dir = Path(assets_dir or DEFAULT_CONFIG.get("assets_dir", "./assets/videos"))
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self._used_videos = set()  # Track used videos to avoid repetition

    def get_available_videos(self) -> List[Path]:
        """
        Get all video files in the assets folder.

        Returns:
            List of paths to video files
        """
        videos = []
        for ext in self.VIDEO_EXTENSIONS:
            videos.extend(self.assets_dir.glob(f"*{ext}"))
            videos.extend(self.assets_dir.glob(f"*{ext.upper()}"))
        return sorted(videos)

    def get_random_video(self) -> str:
        """
        Get a random video from available assets.

        Prefers unused videos, but cycles through all if all have been used.

        Returns:
            Path to a randomly selected video file

        Raises:
            FileNotFoundError: If no videos are found in the assets folder
        """
        available = self.get_available_videos()

        if not available:
            raise FileNotFoundError(
                f"No videos found in {self.assets_dir}. "
                f"Please add video files ({', '.join(self.VIDEO_EXTENSIONS)}) to this folder."
            )

        # Prefer unused videos, but cycle if all used
        unused = [v for v in available if str(v) not in self._used_videos]
        if not unused:
            # All videos have been used, reset and start over
            self._used_videos.clear()
            unused = available

        selected = random.choice(unused)
        self._used_videos.add(str(selected))

        print(f"Selected video: {selected.name}")
        return str(selected)

    def get_video_count(self) -> int:
        """Get the number of available videos."""
        return len(self.get_available_videos())

    def reset_usage(self):
        """Reset the used videos tracking."""
        self._used_videos.clear()

    def list_videos(self) -> List[str]:
        """List all available video filenames."""
        return [v.name for v in self.get_available_videos()]


if __name__ == "__main__":
    # Test the asset manager
    manager = AssetManager()

    print(f"Assets directory: {manager.assets_dir}")
    print(f"Available videos: {manager.get_video_count()}")

    if manager.get_video_count() > 0:
        print(f"Videos: {manager.list_videos()}")
        video = manager.get_random_video()
        print(f"Random video: {video}")
    else:
        print("No videos found. Add videos to assets/videos/ folder.")
