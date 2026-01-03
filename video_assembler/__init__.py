"""
AI Hook Video Generator - Video Assembler Module

This module provides tools to assemble videos from scripts and voiceovers.
Features animated captions, motion graphics, and smart scene direction.
"""

from .video_assembler import VideoAssembler, generate_video
from .asset_manager import AssetManager
from .motion_graphics import MotionGraphics
from .text_animations import TextAnimations
from .scene_composer import SceneComposer
from .scene_director import SceneDirector, AnimationDirective
from .effects import Effects
from .models import Scene, VideoConfig
from .config import DEFAULT_CONFIG

__all__ = [
    # Main assembler
    "VideoAssembler",
    "generate_video",
    # Components
    "AssetManager",
    "MotionGraphics",
    "TextAnimations",
    "SceneComposer",
    "SceneDirector",
    "AnimationDirective",
    "Effects",
    # Models
    "Scene",
    "VideoConfig",
    "DEFAULT_CONFIG",
]
