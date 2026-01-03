"""Scene composer for combining video clips, graphics, and audio."""

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from typing import Optional, Tuple, List

from .config import DEFAULT_CONFIG
from .motion_graphics import MotionGraphics
from .text_animations import TextAnimations
from .scene_director import SceneDirector, AnimationDirective
from .effects import Effects


class SceneComposer:
    """Composes individual scenes by combining clips, graphics, and audio."""

    def __init__(
        self,
        resolution: Tuple[int, int] = None,
        use_ai_director: bool = False,
    ):
        """
        Initialize the scene composer.

        Args:
            resolution: Video resolution (width, height)
            use_ai_director: Whether to use AI for scene analysis
        """
        self.resolution = resolution or DEFAULT_CONFIG["resolution"]
        self.motion_graphics = MotionGraphics(self.resolution)
        self.text_animations = TextAnimations(self.resolution)
        self.scene_director = SceneDirector(use_ai=use_ai_director)
        self.effects = Effects()

    def compose_scene(
        self,
        video_path: str,
        narration_text: str,
        audio_clip: Optional[AudioFileClip] = None,
        duration: Optional[float] = None,
        scene_data: Optional[dict] = None,
        scene_index: int = 0,
        total_scenes: int = 1,
        use_animated_captions: bool = True,
    ) -> CompositeVideoClip:
        """
        Compose a complete scene with video, animated text overlay, and audio.

        Args:
            video_path: Path to the background video
            narration_text: Text to overlay as caption
            audio_clip: Audio clip for this scene
            duration: Target duration (uses audio duration if not specified)
            scene_data: Full scene dict for directive analysis
            scene_index: Index of this scene
            total_scenes: Total number of scenes
            use_animated_captions: Whether to use animated word-by-word captions

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

        # Get animation directives from scene director
        directive = self.scene_director.analyze_scene(
            narration=narration_text,
            visual_suggestion=scene_data.get("visual_suggestion", "") if scene_data else "",
            scene_index=scene_index,
            total_scenes=total_scenes,
        )

        # Create caption based on directive
        if use_animated_captions and directive.caption_style == "word_pop":
            # Use word-by-word pop-in captions
            text_overlay = self.text_animations.create_word_by_word_caption(
                text=narration_text,
                duration=duration,
                position="bottom",
                emphasis_words=directive.emphasis_words,
            )
        elif use_animated_captions and directive.caption_style == "typewriter":
            # Use typewriter effect for calmer scenes
            text_overlay = self.text_animations.create_typewriter_text(
                text=narration_text,
                duration=duration,
                position="bottom",
            )
        else:
            # Fall back to static overlay
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

    def compose_scene_with_graphics(
        self,
        video_path: str,
        narration_text: str,
        scene_data: dict,
        scene_index: int,
        total_scenes: int,
        duration: float,
        audio_clip: Optional[AudioFileClip] = None,
    ) -> CompositeVideoClip:
        """
        Compose a scene with motion graphics based on scene director analysis.

        Automatically adds ranking cards, title cards, etc. based on content.

        Args:
            video_path: Path to background video
            narration_text: Narration text
            scene_data: Scene data dict
            scene_index: Scene index
            total_scenes: Total scenes
            duration: Scene duration
            audio_clip: Optional audio

        Returns:
            Composed scene with graphics
        """
        # Get animation directives
        directive = self.scene_director.analyze_scene(
            narration=narration_text,
            visual_suggestion=scene_data.get("visual_suggestion", ""),
            scene_index=scene_index,
            total_scenes=total_scenes,
        )

        clips_to_concat = []
        remaining_duration = duration

        # Add motion graphic intro if recommended
        if directive.motion_graphic == "ranking_card" and directive.ranking_number:
            # Add animated ranking card
            ranking_duration = min(2.0, duration * 0.3)
            ranking_card = self.motion_graphics.create_animated_ranking_card(
                rank=directive.ranking_number,
                title=self._extract_title_from_narration(narration_text),
                duration=ranking_duration,
            )
            clips_to_concat.append(ranking_card)
            remaining_duration -= ranking_duration

        elif directive.motion_graphic == "title_card" and directive.is_intro:
            # Add animated title card for intro
            title_duration = min(2.5, duration * 0.4)
            title_card = self.motion_graphics.create_animated_title_card(
                title=self._extract_title_from_narration(narration_text),
                duration=title_duration,
            )
            clips_to_concat.append(title_card)
            remaining_duration -= title_duration

        # Compose main content scene
        content_scene = self.compose_scene(
            video_path=video_path,
            narration_text=narration_text,
            duration=remaining_duration,
            scene_data=scene_data,
            scene_index=scene_index,
            total_scenes=total_scenes,
            use_animated_captions=True,
        )
        clips_to_concat.append(content_scene)

        # Add subscribe reminder for outro
        if directive.motion_graphic == "subscribe" and directive.is_outro:
            # Overlay subscribe reminder on last scene
            subscribe = self.motion_graphics.create_subscribe_reminder(
                duration=min(3.0, remaining_duration),
            ).with_start(max(0, remaining_duration - 3.0))

            # Composite subscribe over content
            content_scene = CompositeVideoClip(
                [content_scene, subscribe],
                size=self.resolution,
            )
            clips_to_concat[-1] = content_scene

        # Concatenate all clips
        if len(clips_to_concat) > 1:
            final_scene = concatenate_videoclips(clips_to_concat, method="compose")
        else:
            final_scene = clips_to_concat[0]

        # Add audio if provided
        if audio_clip is not None:
            final_scene = final_scene.with_audio(audio_clip)

        return final_scene

    def _extract_title_from_narration(self, narration: str, max_words: int = 6) -> str:
        """Extract a title from narration text."""
        # Remove common intro phrases
        clean = narration.lower()
        for phrase in ["welcome to", "today we", "in this video", "let's"]:
            clean = clean.replace(phrase, "")

        # Get first few words
        words = narration.split()[:max_words]
        title = " ".join(words)

        # Add ellipsis if truncated
        if len(narration.split()) > max_words:
            title += "..."

        return title

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
