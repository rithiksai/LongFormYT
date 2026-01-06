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

        # Load all available source videos
        print(f"\nLoading source videos...")
        available_videos = self.asset_manager.get_available_videos()
        if not available_videos:
            raise FileNotFoundError("No videos found in assets folder")

        # Load all video clips and get their durations
        source_clips = {}
        for video_path in available_videos:
            clip = VideoFileClip(str(video_path))
            source_clips[str(video_path)] = clip
            print(f"  Loaded: {video_path.name} ({clip.duration:.1f}s)")

        # Fast cuts: 4-5 second clips instead of scene-based duration
        import random
        clip_duration = random.uniform(4, 5)  # Random between 4-5 seconds
        num_clips = int(total_duration / clip_duration) + 1

        print(f"\nCreating {num_clips} fast cuts ({clip_duration:.1f}s each)...")
        video_clips = []
        video_paths = list(source_clips.keys())

        for i in range(num_clips):
            # Randomly select which video to use
            selected_video_path = random.choice(video_paths)
            selected_clip = source_clips[selected_video_path]

            # Random clip duration between 4-5 seconds for variety
            this_clip_duration = random.uniform(4, 5)

            # Get random segment from this video
            start, end = self.asset_manager.get_random_clip_from_video(
                selected_video_path,
                selected_clip.duration,
                this_clip_duration
            )

            print(f"  Clip {i + 1}/{num_clips}: {Path(selected_video_path).name} [{start:.1f}s - {end:.1f}s]")

            try:
                clip = selected_clip.subclipped(start, end)
                clip = clip.resized(self.resolution)
                video_clips.append(clip)

            except Exception as e:
                print(f"    Error: {e}")
                # Create black clip as fallback
                from moviepy import ColorClip
                fallback = ColorClip(
                    size=self.resolution,
                    color=(0, 0, 0),
                    duration=this_clip_duration,
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
        for source_clip in source_clips.values():
            source_clip.close()
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
