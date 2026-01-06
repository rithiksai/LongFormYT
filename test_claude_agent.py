"""Test file to debug Claude agent with structured output."""

import os
from pydantic import BaseModel
from agents import Agent, Runner, ModelSettings
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

load_dotenv()

claude_api_key = os.environ.get("CLAUDE_API_KEY")

# Simple structured output
class SimpleOutput(BaseModel):
    title: str
    summary: str
    score: int


# Complex structured output (like genScript.py)
class Scene(BaseModel):
    timestamp: str
    narration: str
    visual_suggestion: str


class ScriptOutput(BaseModel):
    script: str
    duration_estimate: int
    scenes: list[Scene]


# Test agent with Claude - simple
agent_simple = Agent(
    name="TestAgent",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5", api_key=claude_api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="You are a helpful assistant. Always respond with the requested JSON structure.",
    output_type=SimpleOutput,
)

# Test agent with Claude - complex (like genScript)
agent_complex = Agent(
    name="ScriptWriter",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5", api_key=claude_api_key),
    model_settings=ModelSettings(include_usage=True),
    instructions="""You are an expert YouTube script writer.

YOUR OUTPUT MUST INCLUDE ALL THREE FIELDS:
1. "script" - The full script text as a single string
2. "duration_estimate" - Estimated duration in seconds (integer)
3. "scenes" - An array of scene objects, each with:
   - "timestamp": when this scene starts (e.g., "0:00", "0:30", "1:15")
   - "narration": ONLY the spoken words for this scene
   - "visual_suggestion": visual/audio cues for this scene

Create 3-5 scenes for the script.""",
    output_type=ScriptOutput,
)


def test_simple():
    """Test simple structured output."""
    print("=" * 50)
    print("TEST 1: Simple structured output")
    print("=" * 50)
    print(f"API Key present: {bool(claude_api_key)}")

    prompt = "Give me a title, summary, and score (1-10) for the movie 'Inception'."

    try:
        result = Runner.run_sync(agent_simple, prompt)
        print("\n✅ Success!")
        print(f"Result: {result.final_output}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_complex():
    """Test complex structured output with transcript (like genScript)."""
    print("\n" + "=" * 50)
    print("TEST 2: Complex structured output (ScriptOutput)")
    print("=" * 50)

    # Simulating the actual prompt from genScript.py
    title = "Top 5 Anime Fights"
    transcript = """Today we're counting down the top 5 anime fights of all time.
    Number 5 is Naruto vs Sasuke. Number 4 is Goku vs Frieza.
    Number 3 is Luffy vs Katakuri. Number 2 is Saitama vs Boros.
    And number 1 is Eren vs Reiner."""

    prompt = f"""Create an engaging YouTube video script based on this content:

**Video Title:** {title}

**Original Transcript:**
{transcript}

Generate a script with scenes, timestamps, narration, and visual suggestions."""

    try:
        result = Runner.run_sync(agent_complex, prompt)
        print("\n✅ Success!")
        print(f"Script: {result.final_output.script[:100]}...")
        print(f"Duration: {result.final_output.duration_estimate}s")
        print(f"Scenes count: {len(result.final_output.scenes)}")
        for i, scene in enumerate(result.final_output.scenes):
            print(f"  Scene {i+1}: {scene.timestamp} - {scene.narration[:50]}...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_long_transcript():
    """Test with a very long transcript (simulating real YouTube transcript)."""
    print("\n" + "=" * 50)
    print("TEST 3: Long transcript (simulating real pipeline)")
    print("=" * 50)

    title = "What If Straw Hats Were Reborn With Their Memories"

    # Simulate a long transcript (~2000 words)
    transcript = """What if the Straw Hats were reborn with all their memories intact?
    Would they fix their tragic pasts, or would fate throw them an even bigger curveball?
    Let's dive into this wild alternate timeline and see how our favorite pirates would rewrite their own story!

    Starting with our captain, Monkey D. Luffy. Picture this: little Luffy wakes up as a child,
    but with all his memories from the future. Confusing, right? But being Luffy, he'd play it cool,
    reliving those precious moments with Ace and Sabo. Of course, he'd still gobble up the Gum-Gum Fruit
    because destiny and all that. But here's the twist: Shanks keeps his arm! That's right, no more
    one-armed mentor because Luffy would be smart enough to dodge that bandit situation entirely.

    But wait, it gets better! Young Luffy would secretly train his Haki and single-handedly wreck the
    Blue Jam Pirates, ensuring both Ace and Sabo survive and thrive. No tragedies here, folks!
    When he turns seventeen, our rubber boy sets sail and the reunion tour begins.

    Now let's talk about Zoro. This absolute unit gets reborn and immediately goes into training mode.
    With all his future knowledge, he dominates Kuina in their duels, but they still become best friends.
    And here's the kicker: Zoro actually saves Kuina from her fatal accident! She lives, becomes a
    legendary blade collector, and we get the wholesome Zoro storyline we all deserved.

    """ * 5  # Repeat to make it longer

    print(f"Transcript length: {len(transcript)} chars, ~{len(transcript.split())} words")

    prompt = f"""Create an engaging YouTube video script based on this content:

**Video Title:** {title}

**Original Transcript:**
{transcript}

Generate a script with scenes, timestamps, narration, and visual suggestions."""

    try:
        result = Runner.run_sync(agent_complex, prompt)
        print("\n✅ Success!")
        print(f"Script: {result.final_output.script[:100]}...")
        print(f"Duration: {result.final_output.duration_estimate}s")
        print(f"Scenes count: {len(result.final_output.scenes)}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple()
    test_complex()
    test_long_transcript()
