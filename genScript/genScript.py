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
claude_api_key = os.environ["CLAUDE_API_KEY"]


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
    model=LitellmModel(model="anthropic/claude-sonnet-4-5", api_key=claude_api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="""You are an expert anime/entertainment YouTube script writer.

CRITICAL: You MUST output valid JSON with ALL THREE fields. Generate the "scenes" array FIRST as it is the most important.

OUTPUT FORMAT (all fields required):
{
  "script": "Brief 2-3 sentence summary of the video concept",
  "duration_estimate": 300,
  "scenes": [
    {
      "timestamp": "0:00",
      "narration": "The actual words to speak for this scene",
      "visual_suggestion": "Visual/audio cues"
    }
  ]
}

IMPORTANT RULES:
1. "script" field: Keep it SHORT (2-3 sentences max). Just a brief summary.
2. "duration_estimate": Integer in seconds (aim for 180-300 seconds)
3. "scenes": Array of 8-12 scene objects. THIS IS THE MOST IMPORTANT PART.

SCENE RULES:
- Each scene needs: timestamp, narration, visual_suggestion
- "narration": ONLY spoken words. NO stage directions, NO [brackets], NO *asterisks*
- "visual_suggestion": Put all music/visual cues here
- Keep each narration 2-4 sentences

Create engaging, fun content with:
- Attention-grabbing hook in first scene
- Good pacing and transitions
- Entertaining narration style""",
    output_type=ScriptOutput,
)


def generate_script(title: str, transcript: str) -> dict:
    """Generate a structured video script from a title and transcript."""
    # Debug: Log transcript info
    print(f"  [DEBUG] Title: {title[:50]}...")
    print(f"  [DEBUG] Transcript length: {len(transcript)} chars, ~{len(transcript.split())} words")

    # Truncate transcript if too long (keep first 10000 chars)
    max_chars = 10000
    if len(transcript) > max_chars:
        print(f"  [DEBUG] Truncating transcript from {len(transcript)} to {max_chars} chars")
        transcript = transcript[:max_chars] + "..."

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