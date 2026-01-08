"""Assemble vertical video for YouTube Shorts."""

import os
import random
from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx import FadeIn, FadeOut

# Shorts-specific settings
RESOLUTION = (1080, 1920)  # Vertical 9:16 aspect ratio
CLIP_DURATION_RANGE = (2, 5)  # 2-5 seconds per clip
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']

# Assets path (shared with parent LongFormYT)
ASSETS_DIR = Path(__file__).parent.parent / "assets" / "videos"


def get_available_videos() -> list[Path]:
    """Get all video files from the shared assets folder."""
    videos = []
    for ext in VIDEO_EXTENSIONS:
        videos.extend(ASSETS_DIR.glob(f"*{ext}"))
        videos.extend(ASSETS_DIR.glob(f"*{ext.upper()}"))
    return sorted(videos)


def assemble_video(voiceover_path: str, output_path: str) -> str:
    """
    Assemble a vertical YouTube Short from voiceover and random video clips.

    Args:
        voiceover_path: Path to the voiceover audio file
        output_path: Path to save the final video

    Returns:
        Path to the generated video
    """
    print("Starting video assembly...")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load voiceover to get duration
    print(f"  Loading voiceover: {voiceover_path}")
    voiceover = AudioFileClip(voiceover_path)
    total_duration = voiceover.duration
    print(f"  Duration: {total_duration:.1f}s")

    # Get available videos
    available_videos = get_available_videos()
    if not available_videos:
        raise FileNotFoundError(f"No videos found in {ASSETS_DIR}")

    print(f"  Found {len(available_videos)} source video(s)")

    # Load all source videos
    source_clips = {}
    for video_path in available_videos:
        clip = VideoFileClip(str(video_path))
        source_clips[str(video_path)] = clip
        print(f"    Loaded: {video_path.name} ({clip.duration:.1f}s)")

    video_paths = list(source_clips.keys())

    # Create fast cuts until we have enough duration
    print(f"\n  Creating fast cuts...")
    video_clips = []
    current_duration = 0
    clip_count = 0

    while current_duration < total_duration:
        # Random clip duration between 2-5 seconds
        clip_duration = random.uniform(*CLIP_DURATION_RANGE)

        # Don't exceed total duration
        if current_duration + clip_duration > total_duration:
            clip_duration = total_duration - current_duration

        if clip_duration < 0.5:  # Skip very short clips
            break

        # Randomly select which video to use
        selected_video_path = random.choice(video_paths)
        selected_clip = source_clips[selected_video_path]

        # Random start position in the video
        max_start = max(0, selected_clip.duration - clip_duration)
        start = random.uniform(0, max_start)
        end = start + clip_duration

        clip_count += 1
        print(f"    Clip {clip_count}: {Path(selected_video_path).name} [{start:.1f}s - {end:.1f}s] ({clip_duration:.1f}s)")

        try:
            # Extract clip
            clip = selected_clip.subclipped(start, end)

            # Resize to vertical format (crop to center if needed)
            clip = resize_to_vertical(clip)

            video_clips.append(clip)
            current_duration += clip_duration

        except Exception as e:
            print(f"      Error: {e}")
            # Fallback to black clip
            fallback = ColorClip(
                size=RESOLUTION,
                color=(0, 0, 0),
                duration=clip_duration,
            )
            video_clips.append(fallback)
            current_duration += clip_duration

    print(f"\n  Created {len(video_clips)} clips")

    # Concatenate all clips
    print("  Concatenating clips...")
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Add subtle fade in/out
    final_video = final_video.with_effects([
        FadeIn(0.3),
        FadeOut(0.3),
    ])

    # Attach voiceover
    print("  Attaching voiceover...")
    final_video = final_video.with_audio(voiceover)

    # Render
    print(f"  Rendering to {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k",  # Higher bitrate for Shorts quality
        audio_bitrate="192k",
        threads=4,
    )

    # Cleanup
    final_video.close()
    voiceover.close()
    for source_clip in source_clips.values():
        source_clip.close()
    for clip in video_clips:
        clip.close()

    print(f"\n  Done! Video saved to: {output_path}")
    return output_path


def resize_to_vertical(clip: VideoFileClip) -> VideoFileClip:
    """
    Resize and crop a video clip to vertical 9:16 format.

    Centers the crop on the original video.
    """
    target_width, target_height = RESOLUTION
    target_ratio = target_width / target_height  # 0.5625 for 9:16

    original_width, original_height = clip.size
    original_ratio = original_width / original_height

    if original_ratio > target_ratio:
        # Video is wider than target - crop sides
        new_width = int(original_height * target_ratio)
        x_center = original_width // 2
        x1 = x_center - new_width // 2
        clip = clip.cropped(x1=x1, x2=x1 + new_width)
    else:
        # Video is taller than target - crop top/bottom
        new_height = int(original_width / target_ratio)
        y_center = original_height // 2
        y1 = y_center - new_height // 2
        clip = clip.cropped(y1=y1, y2=y1 + new_height)

    # Resize to exact target resolution
    clip = clip.resized(RESOLUTION)

    return clip


if __name__ == "__main__":
    # Test with a sample voiceover
    print("Video assembler test")
    print(f"Assets directory: {ASSETS_DIR}")
    print(f"Available videos: {[v.name for v in get_available_videos()]}")
