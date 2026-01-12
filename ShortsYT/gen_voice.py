"""Generate voiceover for YouTube Shorts using ElevenLabs."""

import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("ELEVEN_LABS_API")
client = ElevenLabs(api_key=api_key)

# Default voice settings
DEFAULT_VOICE_ID = "V6zMK42bu1TVQBA7MwcF"
DEFAULT_MODEL = "eleven_multilingual_v2"


def generate_voiceover(narration: str, output_path: str) -> str:
    """
    Generate voiceover audio from narration text.

    Args:
        narration: The script text to convert to speech
        output_path: File path to save the audio (e.g., "output/voiceover.mp3")

    Returns:
        Path to the generated audio file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"  Generating voiceover ({len(narration.split())} words)...")

    audio = client.text_to_speech.convert(
        text=narration,
        voice_id=DEFAULT_VOICE_ID,
        model_id=DEFAULT_MODEL,
        output_format="mp3_44100_128",
    )

    # Convert generator to bytes and save
    audio_bytes = b"".join(audio)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    print(f"  Voiceover saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test with sample narration
    test_narration = "Here's something that will blow your mind. Did you know that most people never realize this simple truth? Think about it."
    output = generate_voiceover(test_narration, "output/test_short.mp3")
    print(f"Generated: {output}")
