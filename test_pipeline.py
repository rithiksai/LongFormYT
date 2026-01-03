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
    from video_assembler.text_animations import TextAnimations
    from video_assembler.scene_director import SceneDirector

    print("Testing Motion Graphics...")
    os.makedirs("output", exist_ok=True)

    mg = MotionGraphics()

    # Create static title card
    title = mg.create_title_card(
        title="Test Title",
        subtitle="Test Subtitle",
        duration=3.0
    )
    print(f"Created static title card: {title.duration}s")

    # Test ANIMATED graphics
    print("\nTesting ANIMATED motion graphics...")

    # Animated title card
    animated_title = mg.create_animated_title_card(
        title="Top 10 Anime Moments",
        subtitle="That Will Blow Your Mind!",
        duration=3.0,
    )
    print(f"Created animated title card: {animated_title.duration}s")
    animated_title.save_frame("output/test_animated_title.png", t=0.5)

    # Animated ranking card
    ranking = mg.create_animated_ranking_card(
        rank=5,
        title="The Ultimate Sacrifice",
        subtitle="Attack on Titan",
        duration=2.5,
    )
    print(f"Created animated ranking card: {ranking.duration}s")
    ranking.save_frame("output/test_ranking_card.png", t=0.5)

    # Lower third
    lower_third = mg.create_lower_third(
        name="Naruto Uzumaki",
        title="The Seventh Hokage",
        duration=4.0,
    )
    print(f"Created lower third: {lower_third.duration}s")

    # Test text animations
    print("\nTesting TEXT ANIMATIONS...")
    ta = TextAnimations()

    # Word-by-word caption
    word_caption = ta.create_word_by_word_caption(
        text="Welcome to the top ten anime moments!",
        duration=4.0,
        emphasis_words=["top", "ten", "anime"],
    )
    print(f"Created word-by-word caption: {word_caption.duration}s")
    word_caption.save_frame("output/test_word_caption.png", t=1.0)

    # Pop-in text
    pop_text = ta.create_pop_in_text(
        text="EPIC!",
        duration=2.0,
    )
    print(f"Created pop-in text: {pop_text.duration}s")

    # Test scene director
    print("\nTesting SCENE DIRECTOR...")
    director = SceneDirector(use_ai=False)

    test_scenes = [
        {"narration": "Welcome to our countdown of epic anime moments!", "visual_suggestion": "anime montage"},
        {"narration": "Number 5: The legendary battle!", "visual_suggestion": "fight scene"},
        {"narration": "Thanks for watching! Subscribe!", "visual_suggestion": "outro"},
    ]

    for i, scene in enumerate(test_scenes):
        directive = director.analyze_scene(
            narration=scene["narration"],
            visual_suggestion=scene["visual_suggestion"],
            scene_index=i,
            total_scenes=len(test_scenes),
        )
        print(f"Scene {i+1}: {directive.motion_graphic or 'none'} - {directive.energy_level} energy")

    print("\nMotion Graphics, Text Animations & Scene Director tests passed!")
    print("Check output/ folder for saved frames.")


def test_video_assembler_only():
    """Test video assembler with sample data (requires a voiceover file)."""
    from video_assembler import VideoAssembler

    # Sample script data with ranking scenes to trigger motion graphics
    sample_script = {
        "script": "Welcome to our epic anime countdown!",
        "duration_estimate": 30,
        "scenes": [
            {
                "timestamp": "0:00",
                "narration": "Welcome to our countdown of the top anime moments of all time!",
                "visual_suggestion": "anime epic action montage",
            },
            {
                "timestamp": "0:10",
                "narration": "Number 3: The legendary battle between rivals!",
                "visual_suggestion": "anime fight scene dramatic battle",
            },
            {
                "timestamp": "0:20",
                "narration": "And finally, the most epic moment ever! Thanks for watching, subscribe!",
                "visual_suggestion": "anime climax emotional scene",
            },
        ],
    }

    voiceover_path = "test_voiceover.mp3"

    if not os.path.exists(voiceover_path):
        print(f"\nVoiceover file not found: {voiceover_path}")
        print("\nTo create a voiceover, run:")
        print('  python -c "from voiceOver.genVoice import generate_voiceover; generate_voiceover(\'Welcome to our countdown! Number 3: The legendary battle! And finally, thanks for watching!\', \'test_voiceover.mp3\')"')
        print("\nOr place your own MP3 file at: test_voiceover.mp3")
        print("\nAlternatively, test individual components:")
        print("  python test_pipeline.py --graphics  (test motion graphics + animations)")
        print("  python test_pipeline.py --download  (test clip downloading)")
        return

    # Generate video with animated graphics enabled
    print("\nGenerating video with ANIMATED graphics...")
    assembler = VideoAssembler(
        use_ai_director=False,  # Use rule-based (no API needed)
        use_animated_graphics=True,  # Enable animated motion graphics
    )
    output = assembler.generate_video(
        script_data=sample_script,
        voiceover_path=voiceover_path,
        output_path="output/test_video.mp4"
    )

    print(f"\nVideo created with animated graphics: {output}")


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
