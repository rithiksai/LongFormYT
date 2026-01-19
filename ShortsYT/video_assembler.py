"""Assemble vertical video for YouTube Shorts."""

import os
import random
from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx import FadeIn, FadeOut

# Shorts-specific settings
RESOLUTION = (1080, 1920)  # Vertical 9:16 aspect ratio
CLIP_DURATION_RANGE = (2, 5)  # 2-5 seconds per clip
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']

# Image mode settings
PHOTO_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
ZOOM_RATIO = 1.15  # How much larger than frame (15% zoom margin for Ken Burns)
EFFECTS = [
    "pan_up",
    "pan_down",
    "zoom_in",
    "zoom_out",
]

# Assets path (shared with parent LongFormYT)
ASSETS_DIR = Path(__file__).parent.parent / "assets" / "videos"


def get_available_videos() -> list[Path]:
    """Get all video files from the shared assets folder."""
    videos = []
    for ext in VIDEO_EXTENSIONS:
        videos.extend(ASSETS_DIR.glob(f"*{ext}"))
        videos.extend(ASSETS_DIR.glob(f"*{ext.upper()}"))
    return sorted(videos)


def get_generated_images(images_dir: str) -> list[Path]:
    """Get all generated images from directory, sorted by filename."""
    images_path = Path(images_dir)
    if not images_path.exists():
        return []

    images = []
    for ext in PHOTO_EXTENSIONS:
        images.extend(images_path.glob(f"*{ext}"))
        images.extend(images_path.glob(f"*{ext.upper()}"))

    return sorted(images)


def resize_cover_vertical(clip, target_w: int, target_h: int):
    """
    Resize image to cover target dimensions (like CSS object-fit: cover).

    The image is scaled so the shorter dimension fills the target,
    and the longer dimension overflows (will be cropped by positioning).
    """
    img_w, img_h = clip.size
    scale = max(target_w / img_w, target_h / img_h)
    return clip.resized(scale)


def apply_ken_burns_vertical(clip: ImageClip, effect: str, duration: float) -> ImageClip:
    """
    Apply Ken Burns panning/zoom effect to an image clip for vertical format.
    Uses percentage-based positioning for smooth, reliable panning.
    """
    w, h = RESOLUTION  # 1080x1920 for vertical

    # Scale image to be larger than frame for panning room
    clip = resize_cover_vertical(clip, w, h)
    clip = clip.resized(ZOOM_RATIO)
    clip = clip.with_duration(duration)

    if effect == "pan_up":
        # Start from bottom (100%), pan to top (0%)
        def position(t):
            progress = t / duration
            y_percent = 100 - (100 * progress)  # 100% -> 0%
            return ('center', f'{y_percent}%')
        clip = clip.with_position(position)

    elif effect == "pan_down":
        # Start from top (0%), pan to bottom (100%)
        def position(t):
            progress = t / duration
            y_percent = 100 * progress  # 0% -> 100%
            return ('center', f'{y_percent}%')
        clip = clip.with_position(position)

    elif effect == "zoom_in":
        clip = clip.resized(1 / ZOOM_RATIO)  # Reset to cover-fit
        def zoom_in_scale(t):
            progress = t / duration
            return 1.0 + (ZOOM_RATIO - 1.0) * progress
        clip = clip.resized(zoom_in_scale)
        clip = clip.with_position('center')

    elif effect == "zoom_out":
        clip = clip.resized(1 / ZOOM_RATIO)  # Reset to cover-fit
        def zoom_out_scale(t):
            progress = t / duration
            return ZOOM_RATIO - (ZOOM_RATIO - 1.0) * progress
        clip = clip.resized(zoom_out_scale)
        clip = clip.with_position('center')

    else:
        clip = clip.with_position('center')

    return clip


def assemble_video(
    voiceover_path: str,
    output_path: str,
    mode: str = "video",
    images_dir: str = None,
) -> str:
    """
    Assemble a vertical YouTube Short from voiceover and video clips or AI images.

    Args:
        voiceover_path: Path to the voiceover audio file
        output_path: Path to save the final video
        mode: "video" for video clips from assets, "images" for AI-generated images
        images_dir: Directory containing generated images (required for image mode)

    Returns:
        Path to the generated video
    """
    print(f"Starting video assembly (mode: {mode})...")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load voiceover to get duration
    print(f"  Loading voiceover: {voiceover_path}")
    voiceover = AudioFileClip(voiceover_path)
    total_duration = voiceover.duration
    print(f"  Duration: {total_duration:.1f}s")

    video_clips = []
    source_clips = {}  # For cleanup later

    if mode == "images":
        # ========== IMAGE MODE ==========
        if not images_dir:
            raise ValueError("images_dir is required for image mode")

        images = get_generated_images(images_dir)
        if not images:
            raise FileNotFoundError(f"No images found in {images_dir}")

        print(f"  Found {len(images)} generated image(s)")

        # Calculate duration per image
        image_duration = total_duration / len(images)
        print(f"  Duration per image: {image_duration:.1f}s")

        print(f"\n  Creating image clips with Ken Burns effects...")

        for i, image_path in enumerate(images, 1):
            effect = random.choice(EFFECTS)
            print(f"    Image {i}/{len(images)}: {image_path.name} [{effect}]")

            try:
                clip = ImageClip(str(image_path))
                clip = clip.with_duration(image_duration)
                clip = apply_ken_burns_vertical(clip, effect, image_duration)
                video_clips.append(clip)

            except Exception as e:
                print(f"      Error: {e}")
                # Fallback to black clip
                fallback = ColorClip(
                    size=RESOLUTION,
                    color=(0, 0, 0),
                    duration=image_duration,
                )
                video_clips.append(fallback)

        print(f"\n  Created {len(video_clips)} image clips")

    else:
        # ========== VIDEO MODE (existing logic) ==========
        # Get available videos
        available_videos = get_available_videos()
        if not available_videos:
            raise FileNotFoundError(f"No videos found in {ASSETS_DIR}")

        print(f"  Found {len(available_videos)} source video(s)")

        # Load all source videos
        for video_path in available_videos:
            clip = VideoFileClip(str(video_path))
            source_clips[str(video_path)] = clip
            print(f"    Loaded: {video_path.name} ({clip.duration:.1f}s)")

        video_paths = list(source_clips.keys())

        # Create fast cuts until we have enough duration
        print(f"\n  Creating fast cuts...")
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
