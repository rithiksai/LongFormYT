"""Main video assembler - orchestrates the full video generation pipeline."""

import os
import re
from pathlib import Path
from typing import Optional, List

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
)

from .config import DEFAULT_CONFIG, ensure_directories
from .asset_manager import AssetManager
from .motion_graphics import MotionGraphics
from .scene_composer import SceneComposer
from .effects import Effects
from .models import Scene, ScriptData


class VideoAssembler:
    """
    Main video assembler that orchestrates the full video generation pipeline.

    Takes a script and voiceover as input and produces a complete video.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the video assembler.

        Args:
            config: Optional configuration overrides
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.resolution = self.config["resolution"]

        # Initialize components
        self.asset_manager = AssetManager(self.config["clips_dir"])
        self.motion_graphics = MotionGraphics(self.resolution)
        self.scene_composer = SceneComposer(self.resolution)
        self.effects = Effects()

        # Ensure directories exist
        ensure_directories()

    def generate_video(
        self,
        script_data: dict,
        voiceover_path: str,
        output_path: str = "output/final_video.mp4",
    ) -> str:
        """
        Generate a complete video from script and voiceover.

        Args:
            script_data: Script JSON with scenes
            voiceover_path: Path to voiceover audio file
            output_path: Where to save final video

        Returns:
            Path to the generated video file
        """
        print("Starting video generation...")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Load voiceover
        print(f"Loading voiceover from: {voiceover_path}")
        voiceover = AudioFileClip(voiceover_path)
        total_duration = voiceover.duration
        print(f"Voiceover duration: {total_duration}s")

        # Parse scenes
        scenes = script_data.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes found in script data")

        # Calculate duration per scene
        scene_duration = total_duration / len(scenes)

        # Generate each scene
        composed_scenes = []
        for i, scene in enumerate(scenes):
            print(f"Processing scene {i + 1}/{len(scenes)}...")

            scene_clip = self._generate_scene(
                scene=scene,
                scene_index=i,
                duration=scene_duration,
            )
            composed_scenes.append(scene_clip)

        # Concatenate all scenes with transitions
        print("Concatenating scenes...")
        final_video = concatenate_videoclips(
            composed_scenes,
            method="compose",
        )
        print(f"Final video duration: {final_video.duration}s")

        # Apply final fade in/out first (before audio)
        final_video = self.effects.apply_fade_in_out(final_video)

        # Set the full voiceover audio LAST (after all video effects)
        print("Attaching audio...")
        final_video = final_video.with_audio(voiceover)
        print(f"Audio attached: {final_video.audio is not None}")

        # Render the final video
        print(f"Rendering video to {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=self.config["fps"],
            codec=self.config["video_codec"],
            audio_codec=self.config["audio_codec"],
            bitrate=self.config["video_bitrate"],
            audio_bitrate=self.config["audio_bitrate"],
            threads=self.config["threads"],
        )

        # Cleanup
        final_video.close()
        voiceover.close()
        for scene in composed_scenes:
            scene.close()

        print(f"Video generated successfully: {output_path}")
        return output_path

    def _generate_scene(
        self,
        scene: dict,
        scene_index: int,
        duration: float,
    ):
        """
        Generate a single scene.

        Args:
            scene: Scene data dict
            scene_index: Index of the scene
            duration: Target duration for the scene

        Returns:
            Composed scene clip
        """
        narration = scene.get("narration", "")
        visual_suggestion = scene.get("visual_suggestion", "")

        # Determine scene type and search query
        scene_type = self._detect_scene_type(narration, visual_suggestion)
        search_query = self._generate_search_query(visual_suggestion, narration)

        try:
            # Download clip based on visual suggestion
            clip_path = self.asset_manager.download_clip(
                query=search_query,
                duration=int(duration) + 5,  # Download extra to have buffer
            )

            # Compose scene with video and caption
            composed = self.scene_composer.compose_scene(
                video_path=clip_path,
                narration_text=narration,
                duration=duration,
            )

        except Exception as e:
            print(f"Error getting clip for scene {scene_index}: {e}")
            # Fallback to title card if clip download fails
            composed = self.motion_graphics.create_title_card(
                title=narration[:50] + "..." if len(narration) > 50 else narration,
                subtitle="",
                duration=duration,
            )

        return composed

    def _detect_scene_type(self, narration: str, visual_suggestion: str) -> str:
        """
        Detect the type of scene from narration and visual suggestion.

        Args:
            narration: Scene narration text
            visual_suggestion: Visual suggestion text

        Returns:
            Scene type string
        """
        combined = (narration + " " + visual_suggestion).lower()

        # Check for ranking patterns
        rank_pattern = r"(number\s*\d+|#\d+|\d+\s*(st|nd|rd|th))"
        if re.search(rank_pattern, combined):
            return "ranking"

        # Check for intro patterns
        intro_keywords = ["intro", "welcome", "today", "in this video"]
        if any(kw in combined for kw in intro_keywords):
            return "intro"

        # Check for comparison patterns
        comparison_keywords = ["vs", "versus", "compare", "comparison", "battle"]
        if any(kw in combined for kw in comparison_keywords):
            return "comparison"

        # Default to explanation
        return "explanation"

    def _generate_search_query(self, visual_suggestion: str, narration: str) -> str:
        """
        Generate a YouTube search query from visual suggestion.

        Args:
            visual_suggestion: Visual suggestion from script
            narration: Narration text (fallback)

        Returns:
            Search query string
        """
        # Use visual suggestion if available
        if visual_suggestion:
            # Clean up and make it search-friendly
            query = visual_suggestion

            # Add "anime" if not present
            if "anime" not in query.lower():
                query = f"anime {query}"

            # Add "clip" or "scene" if not present
            if not any(kw in query.lower() for kw in ["clip", "scene", "moment"]):
                query = f"{query} scene"

            return query

        # Fallback to extracting keywords from narration
        # Extract potential anime/character names
        words = narration.split()[:10]  # First 10 words
        return f"anime {' '.join(words)} scene"

    def _parse_timestamp(self, timestamp: str) -> float:
        """
        Convert timestamp string to seconds.

        Args:
            timestamp: Timestamp string (e.g., "0:15", "1:30:00")

        Returns:
            Time in seconds
        """
        parts = timestamp.split(":")
        if len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            try:
                return float(timestamp)
            except ValueError:
                return 0.0


def generate_video(
    script_data: dict,
    voiceover_path: str,
    output_path: str = "output/final_video.mp4",
) -> str:
    """
    Convenience function to generate a video.

    Args:
        script_data: Script JSON with scenes
        voiceover_path: Path to voiceover audio
        output_path: Output video path

    Returns:
        Path to generated video
    """
    assembler = VideoAssembler()
    return assembler.generate_video(script_data, voiceover_path, output_path)


if __name__ == "__main__":
    # Test with sample data
    sample_script = {
        "script": "Today we explore the top anime moments...",
        "duration_estimate": 30,
        "scenes": [
            {
                "timestamp": "0:00",
                "narration": "Welcome to our countdown of epic anime moments!",
                "visual_suggestion": "anime epic montage action scenes",
            },
            {
                "timestamp": "0:10",
                "narration": "Number 3: The legendary battle begins!",
                "visual_suggestion": "anime battle fight scene dramatic",
            },
            {
                "timestamp": "0:20",
                "narration": "And the most epic moment of all time!",
                "visual_suggestion": "anime climax emotional scene",
            },
        ],
    }

    # This would require a voiceover file to test
    print("Video assembler initialized. Provide a voiceover file to test.")
    print("Example usage:")
    print('  generate_video(script_data, "voiceover.mp3", "output.mp4")')
