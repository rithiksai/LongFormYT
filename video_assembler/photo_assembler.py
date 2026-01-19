"""Photo slideshow video assembler with Ken Burns panning effects."""

import os
import random
from pathlib import Path

from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    ColorClip,
    CompositeVideoClip,
)
from moviepy.video.fx import FadeIn, FadeOut

from .config import DEFAULT_CONFIG, ensure_directories

# Video settings
RESOLUTION = (1920, 1080)
PHOTO_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

# Ken Burns effect settings
ZOOM_RATIO = 1.15  # How much larger than frame (15% zoom margin)

# Available panning effects
EFFECTS = [
    "pan_left",
    "pan_right",
    "pan_up",
    "pan_down",
    "zoom_in",
    "zoom_out",
]


def resize_cover(clip, target_w: int, target_h: int):
    """
    Resize image to cover target dimensions (like CSS object-fit: cover).

    The image is scaled so the shorter dimension fills the target,
    and the longer dimension overflows (will be cropped by positioning).
    """
    img_w, img_h = clip.size
    scale = max(target_w / img_w, target_h / img_h)
    return clip.resized(scale)


def get_photos(photos_dir: str) -> list[Path]:
    """Get all photos from directory, sorted by filename."""
    photos_path = Path(photos_dir)
    if not photos_path.exists():
        return []

    photos = []
    for ext in PHOTO_EXTENSIONS:
        photos.extend(photos_path.glob(f"*{ext}"))
        photos.extend(photos_path.glob(f"*{ext.upper()}"))

    return sorted(photos)


def apply_ken_burns(clip: ImageClip, effect: str, duration: float) -> ImageClip:
    """
    Apply Ken Burns panning/zoom effect to an image clip.

    Args:
        clip: The image clip to animate
        effect: One of EFFECTS
        duration: Duration of the clip in seconds

    Returns:
        Animated clip with Ken Burns effect
    """
    w, h = RESOLUTION

    # First apply cover-fit, then scale up for panning room
    clip = resize_cover(clip, w, h)
    clip = clip.resized(ZOOM_RATIO)  # Add margin for panning
    img_w, img_h = clip.size

    # Calculate movement range (how much we can pan)
    x_margin = (img_w - w) // 2
    y_margin = (img_h - h) // 2

    # Center offset (to center the image in the frame)
    center_x = -x_margin
    center_y = -y_margin

    if effect == "pan_left":
        # Start from right, pan to left
        def position(t):
            progress = t / duration
            x = x_margin - (2 * x_margin * progress)
            return (x, center_y)
        clip = clip.with_position(position)

    elif effect == "pan_right":
        # Start from left, pan to right
        def position(t):
            progress = t / duration
            x = -x_margin + (2 * x_margin * progress)
            return (x, center_y)
        clip = clip.with_position(position)

    elif effect == "pan_up":
        # Start from bottom, pan to top
        def position(t):
            progress = t / duration
            y = y_margin - (2 * y_margin * progress)
            return (center_x, y)
        clip = clip.with_position(position)

    elif effect == "pan_down":
        # Start from top, pan to bottom
        def position(t):
            progress = t / duration
            y = -y_margin + (2 * y_margin * progress)
            return (center_x, y)
        clip = clip.with_position(position)

    elif effect == "zoom_in":
        # Start at cover-fit (1.0), zoom in to ZOOM_RATIO
        # Reset to cover-fit size first
        clip = clip.resized(1 / ZOOM_RATIO)

        def zoom_in_scale(t):
            progress = t / duration
            return 1.0 + (ZOOM_RATIO - 1.0) * progress

        clip = clip.resized(zoom_in_scale)
        clip = clip.with_position('center')

    elif effect == "zoom_out":
        # Start zoomed in at ZOOM_RATIO, zoom out to cover-fit (1.0)
        # Reset to cover-fit size first
        clip = clip.resized(1 / ZOOM_RATIO)

        def zoom_out_scale(t):
            progress = t / duration
            return ZOOM_RATIO - (ZOOM_RATIO - 1.0) * progress

        clip = clip.resized(zoom_out_scale)
        clip = clip.with_position('center')

    else:
        # Default: center position
        clip = clip.with_position('center')

    return clip


def generate_photo_video(
    script_data: dict,
    voiceover_path: str,
    output_path: str,
    photos_dir: str = None,
) -> str:
    """
    Generate a video from photos with Ken Burns effects.

    Args:
        script_data: Script JSON with scenes
        voiceover_path: Path to voiceover audio file
        output_path: Where to save final video
        photos_dir: Directory containing photos (default: assets/photos)

    Returns:
        Path to the generated video file
    """
    print("Starting photo slideshow generation...")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ensure_directories()

    # Set photos directory
    if photos_dir is None:
        photos_dir = Path(__file__).parent.parent / "assets" / "photos"

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

    # Get photos
    photos = get_photos(photos_dir)
    if not photos:
        raise FileNotFoundError(
            f"No photos found in {photos_dir}. "
            f"Please add image files ({', '.join(PHOTO_EXTENSIONS)})."
        )

    print(f"\nFound {len(photos)} photos")
    print(f"Processing {total_scenes} scenes ({scene_duration:.1f}s each)...")

    # Create clips for each scene
    video_clips = []

    for i, scene in enumerate(scenes):
        # Cycle through photos if we have more scenes than photos
        photo_idx = i % len(photos)
        photo_path = photos[photo_idx]

        # Random effect for this photo
        effect = random.choice(EFFECTS)

        print(f"  Scene {i + 1}/{total_scenes}: {photo_path.name} [{effect}]")

        try:
            # Create image clip
            clip = ImageClip(str(photo_path))
            clip = clip.with_duration(scene_duration)

            # Apply Ken Burns effect
            clip = apply_ken_burns(clip, effect, scene_duration)

            video_clips.append(clip)

        except Exception as e:
            print(f"    Error: {e}")
            # Create black clip as fallback
            fallback = ColorClip(
                size=RESOLUTION,
                color=(0, 0, 0),
                duration=scene_duration,
            )
            video_clips.append(fallback)

    # Concatenate all clips
    print("\nConcatenating clips...")

    # Composite each clip onto a canvas of RESOLUTION size
    # This preserves Ken Burns positioning while ensuring correct output dimensions
    composited_clips = []
    for i, clip in enumerate(video_clips):
        if clip.size != RESOLUTION:
            # Create a black background canvas
            background = ColorClip(
                size=RESOLUTION,
                color=(0, 0, 0),
                duration=clip.duration,
            )
            # Composite the positioned clip onto the background
            composited = CompositeVideoClip([background, clip], size=RESOLUTION)
            composited = composited.with_fps(30)
            composited_clips.append(composited)
        else:
            composited_clips.append(clip.with_fps(30))
    video_clips = composited_clips

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
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        audio_bitrate="192k",
        threads=4,
    )

    # Cleanup
    final_video.close()
    voiceover.close()
    for clip in video_clips:
        clip.close()

    print(f"\nDone! Video saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test
    photos_dir = Path(__file__).parent.parent / "assets" / "photos"
    print(f"Photos directory: {photos_dir}")
    photos = get_photos(photos_dir)
    print(f"Found {len(photos)} photos: {[p.name for p in photos]}")
