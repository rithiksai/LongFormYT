#!/usr/bin/env python3
"""
Test Video Generation

Uses existing script and voiceover files to test video generation
without using voice credits.

Usage:
    python test_video.py
"""

import os
import json
from datetime import datetime

from video_assembler import generate_video


# Existing assets (edit these paths if needed)
SCRIPT_PATH = "output/test_pipeline/scripts/what_if_tanjiro_was_reborn_with_his_memories_20260104_234023.json"
VOICEOVER_PATH = "output/test_pipeline/voiceovers/what_if_tanjiro_was_reborn_with_his_memories_20260104_234023.mp3"

# Output directory
OUTPUT_DIR = "output/test_videos"


def main():
    print("=" * 50)
    print("  VIDEO GENERATION TEST")
    print("=" * 50)

    # Check files exist
    if not os.path.exists(SCRIPT_PATH):
        print(f"Script not found: {SCRIPT_PATH}")
        return

    if not os.path.exists(VOICEOVER_PATH):
        print(f"Voiceover not found: {VOICEOVER_PATH}")
        return

    # Check assets folder
    assets_dir = "assets/videos"
    if not os.path.exists(assets_dir) or not os.listdir(assets_dir):
        print(f"No videos in {assets_dir}/")
        print("Add some MP4 files to use as background clips.")
        return

    # Load script
    print(f"\nScript: {SCRIPT_PATH}")
    with open(SCRIPT_PATH, "r") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    print(f"Scenes: {len(scenes)}")

    # Voiceover
    print(f"Voiceover: {VOICEOVER_PATH}")

    # Output path
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{OUTPUT_DIR}/test_{timestamp}.mp4"

    print(f"Output: {output_path}")
    print("\n" + "-" * 50)

    # Generate video
    result = generate_video(
        script_data=script_data,
        voiceover_path=VOICEOVER_PATH,
        output_path=output_path,
    )

    print("\n" + "=" * 50)
    print(f"Done! Video: {result}")
    print("=" * 50)


if __name__ == "__main__":
    main()
