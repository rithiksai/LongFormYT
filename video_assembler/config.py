"""Configuration settings for the video assembler."""

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

    # Directory settings
    "assets_dir": str(BASE_DIR.parent / "assets" / "videos"),
    "output_dir": str(BASE_DIR / "output"),

    # Performance
    "threads": 4,
}


def get_config(key: str, default=None):
    """Get a configuration value."""
    return DEFAULT_CONFIG.get(key, default)


def ensure_directories():
    """Ensure all required directories exist."""
    for dir_key in ["assets_dir", "output_dir"]:
        dir_path = Path(DEFAULT_CONFIG[dir_key])
        dir_path.mkdir(parents=True, exist_ok=True)
