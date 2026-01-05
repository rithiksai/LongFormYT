"""Simple video assembler - combines video clips with voiceover audio."""

import os
from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx import FadeIn, FadeOut

from .config import DEFAULT_CONFIG, ensure_directories
from .asset_manager import AssetManager


class VideoAssembler:
    """
    Simple video assembler that combines video clips with voiceover.

    No captions, no motion graphics - just plain video with audio.
    """

    def __init__(self, config: dict = None):
        """
        Initialize the video assembler.

        Args:
            config: Optional configuration overrides
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.resolution = self.config["resolution"]
        self.asset_manager = AssetManager(self.config.get("assets_dir"))
        ensure_directories()

    def generate_video(
        self,
        script_data: dict,
        voiceover_path: str,
        output_path: str = "output/final_video.mp4",
    ) -> str:
        """
        Generate a video from script and voiceover.

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
        print(f"Loading voiceover: {voiceover_path}")
        voiceover = AudioFileClip(voiceover_path)
        total_duration = voiceover.duration
        print(f"Duration: {total_duration:.1f}s")

        # Get scenes
        scenes = script_data.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes found in script data")

        scene_duration = total_duration / len(scenes)
        total_scenes = len(scenes)

        # Get unique videos for variety
        print(f"\nProcessing {total_scenes} scenes...")
        video_clips = []

        for i, scene in enumerate(scenes):
            print(f"  Scene {i + 1}/{total_scenes}")

            try:
                # Get a random video
                video_path = self.asset_manager.get_random_video()

                # Load and prepare clip
                clip = VideoFileClip(video_path)

                # Get a segment from the video
                if clip.duration > scene_duration:
                    # Use different segments for variety
                    max_start = clip.duration - scene_duration
                    start_time = (i * scene_duration) % max_start if max_start > 0 else 0
                    clip = clip.subclipped(start_time, start_time + scene_duration)
                else:
                    # Loop if video is too short
                    clip = clip.with_duration(scene_duration)

                # Resize to target resolution
                clip = clip.resized(self.resolution)

                video_clips.append(clip)

            except Exception as e:
                print(f"    Error: {e}")
                # Create black clip as fallback
                from moviepy import ColorClip
                fallback = ColorClip(
                    size=self.resolution,
                    color=(0, 0, 0),
                    duration=scene_duration,
                )
                video_clips.append(fallback)

        # Concatenate all clips
        print("\nConcatenating clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Add fade in/out
        final_video = final_video.with_effects([
            FadeIn(0.5),
            FadeOut(0.5),
        ])

        # Attach voiceover
        print("Attaching audio...")
        final_video = final_video.with_audio(voiceover)

        # Render
        print(f"Rendering to {output_path}...")
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
        for clip in video_clips:
            clip.close()

        print(f"\nDone! Video saved to: {output_path}")
        return output_path


def generate_video(
    script_data: dict,
    voiceover_path: str,
    output_path: str = "output/final_video.mp4",
) -> str:
    """
    Generate a video from script and voiceover.

    Args:
        script_data: Script JSON with scenes
        voiceover_path: Path to voiceover audio
        output_path: Output video path

    Returns:
        Path to generated video
    """
    assembler = VideoAssembler()
    return assembler.generate_video(script_data, voiceover_path, output_path)
