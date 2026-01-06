from elevenlabs.client import ElevenLabs
from elevenlabs import play, save
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("ELEVEN_LABS_API")
client = ElevenLabs(api_key=api_key)

# Default voice settings
DEFAULT_VOICE_ID = "zYcjlYFOd3taleS0gkk3"
DEFAULT_MODEL = "eleven_multilingual_v2"


def generate_voiceover(text: str, output_path: str = None, voice_id: str = DEFAULT_VOICE_ID) -> bytes:
    """
    Generate voiceover audio from text.

    Args:
        text: The script text to convert to speech
        output_path: Optional file path to save the audio (e.g., "output.mp3")
        voice_id: ElevenLabs voice ID to use

    Returns:
        Audio bytes
    """
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=DEFAULT_MODEL,
        output_format="mp3_44100_128",
    )

    # Convert generator to bytes
    audio_bytes = b"".join(audio)

    if output_path:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"Audio saved to {output_path}")

    return audio_bytes


def generate_voiceover_from_script(script_output: dict, output_dir: str = "output") -> list[str]:
    """
    Generate voiceovers for each scene in a script.

    Args:
        script_output: The script dict with 'scenes' containing 'narration' for each scene
        output_dir: Directory to save audio files

    Returns:
        List of generated audio file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_files = []

    for i, scene in enumerate(script_output.get("scenes", [])):
        narration = scene.get("narration", "")
        if narration:
            output_path = os.path.join(output_dir, f"scene_{i+1}.mp3")
            generate_voiceover(narration, output_path)
            audio_files.append(output_path)

    return audio_files


def generate_full_voiceover(script_output: dict, output_path: str = "output/full_voiceover.mp3") -> str:
    """
    Generate a single voiceover from all scene narrations combined.

    Args:
        script_output: The script dict with 'scenes' containing 'narration' for each scene
        output_path: File path to save the audio

    Returns:
        Path to the generated audio file, or None if no narration found
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Combine all scene narrations (not just script summary)
    scenes = script_output.get("scenes", [])
    narrations = [scene.get("narration", "") for scene in scenes if scene.get("narration")]
    full_text = " ".join(narrations).strip()

    if not full_text:
        return None

    generate_voiceover(full_text, output_path)
    return output_path


if __name__ == "__main__":
    # Test with sample text
    test_text = "The first move is what sets everything in motion."
    audio = generate_voiceover(test_text, "output/test.mp3")
    print("Voiceover generated!")
