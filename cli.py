"""CLI workflow for YouTube script and voiceover generation."""

import os
import re
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def main():
    """Main interactive CLI workflow."""
    print_header()

    while True:
        # Step 1: Research multiple channels
        channels = get_channel_input()
        if not channels:
            print("No channels entered. Please try again.")
            continue

        all_videos = research_channels(channels)

        if all_videos.empty:
            print("\nNo videos found. Try different channels.")
            continue

        # Step 2: Display and select video
        display_videos(all_videos)
        selected = select_video(all_videos)

        if selected is None:
            continue  # User wants to search again

        # Step 3: Get transcript
        video_id = extract_video_id(selected["Video Link"])
        if not video_id:
            print("Could not extract video ID. Try another video.")
            continue

        transcript = fetch_transcript(video_id)

        if not transcript:
            print("Could not fetch transcript. Try another video.")
            continue

        # Step 4: Generate script
        script = generate_script_for_video(selected["Title"], transcript)
        save_script(script, selected["Title"])

        # Step 5: Generate voiceover (FINAL STEP)
        voiceover_path = generate_voiceover_for_script(script, selected["Title"])

        if voiceover_path:
            print(f"\n" + "=" * 50)
            print("✓ COMPLETE!")
            print(f"  Script: output/scripts/{sanitize_filename(selected['Title'])}.json")
            print(f"  Voiceover: {voiceover_path}")
            print("=" * 50)
        else:
            print("\nVoiceover generation failed.")

        if not ask_continue():
            break

    print("\nGoodbye!")


def print_header():
    """Print CLI header."""
    print("\n" + "=" * 50)
    print("     YouTube Script & Voiceover Generator")
    print("=" * 50 + "\n")


def sanitize_filename(title: str) -> str:
    """Create safe filename from title."""
    safe = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[-\s]+', '_', safe)[:50]


def get_channel_input() -> list:
    """Get channel names from user."""
    print("Step 1: Research Channels")
    print("-" * 25)
    channels_input = input("Enter channel names (comma-separated):\n> ")
    return [c.strip() for c in channels_input.split(",") if c.strip()]


def research_channels(channels: list) -> pd.DataFrame:
    """Research multiple channels and combine results."""
    from test import start

    print("\nResearching channels...")
    all_dfs = []

    for channel in channels:
        try:
            df = start(channel)
            if df is not None and not df.empty:
                df["Channel"] = channel  # Add channel column
                all_dfs.append(df)
                print(f"  ✓ {channel} ({len(df)} videos)")
            else:
                print(f"  ✗ {channel} - No videos found")
        except Exception as e:
            print(f"  ✗ {channel} - Error: {e}")

    if not all_dfs:
        return pd.DataFrame()

    # Combine and sort by virality
    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.sort_values("Virality Score", ascending=False)
    return combined


def display_videos(df: pd.DataFrame, top_n: int = 10):
    """Display top videos in a formatted table."""
    print(f"\nStep 2: Select a Video")
    print("-" * 25)
    print(f"Top {min(top_n, len(df))} videos by virality:\n")

    display_df = df.head(top_n).copy()
    display_df.index = range(1, len(display_df) + 1)

    # Format for display - truncate title
    display_df["Title Display"] = display_df["Title"].str[:40]

    # Select columns to display
    columns_to_show = ["Channel", "Title Display", "View Count", "Days Old", "Virality Score"]
    available_columns = [col for col in columns_to_show if col in display_df.columns]

    if available_columns:
        print(display_df[available_columns].to_string())
    else:
        # Fallback: show what we have
        print(display_df.to_string())


def select_video(df: pd.DataFrame) -> dict | None:
    """Let user select a video by number."""
    max_choice = min(10, len(df))

    while True:
        choice = input(f"\nEnter video number (1-{max_choice}), or 'q' to search again:\n> ")

        if choice.lower() == 'q':
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < max_choice:
                return df.iloc[idx].to_dict()
            print(f"Invalid number. Please enter 1-{max_choice}.")
        except ValueError:
            print("Please enter a number or 'q'.")


def extract_video_id(video_link: str) -> str | None:
    """Extract video ID from YouTube URL."""
    if not video_link:
        return None

    # Handle different YouTube URL formats
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


def fetch_transcript(video_id: str) -> str | None:
    """Fetch transcript for a video."""
    from video_content.getContent import get_transcript

    print(f"\nStep 3: Extract Transcript")
    print("-" * 25)
    print(f"Fetching transcript...")

    try:
        transcript = get_transcript(video_id)
        if transcript:
            word_count = len(transcript.split())
            print(f"✓ Transcript extracted ({word_count:,} words)")
            return transcript
        else:
            print("✗ No transcript available")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def generate_script_for_video(title: str, transcript: str) -> dict:
    """Generate script using AI."""
    from genScript.genScript import generate_script

    print(f"\nStep 4: Generate Script")
    print("-" * 25)
    print("Generating script with AI...")

    script = generate_script(title, transcript)

    print(f"✓ Script generated!")

    # Handle duration estimate
    duration = script.get('duration_estimate', 0)
    if duration:
        minutes = duration // 60
        print(f"  - Duration: ~{minutes} minutes")

    # Handle scenes
    scenes = script.get('scenes', [])
    print(f"  - Scenes: {len(scenes)}")

    return script


def save_script(script: dict, title: str) -> str:
    """Save script to JSON file."""
    os.makedirs("output/scripts", exist_ok=True)
    safe_title = sanitize_filename(title)
    filepath = f"output/scripts/{safe_title}.json"

    with open(filepath, 'w') as f:
        json.dump(script, f, indent=2)

    print(f"  Script saved to: {filepath}")
    return filepath


def generate_voiceover_for_script(script: dict, title: str) -> str | None:
    """Generate voiceover audio from script."""
    from voiceOver.genVoice import generate_full_voiceover

    print(f"\nStep 5: Generate Voiceover")
    print("-" * 25)
    print("Generating voiceover with ElevenLabs...")

    os.makedirs("output/voiceovers", exist_ok=True)
    safe_title = sanitize_filename(title)
    output_path = f"output/voiceovers/{safe_title}.mp3"

    try:
        result = generate_full_voiceover(script, output_path)
        if result:
            print(f"✓ Voiceover generated: {output_path}")
            return result
        print("✗ No script text found")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def ask_continue() -> bool:
    """Ask if user wants to continue."""
    choice = input("\nGenerate another script? (y/n): ")
    return choice.lower() == 'y'


if __name__ == "__main__":
    main()
