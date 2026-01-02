"""Motion graphics generator for text overlays and title cards."""

from moviepy import (
    TextClip,
    ColorClip,
    CompositeVideoClip,
)
from typing import Optional, Tuple

from .config import DEFAULT_CONFIG


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


if __name__ == "__main__":
    # Test motion graphics
    mg = MotionGraphics()

    # Create and preview a title card
    title_card = mg.create_title_card(
        title="Top 10 Anime Betrayals",
        subtitle="You Won't Believe #1!",
        duration=3.0,
    )
    print(f"Created title card: {title_card.duration}s")

    # Create ranking card
    ranking = mg.create_ranking_card(
        rank=10,
        title="Guts's Entire Life",
        subtitle="Berserk",
        duration=3.0,
    )
    print(f"Created ranking card: {ranking.duration}s")
