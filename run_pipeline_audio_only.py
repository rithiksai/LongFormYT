#!/usr/bin/env python3
"""
YouTube Video Generation Pipeline - Audio Only (Blank Background)

Generates complete video with script and voiceover, but uses a blank background
instead of photos. Faster than the full photo-based pipeline.

Workflow:
1. Research YouTube channel OR use direct title input
2. Generate script (with or without transcript)
3. Generate voiceover
4. Create video with blank background + voiceover audio

Usage:
    python run_pipeline_audio_only.py
    python run_pipeline_audio_only.py --mode direct --title "Your Title"
    python run_pipeline_audio_only.py --mode research --channel "Channel Name"
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    VideoUnavailable,
    NoTranscriptFound,
)

# Import pipeline components
from youtube_research import start as research_channel
from video_content.getContent import get_transcript
from genScript.genScript import generate_script
from voiceOver.genVoice import generate_full_voiceover

# Import MoviePy for blank video generation
from moviepy import ColorClip, AudioFileClip


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text[:50]


def extract_video_id(video_link: str) -> str:
    """Extract video ID from YouTube URL."""
    if not video_link:
        return None

    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$',
    ]

    for pattern in patterns:
        match = re.search(pattern, video_link)
        if match:
            return match.group(1)

    return None


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

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load audio to get duration
    audio = AudioFileClip(voiceover_path)
    duration = audio.duration
    print(f"  Duration: {duration:.1f}s")

    # Create blank video clip
    video = ColorClip(
        size=resolution,
        color=background_color,
        duration=duration,
    )

    # Attach audio
    video = video.with_audio(audio)
    video = video.with_fps(30)

    # Render video
    print("Rendering video...")
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

    print(f"Done! Video saved to: {output_path}")
    return output_path


def run_pipeline_direct(title: str, output_dir: str = "output/pipeline") -> str:
    """Run pipeline in direct mode (title only, no transcript).

    Args:
        title: Video title to generate script from
        output_dir: Base output directory

    Returns:
        Path to generated video file, or None if failed
    """
    print("\n" + "=" * 60)
    print("  DIRECT MODE - AUDIO ONLY PIPELINE")
    print("=" * 60)
    print(f"Title: {title}")
    print()

    # Create output directories
    base_dir = Path(output_dir)
    script_dir = base_dir / "scripts"
    voiceover_dir = base_dir / "voiceovers"
    video_dir = base_dir / "videos"

    for d in [script_dir, voiceover_dir, video_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Generate filename-safe slug
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(title)
    base_filename = f"{slug}_{timestamp}"

    # Step 1: Generate script (no transcript)
    print("=" * 60)
    print("STEP 1: Generating Script")
    print("=" * 60)

    try:
        script_data = generate_script(title, "")  # Empty transcript
        print(f"  ✓ Script generated successfully")
        print(f"    - Scenes: {len(script_data.get('scenes', []))}")
        print(f"    - Duration estimate: {script_data.get('duration_estimate', 0)}s")
    except Exception as e:
        print(f"  ✗ Script generation failed: {e}")
        return None

    # Save script to JSON
    script_path = script_dir / f"{base_filename}.json"
    with open(script_path, "w") as f:
        json.dump(script_data, f, indent=2)
    print(f"  ✓ Script saved: {script_path}")

    # Step 2: Generate voiceover
    print("\n" + "=" * 60)
    print("STEP 2: Generating Voiceover")
    print("=" * 60)

    voiceover_path = voiceover_dir / f"{base_filename}.mp3"

    try:
        result = generate_full_voiceover(script_data, str(voiceover_path))
        print(f"  ✓ Voiceover generated: {result}")
    except Exception as e:
        print(f"  ✗ Voiceover generation failed: {e}")
        return None

    # Step 3: Generate blank video with audio
    print("\n" + "=" * 60)
    print("STEP 3: Generating Video (Blank Background)")
    print("=" * 60)

    video_path = video_dir / f"{base_filename}.mp4"

    try:
        result = generate_blank_video(
            voiceover_path=str(voiceover_path),
            output_path=str(video_path),
        )
        print(f"  ✓ Video generated: {result}")
    except Exception as e:
        print(f"  ✗ Video generation failed: {e}")
        return None

    return str(video_path)


def run_pipeline_research(
    channel_name: str,
    output_dir: str = "output/pipeline",
    auto_select: int = None,
) -> str:
    """Run pipeline in research mode (with channel research, optional transcript).

    Args:
        channel_name: YouTube channel name to research
        output_dir: Base output directory
        auto_select: Auto-select video by index (1-based), or None for interactive

    Returns:
        Path to generated video file, or None if failed
    """
    print("\n" + "=" * 60)
    print("  RESEARCH MODE - AUDIO ONLY PIPELINE")
    print("=" * 60)
    print(f"Channel: {channel_name}")
    print()

    # Create output directories
    base_dir = Path(output_dir)
    script_dir = base_dir / "scripts"
    voiceover_dir = base_dir / "voiceovers"
    video_dir = base_dir / "videos"

    for d in [script_dir, voiceover_dir, video_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Step 1: Research channel
    print("=" * 60)
    print("STEP 1: Researching Channel")
    print("=" * 60)

    try:
        videos = research_channel(channel_name)
        if not videos:
            print("  ✗ No videos found or analysis failed")
            return None
        print(f"  ✓ Found {len(videos)} videos")
    except Exception as e:
        print(f"  ✗ Channel research failed: {e}")
        return None

    # Step 2: Select video
    print("\n" + "=" * 60)
    print("STEP 2: Selecting Video")
    print("=" * 60)

    if auto_select:
        selected_idx = auto_select - 1
        if selected_idx < 0 or selected_idx >= len(videos):
            print(f"  ✗ Invalid auto-select index: {auto_select}")
            return None
        selected_video = videos[selected_idx]
        print(f"  Auto-selected video {auto_select}: {selected_video.get('title', 'Unknown')}")
    else:
        print("\nSelect a video to generate content from:")
        for i, video in enumerate(videos, 1):
            print(f"  {i}. {video.get('title', 'Unknown')} ({video.get('views', 'N/A')} views)")

        while True:
            try:
                choice = int(input("\nEnter video number: "))
                if 1 <= choice <= len(videos):
                    selected_video = videos[choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(videos)}")
            except ValueError:
                print("Please enter a valid number")

    title = selected_video.get("title", "Unknown Title")
    video_link = selected_video.get("link", "")
    video_id = extract_video_id(video_link)

    print(f"  ✓ Selected: {title}")

    # Step 3: Fetch transcript (with error handling)
    print("\n" + "=" * 60)
    print("STEP 3: Fetching Transcript")
    print("=" * 60)

    transcript = ""
    if video_id:
        for attempt in range(3):
            try:
                transcript = get_transcript(video_id)
                print(f"  ✓ Transcript fetched: {len(transcript)} chars")
                break
            except TranscriptsDisabled as e:
                print(f"  ❌ Transcript Error: Subtitles are disabled for this video")
                if auto_select:
                    print("  Auto-select mode: cannot retry. Exiting.")
                    return None
                response = input("\n  No transcript found. Continue without transcript? (yes/no/retry): ").strip().lower()
                if response in ['yes', 'y']:
                    print("  Continuing without transcript...")
                    transcript = ""
                    break
                elif response in ['retry', 'r']:
                    continue
                else:
                    print("Exiting pipeline.")
                    return None
            except VideoUnavailable as e:
                print(f"  ❌ Video Error: Video is unavailable")
                if auto_select:
                    print("  Auto-select mode: cannot retry. Exiting.")
                    return None
                response = input("\n  No transcript found. Continue without transcript? (yes/no/retry): ").strip().lower()
                if response in ['yes', 'y']:
                    print("  Continuing without transcript...")
                    transcript = ""
                    break
                elif response in ['retry', 'r']:
                    continue
                else:
                    print("Exiting pipeline.")
                    return None
            except NoTranscriptFound as e:
                print(f"  ❌ Transcript Error: No transcript found for this video")
                if auto_select:
                    print("  Auto-select mode: cannot retry. Exiting.")
                    return None
                response = input("\n  No transcript found. Continue without transcript? (yes/no/retry): ").strip().lower()
                if response in ['yes', 'y']:
                    print("  Continuing without transcript...")
                    transcript = ""
                    break
                elif response in ['retry', 'r']:
                    continue
                else:
                    print("Exiting pipeline.")
                    return None
            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")
                if auto_select:
                    print("  Auto-select mode: cannot retry. Exiting.")
                    return None
                response = input("\n  No transcript found. Continue without transcript? (yes/no/retry): ").strip().lower()
                if response in ['yes', 'y']:
                    print("  Continuing without transcript...")
                    transcript = ""
                    break
                elif response in ['retry', 'r']:
                    continue
                else:
                    print("Exiting pipeline.")
                    return None
    else:
        print("  ✗ Could not extract video ID from link")
        response = input("\n  Continue without transcript? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Exiting pipeline.")
            return None

    # Generate filename-safe slug
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(title)
    base_filename = f"{slug}_{timestamp}"

    # Step 4: Generate script
    print("\n" + "=" * 60)
    print("STEP 4: Generating Script")
    print("=" * 60)

    try:
        script_data = generate_script(title, transcript)
        print(f"  ✓ Script generated successfully")
        print(f"    - Scenes: {len(script_data.get('scenes', []))}")
        print(f"    - Duration estimate: {script_data.get('duration_estimate', 0)}s")
    except Exception as e:
        print(f"  ✗ Script generation failed: {e}")
        return None

    # Save script to JSON
    script_path = script_dir / f"{base_filename}.json"
    with open(script_path, "w") as f:
        json.dump(script_data, f, indent=2)
    print(f"  ✓ Script saved: {script_path}")

    # Step 5: Generate voiceover
    print("\n" + "=" * 60)
    print("STEP 5: Generating Voiceover")
    print("=" * 60)

    voiceover_path = voiceover_dir / f"{base_filename}.mp3"

    try:
        result = generate_full_voiceover(script_data, str(voiceover_path))
        print(f"  ✓ Voiceover generated: {result}")
    except Exception as e:
        print(f"  ✗ Voiceover generation failed: {e}")
        return None

    # Step 6: Generate blank video with audio
    print("\n" + "=" * 60)
    print("STEP 6: Generating Video (Blank Background)")
    print("=" * 60)

    video_path = video_dir / f"{base_filename}.mp4"

    try:
        result = generate_blank_video(
            voiceover_path=str(voiceover_path),
            output_path=str(video_path),
        )
        print(f"  ✓ Video generated: {result}")
    except Exception as e:
        print(f"  ✗ Video generation failed: {e}")
        return None

    return str(video_path)


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="YouTube AI Video Generator - Audio Only (Blank Background)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (choose between direct and research)
  python run_pipeline_audio_only.py

  # Direct mode with title
  python run_pipeline_audio_only.py --mode direct --title "Your Video Title"

  # Research mode with channel
  python run_pipeline_audio_only.py --mode research --channel "Channel Name"

  # Research mode with auto-select
  python run_pipeline_audio_only.py --mode research --channel "Channel Name" --auto-select 1
        """
    )

    parser.add_argument(
        "--mode",
        choices=["direct", "research"],
        help="Pipeline mode: 'direct' (title only) or 'research' (channel analysis)"
    )
    parser.add_argument(
        "--title",
        help="Video title (for direct mode)"
    )
    parser.add_argument(
        "--channel",
        help="YouTube channel name to analyze (for research mode)"
    )
    parser.add_argument(
        "--auto-select",
        type=int,
        help="Auto-select video by number (1-based index) instead of prompting"
    )
    parser.add_argument(
        "--output-dir",
        default="output/pipeline",
        help="Base output directory for generated files"
    )

    args = parser.parse_args()

    # Check environment variables
    required_vars = ["GEMINI_API_KEY", "CLAUDE_API_KEY", "ELEVEN_LABS_API"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return

    # Determine mode
    mode = args.mode
    if not mode:
        # Interactive mode selection
        print("=" * 60)
        print("  YOUTUBE AI VIDEO GENERATOR - AUDIO ONLY")
        print("=" * 60)
        print("\nSelect pipeline mode:")
        print("  1. Direct Mode - Generate from title only (no transcript needed)")
        print("  2. Research Mode - Research channel and use transcript if available")

        while True:
            choice = input("\nEnter mode (1 or 2): ").strip()
            if choice == "1":
                mode = "direct"
                break
            elif choice == "2":
                mode = "research"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

    # Execute based on mode
    if mode == "direct":
        # Direct mode: Get title and generate
        title = args.title
        if not title:
            title = input("\nEnter video title: ").strip()
            if not title:
                print("No title provided. Exiting.")
                return

        # Run direct pipeline
        try:
            video_path = run_pipeline_direct(
                title=title,
                output_dir=args.output_dir,
            )

            if video_path:
                print(f"\n✅ Success! Watch your video at: {video_path}")

        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            import traceback
            traceback.print_exc()

    elif mode == "research":
        # Research mode
        channel_name = args.channel
        if not channel_name:
            channel_name = input("\nEnter YouTube channel name: ").strip()
            if not channel_name:
                print("No channel name provided. Exiting.")
                return

        # Run research pipeline
        try:
            video_path = run_pipeline_research(
                channel_name=channel_name,
                output_dir=args.output_dir,
                auto_select=args.auto_select,
            )

            if video_path:
                print(f"\n✅ Success! Watch your video at: {video_path}")

        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
