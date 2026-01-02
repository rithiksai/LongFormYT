"""
AI Hook Video Generator - Video Assembler Module

This module provides tools to assemble videos from scripts and voiceovers.
"""

from .video_assembler import VideoAssembler
from .asset_manager import AssetManager
from .motion_graphics import MotionGraphics
from .scene_composer import SceneComposer
from .effects import Effects
from .models import Scene, VideoConfig
from .config import DEFAULT_CONFIG

__all__ = [
    "VideoAssembler",
    "AssetManager",
    "MotionGraphics",
    "SceneComposer",
    "Effects",
    "Scene",
    "VideoConfig",
    "DEFAULT_CONFIG",
]
