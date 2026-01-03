"""Motion graphics generator for text overlays and title cards."""

import math
from moviepy import (
    TextClip,
    ColorClip,
    CompositeVideoClip,
)
from moviepy.video.fx import FadeIn, FadeOut
from typing import Optional, Tuple, List

from .config import DEFAULT_CONFIG


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Ease-out-back for bounce effect."""
    t = t - 1
    return t * t * ((overshoot + 1) * t + overshoot) + 1


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out for spring effect."""
    if t == 0 or t == 1:
        return t
    p = 0.3
    s = p / 4
    return pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out for smooth deceleration."""
    return 1 - pow(1 - t, 3)


class MotionGraphics:
    """Generates motion graphics like text overlays and title cards."""

    def __init__(self, resolution: Tuple[int, int] = None):
        """
        Initialize the motion graphics generator.

        Args:
            resolution: Video resolution (width, height)
        """
        self.resolution = resolution or DEFAULT_CONFIG["resolution"]
        self.width, self.height = self.resolution

    def create_text_overlay(
        self,
        text: str,
        duration: float,
        position: str = "bottom",
        font_size: int = None,
        color: str = None,
        stroke_color: str = None,
        stroke_width: int = None,
    ) -> CompositeVideoClip:
        """
        Create a text overlay (caption).

        Args:
            text: Text to display
            duration: Duration in seconds
            position: Position ("bottom", "top", "center")
            font_size: Font size (default from config)
            color: Text color
            stroke_color: Stroke/outline color
            stroke_width: Stroke width

        Returns:
            CompositeVideoClip with text overlay
        """
        font_size = font_size or DEFAULT_CONFIG["caption_font_size"]
        color = color or DEFAULT_CONFIG["text_color"]
        stroke_color = stroke_color or DEFAULT_CONFIG["text_stroke_color"]
        stroke_width = stroke_width or DEFAULT_CONFIG["text_stroke_width"]

        # Position the text
        if position == "bottom":
            pos = ("center", self.height - 150)
        elif position == "top":
            pos = ("center", 50)
        else:
            pos = ("center", "center")

        # Create text clip
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method="caption",
            size=(self.width - 100, None),  # Leave margins
            text_align="center",
            duration=duration,
        ).with_position(pos)

        return text_clip

    def create_title_card(
        self,
        title: str,
        subtitle: str = "",
        duration: float = 3.0,
        bg_color: Tuple[int, int, int] = (0, 0, 0),
    ) -> CompositeVideoClip:
        """
        Create a title card with main title and optional subtitle.

        Args:
            title: Main title text
            subtitle: Subtitle text (optional)
            duration: Duration in seconds
            bg_color: Background color (RGB tuple)

        Returns:
            CompositeVideoClip with title card
        """
        # Background
        bg = ColorClip(
            size=self.resolution,
            color=bg_color,
            duration=duration,
        )

        # Position title
        if subtitle:
            title_pos = ("center", self.height // 2 - 80)
        else:
            title_pos = ("center", "center")

        # Main title
        title_clip = TextClip(
            text=title,
            font_size=DEFAULT_CONFIG["title_font_size"],
            color=DEFAULT_CONFIG["text_color"],
            stroke_color=DEFAULT_CONFIG["text_stroke_color"],
            stroke_width=4,
            method="caption",
            size=(self.width - 200, None),
            text_align="center",
            duration=duration,
        ).with_position(title_pos)

        clips = [bg, title_clip]

        # Add subtitle if provided
        if subtitle:
            subtitle_clip = TextClip(
                text=subtitle,
                font_size=int(DEFAULT_CONFIG["title_font_size"] * 0.5),
                color="#cccccc",
                method="caption",
                size=(self.width - 200, None),
                text_align="center",
                duration=duration,
            ).with_position(("center", self.height // 2 + 50))
            clips.append(subtitle_clip)

        return CompositeVideoClip(clips, size=self.resolution)

    def create_ranking_card(
        self,
        rank: int,
        title: str,
        subtitle: str = "",
        duration: float = 3.0,
    ) -> CompositeVideoClip:
        """
        Create a ranking title card (e.g., "#10 - Title").

        Args:
            rank: Ranking number
            title: Title text
            subtitle: Subtitle (e.g., anime name)
            duration: Duration in seconds

        Returns:
            CompositeVideoClip with ranking card
        """
        # Background
        bg = ColorClip(
            size=self.resolution,
            color=(20, 20, 30),
            duration=duration,
        )

        # Rank number
        rank_text = f"#{rank}"
        rank_clip = TextClip(
            text=rank_text,
            font_size=150,
            color="#ff4444",
            stroke_color="white",
            stroke_width=4,
            method="label",
            duration=duration,
        ).with_position((100, self.height // 2 - 100))

        # Title
        title_clip = TextClip(
            text=title,
            font_size=70,
            color="white",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(self.width - 400, None),
            text_align="left",
            duration=duration,
        ).with_position((350, self.height // 2 - 50))

        clips = [bg, rank_clip, title_clip]

        # Subtitle
        if subtitle:
            sub_clip = TextClip(
                text=subtitle,
                font_size=40,
                color="#aaaaaa",
                method="label",
                duration=duration,
            ).with_position((350, self.height // 2 + 50))
            clips.append(sub_clip)

        return CompositeVideoClip(clips, size=self.resolution)

    def create_solid_background(
        self,
        color: Tuple[int, int, int],
        duration: float,
    ) -> ColorClip:
        """
        Create a solid color background.

        Args:
            color: RGB color tuple
            duration: Duration in seconds

        Returns:
            ColorClip background
        """
        return ColorClip(
            size=self.resolution,
            color=color,
            duration=duration,
        )

    # ==========================================
    # ANIMATED MOTION GRAPHICS (Bold YouTube Style)
    # ==========================================

    def create_animated_title_card(
        self,
        title: str,
        subtitle: str = "",
        duration: float = 3.0,
        bg_color: Tuple[int, int, int] = (15, 15, 25),
        title_color: str = "#FFFFFF",
        accent_color: str = "#FF4444",
        animation_duration: float = 0.5,
    ) -> CompositeVideoClip:
        """
        Create an animated title card with bounce/scale effect.

        Title pops in with overshoot animation.

        Args:
            title: Main title text
            subtitle: Subtitle text (optional)
            duration: Total duration
            bg_color: Background color
            title_color: Title text color
            accent_color: Accent color for effects
            animation_duration: Duration of entrance animation

        Returns:
            Animated title card
        """
        clips = []

        # Background
        bg = ColorClip(
            size=self.resolution,
            color=bg_color,
            duration=duration,
        )
        clips.append(bg)

        # Accent bar at bottom (static, simpler)
        accent_bar = ColorClip(
            size=(self.width, 8),
            color=self._hex_to_rgb(accent_color),
            duration=duration,
        ).with_position((0, self.height - 100)).with_effects([FadeIn(animation_duration)])
        clips.append(accent_bar)

        # Title with simple fade in
        title_clip = TextClip(
            text=title,
            font_size=int(DEFAULT_CONFIG["title_font_size"] * 1.2),
            color=title_color,
            stroke_color=accent_color,
            stroke_width=4,
            method="caption",
            size=(self.width - 200, None),
            text_align="center",
            duration=duration,
        ).with_position(("center", self.height // 2 - 50)).with_effects([
            FadeIn(animation_duration)
        ])
        clips.append(title_clip)

        # Subtitle
        if subtitle:
            subtitle_clip = TextClip(
                text=subtitle,
                font_size=int(DEFAULT_CONFIG["title_font_size"] * 0.5),
                color="#AAAAAA",
                method="caption",
                size=(self.width - 200, None),
                text_align="center",
                duration=duration - 0.3,
            ).with_position(("center", self.height // 2 + 60)).with_start(0.3).with_effects([
                FadeIn(0.3)
            ])
            clips.append(subtitle_clip)

        return CompositeVideoClip(clips, size=self.resolution).with_effects([FadeOut(0.3)])

    def create_animated_ranking_card(
        self,
        rank: int,
        title: str,
        subtitle: str = "",
        duration: float = 2.5,
        rank_color: str = "#FF4444",
        title_color: str = "#FFFFFF",
        bg_color: Tuple[int, int, int] = (20, 20, 35),
        slam_effect: bool = True,
    ) -> CompositeVideoClip:
        """
        Create animated ranking card with fade-in effects.

        Simplified version to avoid positioning issues.

        Args:
            rank: Ranking number
            title: Title text
            subtitle: Subtitle (e.g., anime name)
            duration: Total duration
            rank_color: Color for the rank number
            title_color: Title text color
            bg_color: Background color
            slam_effect: Not used (kept for API compatibility)

        Returns:
            Animated ranking card
        """
        clips = []
        animation_duration = 0.4

        # Background
        bg = ColorClip(
            size=self.resolution,
            color=bg_color,
            duration=duration,
        )
        clips.append(bg)

        # Flash effect
        flash = ColorClip(
            size=self.resolution,
            color=(255, 255, 255),
            duration=0.15,
        ).with_start(0).with_effects([FadeIn(0.05), FadeOut(0.1)])
        clips.append(flash)

        # Rank number - static position with fade in
        rank_text = f"#{rank}"
        rank_clip = TextClip(
            text=rank_text,
            font_size=200,
            color=rank_color,
            stroke_color="white",
            stroke_width=6,
            method="label",
            duration=duration,
        ).with_position((150, self.height // 2 - 100)).with_effects([FadeIn(animation_duration)])
        clips.append(rank_clip)

        # Title - static position with delayed fade in
        title_clip = TextClip(
            text=title,
            font_size=70,
            color=title_color,
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(self.width - 500, None),
            text_align="left",
            duration=duration - 0.2,
        ).with_position((400, self.height // 2 - 40)).with_start(0.2).with_effects([
            FadeIn(animation_duration)
        ])
        clips.append(title_clip)

        # Subtitle
        if subtitle:
            sub_clip = TextClip(
                text=subtitle,
                font_size=40,
                color="#888888",
                method="label",
                duration=duration - 0.4,
            ).with_position((400, self.height // 2 + 60)).with_start(0.4).with_effects([
                FadeIn(0.3)
            ])
            clips.append(sub_clip)

        return CompositeVideoClip(clips, size=self.resolution).with_effects([FadeOut(0.2)])

    def create_lower_third(
        self,
        name: str,
        title: str = "",
        duration: float = 4.0,
        bar_color: str = "#FF4444",
        animation_duration: float = 0.4,
    ) -> CompositeVideoClip:
        """
        Create lower third bar for names/titles with fade effects.

        Args:
            name: Main name/text
            title: Secondary title
            duration: Total duration
            bar_color: Color of the animated bar
            animation_duration: Duration of entrance animation

        Returns:
            Animated lower third
        """
        clips = []
        bar_height = 100
        bar_y = self.height - 180

        # Transparent background
        bg = ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration,
        ).with_opacity(0)
        clips.append(bg)

        # Bar background - static with fade
        bar_bg = ColorClip(
            size=(600, bar_height),
            color=(30, 30, 40),
            duration=duration,
        ).with_position((0, bar_y)).with_effects([FadeIn(animation_duration)])
        clips.append(bar_bg)

        # Color accent bar
        accent = ColorClip(
            size=(8, bar_height),
            color=self._hex_to_rgb(bar_color),
            duration=duration,
        ).with_position((0, bar_y)).with_effects([FadeIn(animation_duration)])
        clips.append(accent)

        # Name text
        name_clip = TextClip(
            text=name,
            font_size=45,
            color="white",
            method="label",
            duration=duration - 0.2,
        ).with_position((30, bar_y + 15)).with_start(0.2).with_effects([
            FadeIn(0.2)
        ])
        clips.append(name_clip)

        # Title text
        if title:
            title_clip = TextClip(
                text=title,
                font_size=28,
                color="#AAAAAA",
                method="label",
                duration=duration - 0.3,
            ).with_position((30, bar_y + 55)).with_start(0.3).with_effects([
                FadeIn(0.2)
            ])
            clips.append(title_clip)

        return CompositeVideoClip(clips, size=self.resolution).with_effects([FadeOut(0.3)])

    def create_subscribe_reminder(
        self,
        duration: float = 3.0,
        position: str = "bottom_right",
    ) -> CompositeVideoClip:
        """
        Create subscribe reminder overlay with fade effects.

        Args:
            duration: Total duration
            position: Position ("bottom_right", "bottom_left")

        Returns:
            Subscribe reminder clip
        """
        clips = []
        animation_duration = 0.3

        # Transparent background
        bg = ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration,
        ).with_opacity(0)
        clips.append(bg)

        # Subscribe button background
        button_width, button_height = 200, 50

        if position == "bottom_right":
            final_x = self.width - button_width - 50
        else:
            final_x = 50
        final_y = self.height - 120

        button_bg = ColorClip(
            size=(button_width, button_height),
            color=(255, 0, 0),
            duration=duration,
        ).with_position((final_x, final_y)).with_effects([FadeIn(animation_duration)])
        clips.append(button_bg)

        # Subscribe text
        sub_text = TextClip(
            text="SUBSCRIBE",
            font_size=24,
            color="white",
            method="label",
            duration=duration,
        ).with_position((final_x + 40, final_y + 12)).with_effects([FadeIn(animation_duration)])
        clips.append(sub_text)

        return CompositeVideoClip(clips, size=self.resolution).with_effects([FadeOut(0.2)])

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


if __name__ == "__main__":
    # Test motion graphics
    mg = MotionGraphics()

    # Create and preview a title card
    title_card = mg.create_title_card(
        title="Top 10 Anime Betrayals",
        subtitle="You Won't Believe #1!",
        duration=3.0,
    )
    print(f"Created static title card: {title_card.duration}s")

    # Create ranking card
    ranking = mg.create_ranking_card(
        rank=10,
        title="Guts's Entire Life",
        subtitle="Berserk",
        duration=3.0,
    )
    print(f"Created static ranking card: {ranking.duration}s")

    # Test animated graphics
    print("\nTesting ANIMATED motion graphics...")

    animated_title = mg.create_animated_title_card(
        title="Top 10 Anime Moments",
        subtitle="That Will Blow Your Mind!",
        duration=3.0,
    )
    print(f"Created animated title card: {animated_title.duration}s")

    animated_ranking = mg.create_animated_ranking_card(
        rank=5,
        title="The Ultimate Sacrifice",
        subtitle="Attack on Titan",
        duration=2.5,
    )
    print(f"Created animated ranking card: {animated_ranking.duration}s")

    lower_third = mg.create_lower_third(
        name="Naruto Uzumaki",
        title="The Seventh Hokage",
        duration=4.0,
    )
    print(f"Created lower third: {lower_third.duration}s")

    subscribe = mg.create_subscribe_reminder(duration=3.0)
    print(f"Created subscribe reminder: {subscribe.duration}s")

    print("\nAll motion graphics tests passed!")
