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


class ShortsScriptWithVisuals(BaseModel):
    """Output model for YouTube Shorts script with visual suggestions."""
    narration: str  # Full narration text (~30 seconds when spoken)
    hook: str  # Opening hook (first line to grab attention)
    duration_estimate: int  # Estimated duration in seconds
    visual_suggestions: list[str]  # List of image prompts for AI generation


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

HOOK STRATEGY - START WITH THE OUTCOME (CRITICAL):
The first 1.5 seconds determine if viewers keep watching. Lead with the RESULT, not the story.

WRONG (context/backstory first - NEVER do this):
- "I started a faceless YouTube channel and…"
- "So I decided to try this new thing…"
- "Let me tell you about what happened when…"

RIGHT (outcome/result first - ALWAYS do this):
- "This faceless Short made $47 while I was asleep."
- "$2,000 in 30 days from a channel with zero subscribers."
- "One video. 2 million views. Here's the secret."

Hook Rules:
- NO backstory in the hook
- NO buildup or context setting
- Lead with the shocking result, number, or outcome
- Make viewers NEED to know how

RULES FOR YOUTUBE SHORTS:
1. HOOK IS EVERYTHING - First 1.5 seconds must grab attention with an OUTCOME
2. Keep total narration to ~25 seconds when spoken aloud (MAXIMUM 80 words - this is strict)
3. Fast-paced, punchy sentences - no filler words
4. End with a call-to-action or thought-provoking question
5. NO stage directions, NO [brackets], NO *asterisks* - only spoken words
6. Make it entertaining, surprising, or controversial

STRUCTURE:
- Hook (0-1.5 sec): OUTCOME FIRST - Lead with the result, number, or payoff. No backstory.
- Body (1.5-25 sec): Deliver the main content quickly
- Ending (25-30 sec): Punchline, CTA, or cliffhanger

Keep it SHORT and PUNCHY. Every word must earn its place.""",
    output_type=ShortsScript,
)


agent_with_visuals = Agent(
    name="ShortsScriptWriterWithVisuals",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5", api_key=claude_api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="""You are an expert YouTube Shorts script writer specializing in viral, attention-grabbing content WITH visual suggestions for AI image generation.

OUTPUT FORMAT (all fields required):
{
  "narration": "The full script to be spoken (~30 seconds)",
  "hook": "The opening line that grabs attention",
  "duration_estimate": 30,
  "visual_suggestions": [
    "Anime style description 1",
    "Anime style description 2",
    ...
  ]
}

HOOK STRATEGY - START WITH THE OUTCOME (CRITICAL):
The first 1.5 seconds determine if viewers keep watching. Lead with the RESULT, not the story.

WRONG (context/backstory first - NEVER do this):
- "I started a faceless YouTube channel and…"
- "So I decided to try this new thing…"
- "Let me tell you about what happened when…"

RIGHT (outcome/result first - ALWAYS do this):
- "This faceless Short made $47 while I was asleep."
- "$2,000 in 30 days from a channel with zero subscribers."
- "One video. 2 million views. Here's the secret."

Hook Rules:
- NO backstory in the hook
- NO buildup or context setting
- Lead with the shocking result, number, or outcome
- Make viewers NEED to know how

RULES FOR YOUTUBE SHORTS:
1. HOOK IS EVERYTHING - First 1.5 seconds must grab attention with an OUTCOME
2. Keep total narration to ~25 seconds when spoken aloud (MAXIMUM 80 words - this is strict)
3. Fast-paced, punchy sentences - no filler words
4. End with a call-to-action or thought-provoking question
5. NO stage directions, NO [brackets], NO *asterisks* - only spoken words
6. Make it entertaining, surprising, or controversial

STRUCTURE:
- Hook (0-1.5 sec): OUTCOME FIRST - Lead with the result, number, or payoff. No backstory.
- Body (1.5-25 sec): Deliver the main content quickly
- Ending (25-30 sec): Punchline, CTA, or cliffhanger

VISUAL SUGGESTIONS RULES:
1. Generate 6-8 visual suggestions (one per ~4-5 seconds of content)
2. Each MUST start with "Anime style" prefix
3. Describe STATIC images - no motion, no video clips
4. Focus on VERTICAL compositions suitable for 9:16 phone screens
5. Emphasize close-ups, portraits, and vertically-oriented scenes
6. Match the emotion and theme of the corresponding narration section
7. Be specific and descriptive (1-2 sentences each)

VISUAL SUGGESTION EXAMPLES:
- "Anime style close-up portrait of a determined warrior with glowing eyes and dramatic lighting"
- "Anime style vertical scene of a towering mountain peak shrouded in mist"
- "Anime style dramatic portrait of a character looking shocked with speed lines"
- "Anime style mystical energy orb floating in darkness with colorful aura"

Keep it SHORT and PUNCHY. Every word must earn its place.""",
    output_type=ShortsScriptWithVisuals,
)


def generate_script(title: str, include_visuals: bool = False) -> dict:
    """
    Generate a YouTube Shorts script from a title.

    Args:
        title: The topic/title for the short
        include_visuals: If True, generate visual suggestions for AI image generation

    Returns:
        Dict with narration, hook, duration_estimate, and optionally visual_suggestions
    """
    print(f"  Generating script for: {title}")
    if include_visuals:
        print("  (with visual suggestions for AI images)")

    prompt = f"""Create a viral YouTube Shorts script for this topic:

**Title:** {title}

Generate a ~30 second script that hooks viewers in the first 1.5 seconds with an OUTCOME (not backstory) and keeps them watching until the end."""

    selected_agent = agent_with_visuals if include_visuals else agent
    result = Runner.run_sync(selected_agent, prompt)
    return result.final_output.model_dump()


if __name__ == "__main__":
    # Test with sample title
    test_title = "Why Goku would destroy Naruto in 5 seconds"
    output = generate_script(test_title)
    print(f"\nHook: {output['hook']}")
    print(f"\nNarration ({output['duration_estimate']}s):\n{output['narration']}")
