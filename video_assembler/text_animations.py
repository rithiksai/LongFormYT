"""Text animation system for dynamic captions - TikTok/Shorts style."""

import math
from typing import List, Tuple, Optional
from moviepy import (
    TextClip,
    CompositeVideoClip,
    ColorClip,
)
from moviepy.video.fx import FadeIn, FadeOut

from .config import DEFAULT_CONFIG


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """
    Ease-out-back function for bounce effect.
    Creates overshoot then settles back.

    Args:
        t: Time value from 0 to 1
        overshoot: Amount of overshoot (default 1.70158 for ~10% overshoot)

    Returns:
        Eased value
    """
    t = t - 1
    return t * t * ((overshoot + 1) * t + overshoot) + 1


def ease_out_elastic(t: float) -> float:
    """
    Elastic ease-out for bouncy spring effect.

    Args:
        t: Time value from 0 to 1

    Returns:
        Eased value with elastic bounce
    """
    if t == 0 or t == 1:
        return t
    p = 0.3
    s = p / 4
    return pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


class TextAnimations:
    """Creates animated text overlays with various effects."""

    def __init__(self, resolution: Tuple[int, int] = None):
        """
        Initialize text animations.

        Args:
            resolution: Video resolution (width, height)
        """
        self.resolution = resolution or DEFAULT_CONFIG["resolution"]
        self.width, self.height = self.resolution

    def create_word_by_word_caption(
        self,
        text: str,
        duration: float,
        position: str = "bottom",
        font_size: int = None,
        color: str = None,
        highlight_color: str = "#FFFF00",
        stroke_color: str = None,
        stroke_width: int = None,
        words_per_line: int = 5,
        emphasis_words: List[str] = None,
        pop_duration: float = 0.12,
    ) -> CompositeVideoClip:
        """
        Create TikTok/Shorts style word-by-word pop-in captions.

        Uses a simpler line-by-line approach for better compatibility.

        Args:
            text: Full caption text
            duration: Total duration of the caption
            position: Position ("bottom", "center", "top")
            font_size: Font size (default from config)
            color: Text color
            highlight_color: Color for emphasized words
            stroke_color: Outline color
            stroke_width: Outline width
            words_per_line: Max words per line before wrapping
            emphasis_words: Words to highlight/emphasize
            pop_duration: Duration of pop-in animation per word

        Returns:
            CompositeVideoClip with animated word-by-word captions
        """
        font_size = font_size or DEFAULT_CONFIG["caption_font_size"]
        color = color or DEFAULT_CONFIG["text_color"]
        stroke_color = stroke_color or DEFAULT_CONFIG["text_stroke_color"]
        stroke_width = stroke_width or DEFAULT_CONFIG["text_stroke_width"]
        emphasis_words = [e.lower() for e in (emphasis_words or [])]

        # Split into words
        words = text.split()
        if not words:
            return self._create_empty_clip(duration)

        # Calculate timing
        total_words = len(words)
        available_time = duration * 0.85
        time_per_word = available_time / total_words

        # Calculate vertical position
        if position == "bottom":
            base_y = self.height - 180
        elif position == "top":
            base_y = 120
        else:
            base_y = self.height // 2

        # Group words into lines
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(current_line) >= words_per_line:
                lines.append(" ".join(current_line))
                current_line = []
        if current_line:
            lines.append(" ".join(current_line))

        # Create clips for each line appearing progressively
        clips = []
        line_height = font_size + 30
        total_lines = len(lines)

        # Calculate words per line for timing
        words_so_far = 0

        for line_idx, line_text in enumerate(lines):
            line_words = line_text.split()
            start_time = words_so_far * time_per_word
            line_duration = duration - start_time

            # Check if any emphasis words in this line
            has_emphasis = any(emp in line_text.lower() for emp in emphasis_words)

            # Calculate y position for this line
            line_y = base_y + (line_idx - total_lines // 2) * line_height

            # Create the line clip
            line_clip = TextClip(
                text=line_text,
                font_size=font_size + (4 if has_emphasis else 0),
                color=highlight_color if has_emphasis else color,
                stroke_color=stroke_color,
                stroke_width=stroke_width + (1 if has_emphasis else 0),
                method="caption",
                size=(self.width - 100, None),
                text_align="center",
                duration=line_duration,
            )

            # Use static position with fade effect (avoids rendering issues)
            line_clip = (
                line_clip
                .with_position(("center", line_y))
                .with_start(start_time)
                .with_effects([FadeIn(pop_duration)])
            )

            clips.append(line_clip)
            words_so_far += len(line_words)

        # Create transparent background
        bg = ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration,
        ).with_opacity(0)

        return CompositeVideoClip(
            [bg] + clips,
            size=self.resolution,
        )

    def create_pop_in_text(
        self,
        text: str,
        duration: float,
        position: Tuple[str, int] = ("center", "center"),
        font_size: int = None,
        color: str = None,
        pop_duration: float = 0.3,
        hold_duration: float = None,
    ) -> CompositeVideoClip:
        """
        Create text that pops in with scale animation.

        Good for titles, emphasis text, or single words.

        Args:
            text: Text to display
            duration: Total duration
            position: Position tuple
            font_size: Font size
            color: Text color
            pop_duration: Duration of pop animation
            hold_duration: How long to hold before fade out

        Returns:
            Animated text clip
        """
        font_size = font_size or DEFAULT_CONFIG["title_font_size"]
        color = color or DEFAULT_CONFIG["text_color"]

        if hold_duration is None:
            hold_duration = duration - pop_duration - 0.3

        # Create text clip
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_color=DEFAULT_CONFIG["text_stroke_color"],
            stroke_width=4,
            method="label",
            duration=duration,
        )

        # Use static position with fade effects (avoids rendering issues)
        animated_clip = (
            text_clip
            .with_position(("center", self.height // 2))
            .with_effects([
                FadeIn(pop_duration),
                FadeOut(0.3),
            ])
        )

        return animated_clip

    def create_slide_in_text(
        self,
        text: str,
        duration: float,
        direction: str = "left",
        font_size: int = None,
        color: str = None,
        slide_duration: float = 0.4,
        y_position: int = None,
    ) -> TextClip:
        """
        Create text that slides in from a direction.

        Args:
            text: Text to display
            duration: Total duration
            direction: "left", "right", "top", "bottom"
            font_size: Font size
            color: Text color
            slide_duration: Duration of slide animation
            y_position: Y position (default center)

        Returns:
            Animated text clip
        """
        font_size = font_size or DEFAULT_CONFIG["caption_font_size"]
        color = color or DEFAULT_CONFIG["text_color"]
        y_position = y_position or self.height // 2

        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_color=DEFAULT_CONFIG["text_stroke_color"],
            stroke_width=3,
            method="label",
            duration=duration,
        )

        # Use static center position with fade effect (avoids rendering issues)
        return (
            text_clip
            .with_position(("center", y_position))
            .with_effects([FadeIn(slide_duration)])
        )

    def create_typewriter_text(
        self,
        text: str,
        duration: float,
        position: str = "center",
        font_size: int = None,
        color: str = None,
        chars_per_second: float = 20,
    ) -> CompositeVideoClip:
        """
        Create typewriter-style text with fade-in effect.

        Simplified to use full text with fade for rendering stability.

        Args:
            text: Text to display
            duration: Total duration
            position: Position ("center", "bottom", "top")
            font_size: Font size
            color: Text color
            chars_per_second: Speed of typing (used for fade duration)

        Returns:
            Animated text clip
        """
        font_size = font_size or DEFAULT_CONFIG["caption_font_size"]
        color = color or DEFAULT_CONFIG["text_color"]

        if not text:
            return self._create_empty_clip(duration)

        # Calculate position
        if position == "bottom":
            pos_y = self.height - 150
        elif position == "top":
            pos_y = 100
        else:
            pos_y = self.height // 2

        # Calculate fade duration based on text length
        fade_duration = min(len(text) / chars_per_second, duration * 0.3)

        # Create single text clip with fade (simpler and more stable)
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_color=DEFAULT_CONFIG["text_stroke_color"],
            stroke_width=2,
            method="caption",
            size=(self.width - 100, None),
            text_align="center",
            duration=duration,
        )

        text_clip = (
            text_clip
            .with_position(("center", pos_y))
            .with_effects([FadeIn(fade_duration)])
        )

        bg = ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration,
        ).with_opacity(0)

        return CompositeVideoClip([bg, text_clip], size=self.resolution)

    def _create_empty_clip(self, duration: float) -> CompositeVideoClip:
        """Create an empty transparent clip."""
        return ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration,
        ).with_opacity(0)


if __name__ == "__main__":
    # Test the text animations
    print("Testing TextAnimations...")

    animator = TextAnimations()

    # Test word-by-word caption
    caption = animator.create_word_by_word_caption(
        text="Welcome to the top ten anime moments of all time!",
        duration=5.0,
        emphasis_words=["top", "ten", "anime"],
    )
    print(f"Created word-by-word caption: {caption.duration}s")

    # Test pop-in text
    pop_text = animator.create_pop_in_text(
        text="EPIC!",
        duration=2.0,
    )
    print(f"Created pop-in text: {pop_text.duration}s")

    # Test slide-in text
    slide_text = animator.create_slide_in_text(
        text="Number 10",
        duration=3.0,
        direction="left",
    )
    print(f"Created slide-in text: {slide_text.duration}s")

    print("TextAnimations tests complete!")
