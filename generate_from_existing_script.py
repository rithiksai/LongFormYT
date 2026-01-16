#!/usr/bin/env python3
"""Generate voiceover and video from an existing script JSON file.

Usage:
    python3 generate_from_existing_script.py
"""

import json
import os
from pathlib import Path
from voiceOver.genVoice import generate_full_voiceover
from video_assembler.photo_assembler import generate_photo_video

# Configuration
SCRIPT_PATH = "output/pipeline/scripts/what_if_gojo_was_reborn_with_his_memories_20260115_233432.json"
PHOTOS_DIR = "assets/photos"  # Directory with generated images
OUTPUT_DIR = "output/pipeline"

def main():
    print("=" * 80)
    print("  GENERATE VIDEO FROM EXISTING SCRIPT")
    print("=" * 80)

    # ========== STEP 1: Load Script ==========
    print("\n" + "-" * 80)
    print("STEP 1: Loading Script")
    print("-" * 80)

    script_path = Path(SCRIPT_PATH)
    if not script_path.exists():
        print(f"ERROR: Script file not found: {SCRIPT_PATH}")
        return

    with open(script_path, 'r') as f:
        script_data = json.load(f)

    print(f"  Loaded: {script_path}")
    print(f"  Duration estimate: {script_data.get('duration_estimate', 'N/A')}s")
    print(f"  Number of scenes: {len(script_data.get('scenes', []))}")

    # ========== STEP 2: Generate Voiceover ==========
    print("\n" + "-" * 80)
    print("STEP 2: Generating Voiceover")
    print("-" * 80)

    # Create output directories
    os.makedirs(f"{OUTPUT_DIR}/voiceovers", exist_ok=True)

    # Extract base name from script file
    script_name = script_path.stem  # e.g., "what_if_gojo_was_reborn_with_his_memories_20260115_233432"
    voiceover_path = f"{OUTPUT_DIR}/voiceovers/{script_name}.mp3"

    try:
        result = generate_full_voiceover(script_data, voiceover_path)

        if result:
            print(f"  Voiceover generated!")
            print(f"  - Saved to: {voiceover_path}")
            file_size = os.path.getsize(voiceover_path) / (1024 * 1024)
            print(f"  - File size: {file_size:.2f} MB")
        else:
            print("  No narration found")
            return

    except Exception as e:
        print(f"  Voiceover generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========== STEP 3: Generate Video ==========
    print("\n" + "-" * 80)
    print("STEP 3: Generating Video with Ken Burns Effects")
    print("-" * 80)

    # Create videos directory
    os.makedirs(f"{OUTPUT_DIR}/videos", exist_ok=True)

    video_path = f"{OUTPUT_DIR}/videos/{script_name}.mp4"

    try:
        result = generate_photo_video(
            script_data=script_data,
            voiceover_path=voiceover_path,
            output_path=video_path,
            photos_dir=PHOTOS_DIR,
        )

        print(f"\n  Video generated!")
        print(f"  - Saved to: {video_path}")
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"  - File size: {file_size:.2f} MB")

    except Exception as e:
        print(f"  Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========== DONE ==========
    print("\n" + "=" * 80)
    print("  SUCCESS! VIDEO GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n  Final video: {video_path}")
    print(f"  Duration: ~{script_data.get('duration_estimate', 'N/A')} seconds")
    print(f"  Scenes: {len(script_data.get('scenes', []))}")
    print()


if __name__ == "__main__":
    main()
