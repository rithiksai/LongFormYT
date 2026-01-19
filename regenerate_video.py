#!/usr/bin/env python3
"""Regenerate video from existing script, voiceover, and images."""

import json
from pathlib import Path

from video_assembler.photo_assembler import generate_photo_video


def main():
    # Paths to existing assets
    base_dir = Path(__file__).parent

    script_path = base_dir / "output/pipeline/scripts/what_if_tanjiro_was_reborn_with_his_memories_and_p_20260117_122155.json"
    voiceover_path = base_dir / "output/pipeline/voiceovers/what_if_tanjiro_was_reborn_with_his_memories_and_p_20260117_122155.mp3"
    photos_dir = base_dir / "assets/photos"
    output_path = base_dir / "output/regenerated_video.mp4"

    # Verify files exist
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not voiceover_path.exists():
        raise FileNotFoundError(f"Voiceover not found: {voiceover_path}")
    if not photos_dir.exists():
        raise FileNotFoundError(f"Photos directory not found: {photos_dir}")

    # Load script data
    print(f"Loading script: {script_path}")
    with open(script_path) as f:
        script_data = json.load(f)

    print(f"Voiceover: {voiceover_path}")
    print(f"Photos directory: {photos_dir}")
    print(f"Output: {output_path}")
    print()

    # Generate video with Ken Burns effects
    generate_photo_video(
        script_data=script_data,
        voiceover_path=str(voiceover_path),
        output_path=str(output_path),
        photos_dir=str(photos_dir),
    )

    print(f"\nVideo regenerated: {output_path}")


if __name__ == "__main__":
    main()
