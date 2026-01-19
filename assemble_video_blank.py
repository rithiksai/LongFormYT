#!/usr/bin/env python3
"""Assemble video with blank black background from existing voiceover.

This script creates a simple video with a blank black background and your
pre-generated voiceover audio. Much faster than photo-based assembly.

Usage:
    python assemble_video_blank.py -v <voiceover.mp3> -o <output.mp4>

Example:
    python assemble_video_blank.py \\
        --voiceover output/pipeline/voiceovers/my_voiceover.mp3 \\
        --output output/final_video.mp4
"""



import sys
import os
import argparse
from pathlib import Path
from moviepy import ColorClip, AudioFileClip


def generate_blank_video(
    voiceover_path: str,
    output_path: str,
    resolution: tuple = (1920, 1080),
    background_color: tuple = (0, 0, 0),
) -> str:
    """Generate a video with blank background and voiceover audio.

    Args:
        voiceover_path: Path to voiceover MP3 file
        output_path: Where to save the output video
        resolution: Video resolution (default: 1920x1080)
        background_color: RGB color tuple (default: black)

    Returns:
        Path to the generated video file
    """
    print("Generating blank background video...")
    print(f"  Voiceover: {voiceover_path}")
    print(f"  Output: {output_path}")
    print(f"  Resolution: {resolution[0]}x{resolution[1]}")
    print(f"  Background: RGB{background_color}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load audio to get duration
    print("\nLoading audio...")
    audio = AudioFileClip(voiceover_path)
    duration = audio.duration
    print(f"  Duration: {duration:.1f}s ({duration/60:.1f} minutes)")

    # Create blank video clip
    print("\nCreating blank video clip...")
    video = ColorClip(
        size=resolution,
        color=background_color,
        duration=duration,
    )

    # Attach audio
    print("Attaching audio...")
    video = video.with_audio(audio)
    video = video.with_fps(30)

    # Render video
    print(f"\nRendering to {output_path}...")
    video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        audio_bitrate="192k",
        threads=4,
    )

    # Cleanup
    video.close()
    audio.close()

    print(f"\n✅ Done! Video saved to: {output_path}")
    return output_path


def main():
    """Main entry point for the blank video assembler."""
    parser = argparse.ArgumentParser(
        description="Assemble video with blank background from pre-generated voiceover",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (black background)
  python assemble_video_blank.py -v voiceover.mp3 -o output.mp4

  # With custom resolution
  python assemble_video_blank.py \\
      --voiceover output/pipeline/voiceovers/my_voiceover.mp3 \\
      --output output/final_video.mp4 \\
      --width 1280 \\
      --height 720

  # With custom color (dark gray instead of black)
  python assemble_video_blank.py \\
      -v voiceover.mp3 \\
      -o output.mp4 \\
      --color 50 50 50
        """
    )

    parser.add_argument(
        "-v", "--voiceover",
        required=True,
        help="Path to voiceover MP3 file"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path for output video file (MP4)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Video width in pixels (default: 1920)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Video height in pixels (default: 1080)"
    )
    parser.add_argument(
        "--color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        default=[0, 0, 0],
        help="Background color as RGB values 0-255 (default: 0 0 0 for black)"
    )

    args = parser.parse_args()

    # Convert to Path objects
    voiceover_path = Path(args.voiceover)
    output_path = args.output

    # Validate voiceover file exists
    print("Validating input files...")
    if not voiceover_path.exists():
        print(f"Error: Voiceover file not found: {voiceover_path}")
        sys.exit(1)

    # Validate color values
    for val in args.color:
        if not 0 <= val <= 255:
            print(f"Error: Color values must be between 0 and 255. Got: {args.color}")
            sys.exit(1)

    # Print configuration
    print("\nVideo Configuration:")
    print(f"  Voiceover: {voiceover_path}")
    print(f"  Output:    {output_path}")
    print(f"  Resolution: {args.width}x{args.height}")
    print(f"  Background: RGB{tuple(args.color)}")
    print()

    # Generate video
    try:
        result = generate_blank_video(
            voiceover_path=str(voiceover_path),
            output_path=output_path,
            resolution=(args.width, args.height),
            background_color=tuple(args.color),
        )

        print(f"\n✅ Video created successfully!")
        print(f"   Output: {result}")

    except Exception as e:
        print(f"\n❌ Error during video assembly: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
