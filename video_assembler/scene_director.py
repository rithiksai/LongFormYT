"""Scene Director - Analyzes scenes and recommends animations/effects.

Provides both rule-based defaults and optional AI-powered enhancement.
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class AnimationDirective(BaseModel):
    """Directives for how to animate a scene."""

    caption_style: str = Field(
        default="word_pop",
        description="Caption animation style: word_pop, full_pop, slide, typewriter"
    )
    motion_graphic: Optional[str] = Field(
        default=None,
        description="Motion graphic to use: ranking_card, title_card, lower_third, subscribe, None"
    )
    transition_in: str = Field(
        default="fade",
        description="Transition effect: fade, zoom, slide, none"
    )
    transition_out: str = Field(
        default="fade",
        description="Transition out effect"
    )
    emphasis_words: List[str] = Field(
        default_factory=list,
        description="Words to emphasize/highlight in captions"
    )
    energy_level: str = Field(
        default="medium",
        description="Energy level: high, medium, low"
    )
    ranking_number: Optional[int] = Field(
        default=None,
        description="Ranking number if this is a ranking scene"
    )
    is_intro: bool = Field(
        default=False,
        description="Whether this is an intro scene"
    )
    is_outro: bool = Field(
        default=False,
        description="Whether this is an outro scene"
    )


class SceneDirector:
    """
    Analyzes scene content and provides animation directives.

    Uses rule-based analysis by default, with optional AI enhancement.
    """

    # Keywords for detecting scene types and energy levels
    HIGH_ENERGY_KEYWORDS = [
        "epic", "legendary", "incredible", "insane", "amazing", "powerful",
        "explosive", "intense", "ultimate", "devastating", "shocking",
        "unbelievable", "mindblowing", "crazy", "extreme", "massive",
        "brutal", "fierce", "unstoppable", "legendary"
    ]

    INTRO_KEYWORDS = [
        "welcome", "today", "in this video", "let's", "we're going to",
        "introducing", "hello", "hey everyone", "what's up", "greetings"
    ]

    OUTRO_KEYWORDS = [
        "thanks for watching", "subscribe", "like and subscribe",
        "see you next time", "until next time", "that's all",
        "conclusion", "final thoughts", "wrap up"
    ]

    EMPHASIS_PATTERNS = [
        r'\b(number\s*\d+|#\d+)\b',  # Rankings
        r'\b(top\s*\d+)\b',  # Top X
        r'\b(best|worst|greatest|most)\b',  # Superlatives
        r'\b(epic|legendary|incredible|amazing)\b',  # Emphasis words
    ]

    def __init__(self, use_ai: bool = False):
        """
        Initialize the scene director.

        Args:
            use_ai: Whether to use AI for analysis (requires API key)
        """
        self.use_ai = use_ai
        self._ai_agent = None

        if use_ai:
            self._init_ai_agent()

    def _init_ai_agent(self):
        """Initialize the AI agent for scene analysis."""
        try:
            from agents import Agent, ModelSettings

            self._ai_agent = Agent(
                name="SceneDirector",
                model="gemini/gemini-2.0-flash",
                model_settings=ModelSettings(temperature=0.3),
                instructions="""You are a video effects director for YouTube anime content.

Analyze the scene narration and suggest the best animations and effects.
Focus on making the video engaging with bold, energetic YouTube style.

For each scene, determine:
1. Caption style (word_pop for energy, typewriter for calm, slide for transitions)
2. Whether to use motion graphics (ranking cards for rankings, lower thirds for introductions)
3. Energy level (high for epic moments, medium for explanations, low for emotional beats)
4. Words to emphasize (key terms, character names, ranking numbers)

Be selective with motion graphics - use them for important moments, not every scene.
""",
                output_type=AnimationDirective,
            )
        except Exception as e:
            print(f"Warning: Could not initialize AI agent: {e}")
            self._ai_agent = None

    def analyze_scene(
        self,
        narration: str,
        visual_suggestion: str = "",
        scene_index: int = 0,
        total_scenes: int = 1,
    ) -> AnimationDirective:
        """
        Analyze a scene and return animation directives.

        Args:
            narration: The scene's narration text
            visual_suggestion: Visual suggestion from script
            scene_index: Index of this scene (0-based)
            total_scenes: Total number of scenes

        Returns:
            AnimationDirective with recommended effects
        """
        if self.use_ai and self._ai_agent:
            return self._analyze_with_ai(
                narration, visual_suggestion, scene_index, total_scenes
            )

        return self._analyze_rule_based(
            narration, visual_suggestion, scene_index, total_scenes
        )

    def _analyze_rule_based(
        self,
        narration: str,
        visual_suggestion: str,
        scene_index: int,
        total_scenes: int,
    ) -> AnimationDirective:
        """
        Rule-based scene analysis.

        Args:
            narration: Scene narration
            visual_suggestion: Visual suggestion
            scene_index: Scene index
            total_scenes: Total scenes

        Returns:
            AnimationDirective
        """
        combined_text = f"{narration} {visual_suggestion}".lower()
        directive = AnimationDirective()

        # Detect intro/outro
        if scene_index == 0:
            if any(kw in combined_text for kw in self.INTRO_KEYWORDS):
                directive.is_intro = True
                directive.motion_graphic = "title_card"
                directive.energy_level = "high"

        if scene_index == total_scenes - 1:
            if any(kw in combined_text for kw in self.OUTRO_KEYWORDS):
                directive.is_outro = True
                directive.motion_graphic = "subscribe"

        # Detect ranking scenes
        ranking_match = re.search(
            r'(?:number|#)\s*(\d+)|(\d+)(?:st|nd|rd|th)\s+(?:place|spot)',
            combined_text,
            re.IGNORECASE
        )
        if ranking_match:
            rank_num = ranking_match.group(1) or ranking_match.group(2)
            directive.ranking_number = int(rank_num)
            directive.motion_graphic = "ranking_card"
            directive.energy_level = "high"

        # Detect energy level
        energy_score = sum(
            1 for kw in self.HIGH_ENERGY_KEYWORDS
            if kw in combined_text
        )
        if energy_score >= 2:
            directive.energy_level = "high"
        elif energy_score == 0:
            directive.energy_level = "low" if len(narration) > 200 else "medium"

        # Find emphasis words
        emphasis_words = []
        for pattern in self.EMPHASIS_PATTERNS:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                # Handle both string matches and tuple matches from groups
                if isinstance(matches[0], str):
                    emphasis_words.extend(matches)
                else:
                    # Flatten tuple matches
                    for match in matches:
                        if isinstance(match, tuple):
                            emphasis_words.extend([m for m in match if m])
                        else:
                            emphasis_words.append(match)

        # Also emphasize character/anime names (capitalized words)
        capital_words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', narration)
        emphasis_words.extend(capital_words[:3])  # Limit to 3

        directive.emphasis_words = list(set(emphasis_words))[:5]  # Max 5 emphasis words

        # Set caption style based on energy
        if directive.energy_level == "high":
            directive.caption_style = "word_pop"
        elif directive.energy_level == "low":
            directive.caption_style = "typewriter"
        else:
            directive.caption_style = "word_pop"  # Default to word_pop for engagement

        # Set transitions based on scene position
        if scene_index == 0:
            directive.transition_in = "fade"
        else:
            directive.transition_in = "fade" if directive.energy_level == "low" else "zoom"

        if scene_index == total_scenes - 1:
            directive.transition_out = "fade"
        else:
            directive.transition_out = "fade"

        return directive

    def _analyze_with_ai(
        self,
        narration: str,
        visual_suggestion: str,
        scene_index: int,
        total_scenes: int,
    ) -> AnimationDirective:
        """
        AI-powered scene analysis using Gemini.

        Falls back to rule-based if AI fails.

        Args:
            narration: Scene narration
            visual_suggestion: Visual suggestion
            scene_index: Scene index
            total_scenes: Total scenes

        Returns:
            AnimationDirective
        """
        if not self._ai_agent:
            return self._analyze_rule_based(
                narration, visual_suggestion, scene_index, total_scenes
            )

        try:
            from agents import Runner

            prompt = f"""Analyze this scene and provide animation directives:

Scene {scene_index + 1} of {total_scenes}

Narration: {narration}

Visual Suggestion: {visual_suggestion}

Provide animation directives for this scene. Consider:
- Is this an intro, ranking, or outro scene?
- What's the energy level?
- Which words should be emphasized?
- What caption style fits best?
"""

            result = Runner.run_sync(self._ai_agent, prompt)

            if result.final_output:
                return result.final_output

        except Exception as e:
            print(f"AI analysis failed, using rule-based: {e}")

        return self._analyze_rule_based(
            narration, visual_suggestion, scene_index, total_scenes
        )

    def get_directives_for_script(
        self,
        scenes: List[dict],
    ) -> List[AnimationDirective]:
        """
        Analyze all scenes in a script.

        Args:
            scenes: List of scene dicts with narration and visual_suggestion

        Returns:
            List of AnimationDirective for each scene
        """
        directives = []
        total_scenes = len(scenes)

        for i, scene in enumerate(scenes):
            directive = self.analyze_scene(
                narration=scene.get("narration", ""),
                visual_suggestion=scene.get("visual_suggestion", ""),
                scene_index=i,
                total_scenes=total_scenes,
            )
            directives.append(directive)

        return directives


if __name__ == "__main__":
    # Test the scene director
    print("Testing SceneDirector...")

    director = SceneDirector(use_ai=False)

    # Test scenes
    test_scenes = [
        {
            "narration": "Welcome to our countdown of the top 10 most epic anime moments of all time!",
            "visual_suggestion": "anime epic montage",
        },
        {
            "narration": "Number 5: The legendary battle between Naruto and Sasuke at the Valley of the End.",
            "visual_suggestion": "Naruto vs Sasuke fight scene",
        },
        {
            "narration": "This emotional moment truly showcased the power of their friendship.",
            "visual_suggestion": "emotional anime scene",
        },
        {
            "narration": "Thanks for watching! Don't forget to like and subscribe!",
            "visual_suggestion": "outro graphics",
        },
    ]

    directives = director.get_directives_for_script(test_scenes)

    for i, (scene, directive) in enumerate(zip(test_scenes, directives)):
        print(f"\n--- Scene {i + 1} ---")
        print(f"Narration: {scene['narration'][:50]}...")
        print(f"Caption Style: {directive.caption_style}")
        print(f"Motion Graphic: {directive.motion_graphic}")
        print(f"Energy Level: {directive.energy_level}")
        print(f"Ranking: {directive.ranking_number}")
        print(f"Is Intro: {directive.is_intro}")
        print(f"Is Outro: {directive.is_outro}")
        print(f"Emphasis Words: {directive.emphasis_words}")

    print("\nSceneDirector tests complete!")
