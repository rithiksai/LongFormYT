"""Data models for the video assembler."""

from pydantic import BaseModel
from typing import Optional


class Scene(BaseModel):
    """Represents a single scene in the video."""
    timestamp: str
    narration: str
    visual_suggestion: str
    duration: Optional[float] = None


class ScriptData(BaseModel):
    """Represents the full script data from the script generator."""
    script: str
    duration_estimate: int
    scenes: list[Scene]


class VideoConfig(BaseModel):
    """Configuration for video generation."""
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    video_bitrate: str = "5000k"
    audio_bitrate: str = "192k"
    cache_dir: str = "./cache"
    output_dir: str = "./output"


class ClipMetadata(BaseModel):
    """Metadata for a downloaded clip."""
    query: str
    file_path: str
    duration: float
    source_url: Optional[str] = None
