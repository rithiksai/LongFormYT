"""Configuration settings for the video assembler."""

import os
from pathlib import Path

# Base directory for the video assembler
BASE_DIR = Path(__file__).parent

# Default configuration
DEFAULT_CONFIG = {
    # Output settings
    "resolution": (1920, 1080),
    "fps": 30,
    "video_codec": "libx264",
    "audio_codec": "aac",
    "video_bitrate": "5000k",
    "audio_bitrate": "192k",

    # Cache settings
    "cache_dir": str(BASE_DIR / "cache"),
    "clips_dir": str(BASE_DIR / "cache" / "clips"),
    "output_dir": str(BASE_DIR / "output"),

    # Download settings
    "youtube_format": "best[height<=1080]",
    "max_clip_duration": 15,
    "retry_attempts": 3,

    # Graphics settings
    "default_font": "Arial-Bold",
    "caption_font_size": 60,
    "title_font_size": 100,
    "text_color": "white",
    "text_stroke_color": "black",
    "text_stroke_width": 3,

    # Effects settings
    "transition_duration": 0.5,
    "fade_duration": 0.3,

    # Performance
    "preview_resolution": (1280, 720),
    "threads": 4,
}


def get_config(key: str, default=None):
    """Get a configuration value."""
    return DEFAULT_CONFIG.get(key, default)


def ensure_directories():
    """Ensure all required directories exist."""
    for dir_key in ["cache_dir", "clips_dir", "output_dir"]:
        dir_path = Path(DEFAULT_CONFIG[dir_key])
        dir_path.mkdir(parents=True, exist_ok=True)
