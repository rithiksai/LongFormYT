"""
Test the full video generation pipeline.

This script tests:
1. Script Generation (genScript)
2. Voiceover Generation (genVoice)
3. Video Assembly (video_assembler)
"""

import os
from dotenv import load_dotenv
load_dotenv()


def test_asset_manager():
    """Test just the asset manager (downloading clips)."""
    from video_assembler.asset_manager import AssetManager

    print("Testing Asset Manager...")
    manager = AssetManager()

    # Download a short clip
    clip_path = manager.download_clip("anime action scene short", duration=10)
    print(f"Downloaded clip: {clip_path}")
    print("Asset Manager test passed!")


def test_motion_graphics():
    """Test motion graphics generation (no API needed)."""
    from video_assembler.motion_graphics import MotionGraphics

    print("Testing Motion Graphics...")
    mg = MotionGraphics()

    # Create title card
    title = mg.create_title_card(
        title="Test Title",
        subtitle="Test Subtitle",
        duration=3.0
    )
    print(f"Created title card: {title.duration}s")

    # Save a frame to verify
    title.save_frame("output/test_title_frame.png", t=0)
    print("Saved test frame to output/test_title_frame.png")
    print("Motion Graphics test passed!")


def test_video_assembler_only():
    """Test video assembler with sample data (requires a voiceover file)."""
    from video_assembler import VideoAssembler

    # Sample script data
    sample_script = {
        "script": "Welcome to our epic anime countdown!",
        "duration_estimate": 30,
        "scenes": [
            {
                "timestamp": "0:00",
                "narration": "Welcome to the top anime moments!",
                "visual_suggestion": "anime epic action montage",
            },
            {
                "timestamp": "0:10",
                "narration": "Number one: The legendary battle!",
                "visual_suggestion": "anime fight scene dramatic battle",
            },
        ],
    }

    voiceover_path = "test_voiceover.mp3"

    if not os.path.exists(voiceover_path):
        print(f"\nVoiceover file not found: {voiceover_path}")
        print("\nTo create a voiceover, run:")
        print('  python -c "from voiceOver.genVoice import generate_voiceover; generate_voiceover(\'Welcome to the top anime moments! Number one: The legendary battle!\', \'test_voiceover.mp3\')"')
        print("\nOr place your own MP3 file at: test_voiceover.mp3")
        print("\nAlternatively, test individual components:")
        print("  python test_pipeline.py --graphics  (test motion graphics)")
        print("  python test_pipeline.py --download  (test clip downloading)")
        return

    # Generate video
    assembler = VideoAssembler()
    output = assembler.generate_video(
        script_data=sample_script,
        voiceover_path=voiceover_path,
        output_path="output/test_video.mp4"
    )

    print(f"Video created: {output}")


def test_full_pipeline():
    """Test the complete pipeline from script to video."""
    from genScript.genScript import generate_script
    from voiceOver.genVoice import generate_full_voiceover
    from video_assembler import VideoAssembler

    # Step 1: Generate script
    print("Step 1: Generating script...")
    script = generate_script(
        title="Top 3 Epic Anime Moments",
        transcript="Today we count down the most epic moments in anime history that made us all cry."
    )
    print(f"Script generated with {len(script['scenes'])} scenes")

    # Step 2: Generate voiceover
    print("\nStep 2: Generating voiceover...")
    voiceover_path = generate_full_voiceover(
        script_output=script,
        output_path="output/pipeline_voiceover.mp3"
    )
    print(f"Voiceover saved to: {voiceover_path}")

    # Step 3: Assemble video
    print("\nStep 3: Assembling video...")
    assembler = VideoAssembler()
    output = assembler.generate_video(
        script_data=script,
        voiceover_path=voiceover_path,
        output_path="output/pipeline_video.mp4"
    )

    print(f"\nPipeline complete! Video saved to: {output}")
    return output


if __name__ == "__main__":
    import sys

    print("=" * 50)
    print("Video Generation Pipeline Test")
    print("=" * 50)

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--full":
            # Full pipeline test (requires API keys)
            print("\nRunning FULL pipeline test...")
            print("This requires: GEMINI_API_KEY, ELEVEN_LABS_API\n")
            test_full_pipeline()

        elif arg == "--graphics":
            # Test motion graphics only (no API needed)
            print("\nRunning MOTION GRAPHICS test...")
            print("No API keys required.\n")
            test_motion_graphics()

        elif arg == "--download":
            # Test asset manager only
            print("\nRunning ASSET MANAGER test...")
            print("This downloads clips from YouTube.\n")
            test_asset_manager()

        else:
            print(f"\nUnknown option: {arg}")
            print("\nAvailable options:")
            print("  --graphics  : Test motion graphics (no API needed)")
            print("  --download  : Test YouTube clip downloading")
            print("  --full      : Full pipeline test (all APIs needed)")
            print("  (no args)   : Test video assembler (needs voiceover file)")
    else:
        # Default: test video assembler
        print("\nRunning VIDEO ASSEMBLER test...")
        print("Requires: test_voiceover.mp3 file\n")
        test_video_assembler_only()
