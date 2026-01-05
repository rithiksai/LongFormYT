#!/usr/bin/env python3
"""
YouTube Video Generation Pipeline

Complete end-to-end workflow:
1. Research YouTube channel for viral videos
2. Select a video from top performers
3. Fetch transcript
4. Generate script
5. Generate voiceover
6. Create final video

Usage:
    python run_pipeline.py
    python run_pipeline.py --channel "Channel Name"
    python run_pipeline.py --channel "Channel Name" --auto-select 1
"""

import os
import re
import json
import argparse
from datetime import datetime

# Import pipeline components
from test import start as research_channel
from video_content.getContent import get_transcript
from genScript.genScript import generate_script
from voiceOver.genVoice import generate_full_voiceover
from video_assembler.video_assembler import generate_video


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
        r'v=([^&]+)',           # Standard watch URL
        r'youtu\.be/([^?]+)',   # Short URL
        r'embed/([^?]+)',       # Embed URL
    ]

    for pattern in patterns:
        match = re.search(pattern, str(video_link))
        if match:
            return match.group(1)

    return None


def display_videos(df):
    """Display videos in a formatted table."""
    print("\n" + "=" * 80)
    print("  TOP VIRAL VIDEOS")
    print("=" * 80)

    # Sort by virality and take top 10
    df_sorted = df.sort_values("Virality Score", ascending=False).head(10)

    print(f"\n{'#':<3} {'Title':<45} {'Views':<12} {'Virality':<10}")
    print("-" * 80)

    for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
        title = row['Title'][:42] + "..." if len(row['Title']) > 45 else row['Title']
        views = f"{row['View Count']:,}"
        virality = f"{row['Virality Score']:,.0f}"
        print(f"{i:<3} {title:<45} {views:<12} {virality:<10}")

    print("-" * 80)
    return df_sorted


def select_video(df_sorted):
    """Let user select a video from the list."""
    while True:
        try:
            choice = input("\nSelect a video (1-10) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(df_sorted):
                selected = df_sorted.iloc[idx]
                print(f"\n  Selected: {selected['Title']}")
                return selected
            else:
                print("Invalid selection. Please enter 1-10.")
        except ValueError:
            print("Please enter a number.")


def run_pipeline(
    channel_name: str,
    output_dir: str = "output/pipeline",
    auto_select: int = None,
):
    """
    Run the complete video generation pipeline.

    Args:
        channel_name: YouTube channel name to research
        output_dir: Directory for all output files
        auto_select: Auto-select video by index (1-10) for non-interactive mode

    Returns:
        Path to the generated video
    """
    print("=" * 60)
    print("  VIDEO GENERATION PIPELINE")
    print("=" * 60)

    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/scripts", exist_ok=True)
    os.makedirs(f"{output_dir}/voiceovers", exist_ok=True)
    os.makedirs(f"{output_dir}/videos", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ========== STEP 1: Research Channel ==========
    print("\n" + "-" * 60)
    print("STEP 1: Researching Channel")
    print("-" * 60)
    print(f"Channel: {channel_name}")

    try:
        df = research_channel(channel_name)

        if df is None or df.empty:
            print("  No videos found for this channel")
            return None

        print(f"  Found {len(df)} videos")

    except Exception as e:
        print(f"  Research failed: {e}")
        raise

    # ========== STEP 2: Select Video ==========
    print("\n" + "-" * 60)
    print("STEP 2: Select Video")
    print("-" * 60)

    df_sorted = display_videos(df)

    if auto_select:
        # Auto-select for non-interactive mode
        if 1 <= auto_select <= len(df_sorted):
            selected = df_sorted.iloc[auto_select - 1]
            print(f"\n  Auto-selected #{auto_select}: {selected['Title']}")
        else:
            selected = df_sorted.iloc[0]
            print(f"\n  Auto-selected #1: {selected['Title']}")
    else:
        selected = select_video(df_sorted)

    if selected is None:
        print("No video selected. Exiting.")
        return None

    video_title = selected['Title']
    video_link = selected['Video Link']
    video_id = extract_video_id(video_link)

    print(f"  Video ID: {video_id}")

    # ========== STEP 3: Fetch Transcript ==========
    print("\n" + "-" * 60)
    print("STEP 3: Fetching Transcript")
    print("-" * 60)

    try:
        transcript = get_transcript(video_id)

        if not transcript:
            print("  No transcript available")
            return None

        word_count = len(transcript.split())
        print(f"  Transcript fetched ({word_count:,} words)")
        print(f"  Preview: {transcript[:100]}...")

    except Exception as e:
        print(f"  Transcript fetch failed: {e}")
        raise

    # ========== STEP 4: Generate Script ==========
    print("\n" + "-" * 60)
    print("STEP 4: Generating Script")
    print("-" * 60)

    slug = slugify(video_title)

    try:
        script_data = generate_script(video_title, transcript)
        script_path = f"{output_dir}/scripts/{slug}_{timestamp}.json"

        # Save script to file
        with open(script_path, "w") as f:
            json.dump(script_data, f, indent=2)

        print(f"  Script generated!")
        print(f"  - Duration estimate: {script_data.get('duration_estimate', 'N/A')}s")
        print(f"  - Number of scenes: {len(script_data.get('scenes', []))}")
        print(f"  - Saved to: {script_path}")

    except Exception as e:
        print(f"  Script generation failed: {e}")
        raise

    # ========== STEP 5: Generate Voiceover ==========
    print("\n" + "-" * 60)
    print("STEP 5: Generating Voiceover")
    print("-" * 60)

    voiceover_path = f"{output_dir}/voiceovers/{slug}_{timestamp}.mp3"

    try:
        result = generate_full_voiceover(script_data, voiceover_path)

        if result:
            print(f"  Voiceover generated!")
            print(f"  - Saved to: {voiceover_path}")
            file_size = os.path.getsize(voiceover_path) / (1024 * 1024)
            print(f"  - File size: {file_size:.2f} MB")
        else:
            print("  No narration found")
            raise ValueError("No narration to generate voiceover from")

    except Exception as e:
        print(f"  Voiceover generation failed: {e}")
        raise

    # ========== STEP 6: Generate Video ==========
    print("\n" + "-" * 60)
    print("STEP 6: Generating Video")
    print("-" * 60)

    video_path = f"{output_dir}/videos/{slug}_{timestamp}.mp4"

    try:
        print("  This may take a few minutes...\n")

        result = generate_video(
            script_data=script_data,
            voiceover_path=voiceover_path,
            output_path=video_path,
        )

        print(f"\n  Video generated!")
        print(f"  - Saved to: {video_path}")
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"  - File size: {file_size:.2f} MB")

    except Exception as e:
        print(f"  Video generation failed: {e}")
        raise

    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\nSource: {video_title}")
    print(f"\nGenerated files:")
    print(f"  1. Script:    {script_path}")
    print(f"  2. Voiceover: {voiceover_path}")
    print(f"  3. Video:     {video_path}")
    print("\n" + "=" * 60)

    return video_path


def main():
    parser = argparse.ArgumentParser(
        description="Complete video generation pipeline"
    )
    parser.add_argument(
        "--channel",
        type=str,
        default=None,
        help="YouTube channel name to research"
    )
    parser.add_argument(
        "--auto-select",
        type=int,
        default=None,
        help="Auto-select video by index (1-10) for non-interactive mode"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/pipeline",
        help="Output directory (default: output/pipeline)"
    )

    args = parser.parse_args()

    # Check for required environment variables
    required_vars = ["YOUTUBE_API_KEY", "GEMINI_API_KEY", "ELEVEN_LABS_API"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return

    # Check for videos in assets folder
    assets_dir = "assets/videos"
    if not os.path.exists(assets_dir) or not os.listdir(assets_dir):
        print(f"WARNING: No videos found in {assets_dir}/")
        print("Please add some MP4 videos to use as background clips.")
        return

    # Get channel name
    channel_name = args.channel
    if not channel_name:
        channel_name = input("Enter YouTube channel name: ").strip()
        if not channel_name:
            print("No channel name provided. Exiting.")
            return

    # Run the pipeline
    try:
        video_path = run_pipeline(
            channel_name=channel_name,
            output_dir=args.output_dir,
            auto_select=args.auto_select,
        )

        if video_path:
            print(f"\nSuccess! Watch your video at: {video_path}")

    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
