import os
from pydantic import BaseModel
from agents import Agent, Runner, ModelSettings, set_tracing_export_api_key
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

load_dotenv()

# Enable tracing to OpenAI dashboard with your OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    set_tracing_export_api_key(openai_api_key)

api_key = os.environ["GEMINI_API_KEY"]


# Pydantic models for structured output
class Scene(BaseModel):
    timestamp: str
    narration: str
    visual_suggestion: str


class ScriptOutput(BaseModel):
    script: str
    duration_estimate: int
    scenes: list[Scene]


# Agent with instructions for anime/entertainment script generation
agent = Agent(
    name="ScriptWriter",
    model=LitellmModel(model="gemini/gemini-2.0-flash", api_key=api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="""You are an expert anime/entertainment YouTube script writer.

CRITICAL RULES FOR NARRATION:
- The "narration" field must contain ONLY words to be spoken aloud by a narrator
- DO NOT include stage directions, music cues, or production notes in narration
- NO text like "[epic music plays]", "(dramatic pause)", "*music swells*", or similar
- NO descriptions of sounds, music, or visual effects in narration
- Put all visual/audio cues in the "visual_suggestion" field instead
- Narration should read naturally when spoken - no brackets, asterisks, or parentheses

When given a video title and transcript:
1. Analyze the key themes, hooks, and engaging moments
2. Create a new script that captures the essence but adds your own twist
3. Break down into scenes with timestamps
4. Keep narration clean - only spoken words
5. Put music/visual cues in visual_suggestion field

Your scripts should be:
- A mximum duration of 1 min
- Attention-grabbing from the first second
- Fun and entertaining with humor
- Well-paced with clear transitions
- Optimized for viewer retention""",
    output_type=ScriptOutput,
)


def generate_script(title: str, transcript: str) -> dict:
    """Generate a structured video script from a title and transcript."""
    prompt = f"""Create an engaging YouTube video script based on this content:

**Video Title:** {title}

**Original Transcript:**
{transcript}

Generate a script with scenes, timestamps, narration, and visual suggestions."""

    result = Runner.run_sync(agent, prompt)
    return result.final_output.model_dump()


if __name__ == "__main__":
    # Test with sample data
    test_title = "Top 10 Anime Betrayals"
    test_transcript = "Today we're going to talk about the most shocking betrayals in anime history..."

    output = generate_script(test_title, test_transcript)
    print(output)