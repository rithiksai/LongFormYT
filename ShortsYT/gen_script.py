"""Generate short script for YouTube Shorts from just a title."""

import os
from pydantic import BaseModel
from agents import Agent, Runner, ModelSettings
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

load_dotenv()

claude_api_key = os.environ.get("CLAUDE_API_KEY")


class ShortsScript(BaseModel):
    """Output model for YouTube Shorts script."""
    narration: str  # Full narration text (~30 seconds when spoken)
    hook: str  # Opening hook (first line to grab attention)
    duration_estimate: int  # Estimated duration in seconds


agent = Agent(
    name="ShortsScriptWriter",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5", api_key=claude_api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="""You are an expert YouTube Shorts script writer specializing in viral, attention-grabbing content.

OUTPUT FORMAT (all fields required):
{
  "narration": "The full script to be spoken (~30 seconds)",
  "hook": "The opening line that grabs attention",
  "duration_estimate": 30
}

RULES FOR YOUTUBE SHORTS:
1. HOOK IS EVERYTHING - First 3 seconds must grab attention immediately
2. Keep total narration to ~30 seconds when spoken aloud (~75-90 words)
3. Fast-paced, punchy sentences - no filler words
4. End with a call-to-action or thought-provoking question
5. NO stage directions, NO [brackets], NO *asterisks* - only spoken words
6. Make it entertaining, surprising, or controversial

STRUCTURE:
- Hook (0-3 sec): Shocking statement, question, or bold claim
- Body (3-25 sec): Deliver the main content quickly
- Ending (25-30 sec): Punchline, CTA, or cliffhanger

Keep it SHORT and PUNCHY. Every word must earn its place.""",
    output_type=ShortsScript,
)


def generate_script(title: str) -> dict:
    """
    Generate a YouTube Shorts script from a title.

    Args:
        title: The topic/title for the short

    Returns:
        Dict with narration, hook, and duration_estimate
    """
    print(f"  Generating script for: {title}")

    prompt = f"""Create a viral YouTube Shorts script for this topic:

**Title:** {title}

Generate a ~30 second script that hooks viewers in the first 3 seconds and keeps them watching until the end."""

    result = Runner.run_sync(agent, prompt)
    return result.final_output.model_dump()


if __name__ == "__main__":
    # Test with sample title
    test_title = "Why Goku would destroy Naruto in 5 seconds"
    output = generate_script(test_title)
    print(f"\nHook: {output['hook']}")
    print(f"\nNarration ({output['duration_estimate']}s):\n{output['narration']}")
