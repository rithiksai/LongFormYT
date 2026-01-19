#!/usr/bin/env python3
"""
YouTube Shorts Generation Pipeline

Generate a ~30 second vertical video from just a title.

Usage:
    python run_pipeline.py                              # Interactive mode
    python run_pipeline.py --title "Your Short Title"   # Direct title mode
"""

import os
import re
import argparse
from datetime import datetime

from gen_script import generate_script
from gen_voice import generate_voiceover
from gen_images import generate_images_for_short
from video_assembler import assemble_video, get_available_videos, ASSETS_DIR
from research_shorts import research_channel, display_shorts, select_short


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text[:30]


def run_pipeline(title: str, output_dir: str = "output", mode: str = "video") -> str:
    """
    Run the complete YouTube Shorts generation pipeline.

    Args:
        title: The topic/title for the short
        output_dir: Directory for output files
        mode: "video" for video clips, "images" for AI-generated images

    Returns:
        Path to the generated video
    """
    print("=" * 50)
    print("  YOUTUBE SHORTS PIPELINE")
    print("=" * 50)
    print(f"\nTitle: {title}")
    print(f"Mode: {mode}")

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(title)

    # ========== STEP 1: Generate Script ==========
    print("\n" + "-" * 50)
    print(f"STEP 1: Generating Script")
    print("-" * 50)

    include_visuals = (mode == "images")

    try:
        script_data = generate_script(title, include_visuals=include_visuals)
        print(f"  Hook: {script_data['hook'][:50]}...")
        print(f"  Duration estimate: {script_data['duration_estimate']}s")
        print(f"  Word count: {len(script_data['narration'].split())} words")
        if include_visuals:
            print(f"  Visual suggestions: {len(script_data.get('visual_suggestions', []))}")
    except Exception as e:
        print(f"  Script generation failed: {e}")
        raise

    # ========== STEP 2: Generate Voiceover ==========
    print("\n" + "-" * 50)
    print("STEP 2: Generating Voiceover")
    print("-" * 50)

    voiceover_path = f"{output_dir}/{slug}_{timestamp}_voice.mp3"

    try:
        generate_voiceover(script_data["narration"], voiceover_path)
        file_size = os.path.getsize(voiceover_path) / 1024
        print(f"  File size: {file_size:.1f} KB")
    except Exception as e:
        print(f"  Voiceover generation failed: {e}")
        raise

    # ========== STEP 2.5: Generate Images (if image mode) ==========
    images_dir = None
    if mode == "images":
        print("\n" + "-" * 50)
        print("STEP 2.5: Generating AI Images")
        print("-" * 50)

        images_dir = f"{output_dir}/{slug}_{timestamp}_images"
        visual_suggestions = script_data.get("visual_suggestions", [])

        if not visual_suggestions:
            print("  ERROR: No visual suggestions in script data")
            raise ValueError("No visual suggestions generated for image mode")

        try:
            image_paths = generate_images_for_short(
                visual_suggestions,
                output_dir=images_dir,
            )
            print(f"  Generated {len(image_paths)} images")
        except Exception as e:
            print(f"  Image generation failed: {e}")
            raise

    # ========== STEP 3: Assemble Video ==========
    print("\n" + "-" * 50)
    print("STEP 3: Assembling Video")
    print("-" * 50)

    video_path = f"{output_dir}/{slug}_{timestamp}.mp4"

    try:
        assemble_video(
            voiceover_path,
            video_path,
            mode=mode,
            images_dir=images_dir,
        )
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"  File size: {file_size:.2f} MB")
    except Exception as e:
        print(f"  Video assembly failed: {e}")
        raise

    # ========== SUMMARY ==========
    print("\n" + "=" * 50)
    print("  PIPELINE COMPLETE!")
    print("=" * 50)
    print(f"\nTitle: {title}")
    print(f"Mode: {mode}")
    print(f"\nGenerated files:")
    print(f"  1. Voiceover: {voiceover_path}")
    if images_dir:
        print(f"  2. Images:    {images_dir}/")
        print(f"  3. Video:     {video_path}")
    else:
        print(f"  2. Video:     {video_path}")
    print("\n" + "=" * 50)

    return video_path


def get_mode_interactive() -> str:
    """Get visual mode through interactive menu."""
    print("\nSelect visual mode:")
    print("  1. Video clips (random cuts from assets/videos)")
    print("  2. AI-generated images (Stability.AI)")

    while True:
        choice = input("\nSelect option (1/2): ").strip()
        if choice == '1':
            return "video"
        elif choice == '2':
            return "images"
        print("Invalid option. Please enter 1 or 2.")


def get_title_interactive():
    """Get title through interactive menu."""
    print("\n" + "=" * 50)
    print("  YOUTUBE SHORTS GENERATOR")
    print("=" * 50)
    print("\nHow would you like to provide the title?")
    print("  1. Enter title manually")
    print("  2. Research a YouTube channel for shorts")
    print("  q. Quit")

    while True:
        choice = input("\nSelect option (1/2/q): ").strip().lower()

        if choice == 'q':
            return None

        if choice == '1':
            title = input("\nEnter the title for your short: ").strip()
            if title:
                return title
            print("Title cannot be empty.")

        elif choice == '2':
            channel_name = input("\nEnter YouTube channel name: ").strip()
            if not channel_name:
                print("Channel name cannot be empty.")
                continue

            try:
                print()
                df = research_channel(channel_name)
                if df.empty:
                    print("No shorts found. Try another channel.")
                    continue

                df_display = display_shorts(df)
                title = select_short(df_display)
                if title:
                    return title
            except Exception as e:
                print(f"Error researching channel: {e}")
                continue

        else:
            print("Invalid option. Please enter 1, 2, or q.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube Shorts from a title"
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="The topic/title for the short (optional - will prompt if not provided)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["video", "images"],
        default=None,
        help="Visual mode: 'video' for video clips, 'images' for AI-generated images (default: prompt)"
    )

    args = parser.parse_args()

    # Check for required environment variables
    required_vars = ["CLAUDE_API_KEY", "ELEVEN_LABS_API"]

    # Add STABILITY_API_KEY if image mode is specified via CLI
    if args.mode == "images":
        required_vars.append("STABILITY_API_KEY")

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return

    # Get title - either from args or interactive menu
    if args.title:
        title = args.title
    else:
        title = get_title_interactive()
        if not title:
            print("No title provided. Exiting.")
            return

    # Get mode - either from args or interactive menu
    if args.mode:
        mode = args.mode
    else:
        mode = get_mode_interactive()

    # Check for STABILITY_API_KEY if image mode was selected interactively
    if mode == "images" and not os.environ.get("STABILITY_API_KEY"):
        print("ERROR: Missing STABILITY_API_KEY environment variable")
        print("This is required for AI image generation mode.")
        print("\nPlease set it in your .env file or environment.")
        return

    # Check for videos in assets folder (only needed for video mode)
    if mode == "video":
        available_videos = get_available_videos()
        if not available_videos:
            print(f"ERROR: No videos found in {ASSETS_DIR}")
            print("Please add video files to use as background clips.")
            return
        print(f"Found {len(available_videos)} video(s) in assets folder")
    else:
        print("AI image mode selected - images will be generated via Stability.AI")

    # Run the pipeline
    try:
        video_path = run_pipeline(
            title=title,
            output_dir=args.output_dir,
            mode=mode,
        )
        print(f"\nSuccess! Watch your Short at: {video_path}")

    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
