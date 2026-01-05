"""Video Assembler - Combines video clips with voiceover audio."""

from .video_assembler import VideoAssembler, generate_video
from .asset_manager import AssetManager
from .config import DEFAULT_CONFIG

__all__ = [
    "VideoAssembler",
    "generate_video",
    "AssetManager",
    "DEFAULT_CONFIG",
]
