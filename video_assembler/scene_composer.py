"""Scene composer for combining video clips, graphics, and audio."""

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from typing import Optional, Tuple

from .config import DEFAULT_CONFIG
from .motion_graphics import MotionGraphics
from .effects import Effects


class SceneComposer:
    """Composes individual scenes by combining clips, graphics, and audio."""

    def __init__(self, resolution: Tuple[int, int] = None):
        """
        Initialize the scene composer.

        Args:
            resolution: Video resolution (width, height)
        """
        self.resolution = resolution or DEFAULT_CONFIG["resolution"]
        self.motion_graphics = MotionGraphics(self.resolution)
        self.effects = Effects()

    def compose_scene(
        self,
        video_path: str,
        narration_text: str,
        audio_clip: Optional[AudioFileClip] = None,
        duration: Optional[float] = None,
    ) -> CompositeVideoClip:
        """
        Compose a complete scene with video, text overlay, and audio.

        Args:
            video_path: Path to the background video
            narration_text: Text to overlay as caption
            audio_clip: Audio clip for this scene
            duration: Target duration (uses audio duration if not specified)

        Returns:
            Composed scene as CompositeVideoClip
        """
        # Load video
        video = VideoFileClip(video_path)

        # Determine duration
        if duration is None and audio_clip is not None:
            duration = audio_clip.duration
        elif duration is None:
            duration = video.duration

        # Resize and set duration
        video = video.resized(self.resolution)
        video = self.effects.set_clip_duration(video, duration)

        # Create text overlay
        text_overlay = self.motion_graphics.create_text_overlay(
            text=narration_text,
            duration=duration,
            position="bottom",
        )

        # Composite video and text
        composed = CompositeVideoClip(
            [video, text_overlay],
            size=self.resolution,
        )

        # Add audio if provided
        if audio_clip is not None:
            composed = composed.with_audio(audio_clip)

        return composed

    def compose_title_scene(
        self,
        title: str,
        subtitle: str = "",
        duration: float = 3.0,
        audio_clip: Optional[AudioFileClip] = None,
    ) -> CompositeVideoClip:
        """
        Compose a title card scene.

        Args:
            title: Main title text
            subtitle: Subtitle text
            duration: Scene duration
            audio_clip: Optional audio

        Returns:
            Title scene clip
        """
        title_card = self.motion_graphics.create_title_card(
            title=title,
            subtitle=subtitle,
            duration=duration,
        )

        if audio_clip is not None:
            title_card = title_card.with_audio(audio_clip)

        return title_card

    def compose_ranking_scene(
        self,
        rank: int,
        title: str,
        subtitle: str,
        video_path: str,
        narration_text: str,
        audio_clip: Optional[AudioFileClip] = None,
        title_duration: float = 2.0,
    ) -> CompositeVideoClip:
        """
        Compose a complete ranking scene with title card + content.

        Args:
            rank: Ranking number
            title: Title for the ranking
            subtitle: Subtitle (e.g., anime name)
            video_path: Path to background video
            narration_text: Narration text for captions
            audio_clip: Audio for the scene
            title_duration: Duration of the title card portion

        Returns:
            Complete ranking scene
        """
        # Calculate content duration from audio
        if audio_clip is not None:
            total_duration = audio_clip.duration
            content_duration = total_duration - title_duration
        else:
            content_duration = 5.0
            total_duration = title_duration + content_duration

        # Create ranking title card
        ranking_card = self.motion_graphics.create_ranking_card(
            rank=rank,
            title=title,
            subtitle=subtitle,
            duration=title_duration,
        )

        # Load and prepare content video
        video = VideoFileClip(video_path)
        video = video.resized(self.resolution)
        video = self.effects.set_clip_duration(video, content_duration)

        # Add caption overlay
        caption = self.motion_graphics.create_text_overlay(
            text=narration_text,
            duration=content_duration,
            position="bottom",
        )

        content_scene = CompositeVideoClip(
            [video, caption],
            size=self.resolution,
        )

        # Concatenate title card and content
        full_scene = concatenate_videoclips(
            [ranking_card, content_scene],
            method="compose",
        )

        # Add audio
        if audio_clip is not None:
            full_scene = full_scene.with_audio(audio_clip)

        return full_scene

    def add_captions(
        self,
        video_clip: CompositeVideoClip,
        text: str,
        position: str = "bottom",
    ) -> CompositeVideoClip:
        """
        Add caption text overlay to an existing video clip.

        Args:
            video_clip: Video clip to add captions to
            text: Caption text
            position: Caption position

        Returns:
            Video with captions added
        """
        caption = self.motion_graphics.create_text_overlay(
            text=text,
            duration=video_clip.duration,
            position=position,
        )

        return CompositeVideoClip(
            [video_clip, caption],
            size=self.resolution,
        )


if __name__ == "__main__":
    # Test scene composer
    composer = SceneComposer()

    # Create a simple title scene
    title_scene = composer.compose_title_scene(
        title="Top 10 Anime Moments",
        subtitle="That Will Make You Cry",
        duration=3.0,
    )
    print(f"Created title scene: {title_scene.duration}s")
