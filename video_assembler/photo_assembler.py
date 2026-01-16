"""Photo slideshow video assembler with Ken Burns effects."""

import os
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut

# Video settings
RESOLUTION = (1920, 1080)
PHOTO_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

# Ken Burns effect settings (from moviepytest.py)
BASE_SCALE = 1.35  # Overscale to prevent black backgrounds during pan/zoom
ZOOM_INTENSITY = 0.20  # 20% zoom range

# Available Ken Burns effects (rotate through these)
EFFECTS = [
    "pan_right",
    "zoom_out",
    "zoom_in",
    "pan_left",
    "static"
]


def get_photos(photos_dir: str) -> list[Path]:
    """Get all photos from directory, sorted by filename.

    Args:
        photos_dir: Directory containing photos

    Returns:
        Sorted list of photo file paths
    """
    photos_path = Path(photos_dir)
    if not photos_path.exists():
        return []

    photos = []
    for ext in PHOTO_EXTENSIONS:
        photos.extend(photos_path.glob(f"*{ext}"))
        photos.extend(photos_path.glob(f"*{ext.upper()}"))

    return sorted(photos)


def apply_ken_burns(
    clip: ImageClip,
    effect: str,
    duration: float
) -> ImageClip:
    """Apply Ken Burns effect with automatic scaling to prevent black backgrounds.

    Args:
        clip: Image clip to animate
        effect: Effect type ('pan_right', 'zoom_in', 'zoom_out', 'pan_left', 'static')
        duration: Duration in seconds

    Returns:
        Animated clip with Ken Burns effect applied
    """
    if effect == "pan_right":
        # STEP 1: Define desired pan distance (one-way distance)
        pan_distance = 150  # pixels to pan in one direction

        # STEP 2: Calculate required scale to avoid black borders
        canvas_width, canvas_height = RESOLUTION
        image_width, image_height = clip.size

        # Required width after scaling
        required_width = canvas_width + (2 * pan_distance)

        # Scale factor must cover both width (for panning) and height (for aspect ratio)
        scale_factor = max(
            required_width / image_width,
            canvas_height / image_height
        )

        # STEP 3: Apply scaling
        scaled_clip = clip.resized(scale_factor).with_duration(duration)

        # STEP 4: Calculate safe pan boundaries
        scaled_width = image_width * scale_factor
        max_pan = (scaled_width - canvas_width) / 2

        # STEP 5: Pan from left to right
        # Camera pans right = image moves left to reveal right side
        # Use 90% of max_pan to avoid edge cases
        safe_pan = max_pan * 0.9
        positioned_clip = scaled_clip.with_position(
            lambda t: (safe_pan - (2 * safe_pan * t / duration), "center")
        )

        # Compose with explicit canvas size
        return CompositeVideoClip([positioned_clip], size=RESOLUTION).with_duration(duration)

    elif effect == "pan_left":
        # STEP 1: Define desired pan distance (one-way distance)
        pan_distance = 150  # pixels to pan in one direction

        # STEP 2: Calculate required scale to avoid black borders
        canvas_width, canvas_height = RESOLUTION
        image_width, image_height = clip.size

        # Required width after scaling
        required_width = canvas_width + (2 * pan_distance)

        # Scale factor must cover both width (for panning) and height (for aspect ratio)
        scale_factor = max(
            required_width / image_width,
            canvas_height / image_height
        )

        # STEP 3: Apply scaling
        scaled_clip = clip.resized(scale_factor).with_duration(duration)

        # STEP 4: Calculate safe pan boundaries
        scaled_width = image_width * scale_factor
        max_pan = (scaled_width - canvas_width) / 2

        # STEP 5: Pan from right to left
        # Camera pans left = image moves right to reveal left side
        # Use 90% of max_pan to avoid edge cases
        safe_pan = max_pan * 0.9
        positioned_clip = scaled_clip.with_position(
            lambda t: (-safe_pan + (2 * safe_pan * t / duration), "center")
        )

        # Compose with explicit canvas size
        return CompositeVideoClip([positioned_clip], size=RESOLUTION).with_duration(duration)

    elif effect == "zoom_in":
        # Zoom in from BASE_SCALE to BASE_SCALE + ZOOM_INTENSITY
        return (
            clip
            .with_duration(duration)
            .resized(lambda t: BASE_SCALE + (BASE_SCALE * ZOOM_INTENSITY * (t / duration)))
            .with_position("center")
        )

    elif effect == "zoom_out":
        # Zoom out from BASE_SCALE + ZOOM_INTENSITY to BASE_SCALE
        # Ensures we never go below BASE_SCALE (always > 1.0)
        return (
            clip
            .with_duration(duration)
            .resized(lambda t: BASE_SCALE + (BASE_SCALE * ZOOM_INTENSITY * (1 - t / duration)))
            .with_position("center")
        )

    else:  # "static" or default
        # No animation, just centered
        return (
            clip
            .resized(BASE_SCALE)
            .with_duration(duration)
            .with_position("center")
        )


def generate_photo_video(
    script_data: dict,
    voiceover_path: str,
    output_path: str,
    photos_dir: str = None,
) -> str:
    """Generate video from photos with Ken Burns effects and voiceover.

    Args:
        script_data: Script JSON with 'scenes' array
        voiceover_path: Path to voiceover MP3 file
        output_path: Where to save final video
        photos_dir: Directory with photos (default: assets/photos)

    Returns:
        Path to generated video file
    """
    print("\nGenerating photo slideshow video with Ken Burns effects...")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Set photos directory
    if photos_dir is None:
        photos_dir = Path(__file__).parent.parent / "assets" / "photos"

    # Load voiceover to get total duration
    print(f"  Loading voiceover: {voiceover_path}")
    voiceover = AudioFileClip(voiceover_path)
    total_duration = voiceover.duration
    print(f"  Duration: {total_duration:.1f}s")

    # Get scenes from script
    scenes = script_data.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes found in script data")

    num_scenes = len(scenes)
    scene_duration = total_duration / num_scenes

    print(f"  Scenes: {num_scenes}")
    print(f"  Duration per scene: {scene_duration:.2f}s")

    # Get photos
    photos = get_photos(str(photos_dir))
    if not photos:
        raise FileNotFoundError(
            f"No photos found in {photos_dir}. "
            f"Please add image files ({', '.join(PHOTO_EXTENSIONS)})."
        )

    print(f"  Photos available: {len(photos)}")
    print()

    # Create clips for each scene
    video_clips = []

    for i, scene in enumerate(scenes):
        # Cycle through photos if we have more scenes than photos
        photo_idx = i % len(photos)
        photo_path = photos[photo_idx]

        # Rotate through Ken Burns effects
        effect = EFFECTS[i % len(EFFECTS)]

        print(f"  Scene {i + 1}/{num_scenes}: {photo_path.name} [{effect}] ({scene_duration:.2f}s)")

        try:
            # Create image clip
            clip = ImageClip(str(photo_path))

            # Apply Ken Burns effect
            clip = apply_ken_burns(clip, effect, scene_duration)

            video_clips.append(clip)

        except Exception as e:
            print(f"    Error creating clip: {e}")
            # Create black fallback clip
            fallback = ColorClip(
                size=RESOLUTION,
                color=(0, 0, 0),
                duration=scene_duration
            )
            video_clips.append(fallback)

    # Concatenate all clips
    print("\nConcatenating clips...")

    # Ensure all clips have the same FPS
    for i, clip in enumerate(video_clips):
        video_clips[i] = clip.with_fps(30)

    final_video = concatenate_videoclips(video_clips, method="compose")

    # Add fade in/out effects
    final_video = final_video.with_effects([
        FadeIn(0.5),
        FadeOut(0.5)
    ])

    # Attach voiceover
    print("Attaching voiceover...")
    final_video = final_video.with_audio(voiceover)

    # Render final video
    print(f"Rendering to {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        audio_bitrate="192k",
        threads=4
    )

    # Cleanup
    final_video.close()
    voiceover.close()
    for clip in video_clips:
        clip.close()

    print(f"\nDone! Video saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test with existing assets
    import json

    # Find a test script
    script_dir = Path(__file__).parent.parent / "output" / "pipeline" / "scripts"
    if script_dir.exists():
        scripts = list(script_dir.glob("*.json"))
        if scripts:
            with open(scripts[0]) as f:
                test_script = json.load(f)

            voiceover_path = scripts[0].parent.parent / "voiceovers" / f"{scripts[0].stem}.mp3"

            if voiceover_path.exists():
                print("Testing photo_assembler...")
                result = generate_photo_video(
                    script_data=test_script,
                    voiceover_path=str(voiceover_path),
                    output_path="output/test_photo_assembler.mp4"
                )
                print(f"Test successful: {result}")
            else:
                print("No matching voiceover found")
        else:
            print("No test scripts found")
    else:
        print("Script directory not found")
