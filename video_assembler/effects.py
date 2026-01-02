"""Video effects and transitions."""

from moviepy import (
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx import FadeIn, FadeOut

from .config import DEFAULT_CONFIG


class Effects:
    """Video effects and transitions library."""

    @staticmethod
    def apply_fade_in(clip, duration: float = None):
        """
        Apply fade-in effect to a clip.

        Args:
            clip: Video clip to apply effect to
            duration: Fade duration in seconds

        Returns:
            Clip with fade-in effect
        """
        duration = duration or DEFAULT_CONFIG["fade_duration"]
        return clip.with_effects([FadeIn(duration)])

    @staticmethod
    def apply_fade_out(clip, duration: float = None):
        """
        Apply fade-out effect to a clip.

        Args:
            clip: Video clip to apply effect to
            duration: Fade duration in seconds

        Returns:
            Clip with fade-out effect
        """
        duration = duration or DEFAULT_CONFIG["fade_duration"]
        return clip.with_effects([FadeOut(duration)])

    @staticmethod
    def apply_fade_in_out(
        clip,
        fade_in_duration: float = None,
        fade_out_duration: float = None,
    ):
        """
        Apply both fade-in and fade-out effects.

        Args:
            clip: Video clip to apply effects to
            fade_in_duration: Fade-in duration
            fade_out_duration: Fade-out duration

        Returns:
            Clip with both fade effects
        """
        fade_in_duration = fade_in_duration or DEFAULT_CONFIG["fade_duration"]
        fade_out_duration = fade_out_duration or DEFAULT_CONFIG["fade_duration"]

        return clip.with_effects([
            FadeIn(fade_in_duration),
            FadeOut(fade_out_duration)
        ])

    @staticmethod
    def crossfade_clips(
        clip1,
        clip2,
        duration: float = None,
    ):
        """
        Create a crossfade transition between two clips.

        Args:
            clip1: First clip
            clip2: Second clip
            duration: Crossfade duration in seconds

        Returns:
            Concatenated clip with crossfade
        """
        duration = duration or DEFAULT_CONFIG["transition_duration"]

        # Apply fadeout to first clip
        clip1 = clip1.with_effects([FadeOut(duration)])

        # Apply fadein to second clip and offset start time
        clip2 = clip2.with_effects([FadeIn(duration)])
        clip2 = clip2.with_start(clip1.duration - duration)

        # Composite the clips
        return CompositeVideoClip([clip1, clip2])

    @staticmethod
    def concatenate_with_transition(
        clips: list,
        transition_duration: float = None,
    ):
        """
        Concatenate multiple clips with crossfade transitions.

        Args:
            clips: List of video clips
            transition_duration: Duration of each transition

        Returns:
            Single concatenated clip with transitions
        """
        transition_duration = transition_duration or DEFAULT_CONFIG["transition_duration"]

        if len(clips) == 0:
            raise ValueError("No clips provided")
        if len(clips) == 1:
            return clips[0]

        # Use moviepy's built-in crossfade
        return concatenate_videoclips(
            clips,
            method="compose",
            padding=-transition_duration,
        )

    @staticmethod
    def resize_clip(clip, target_resolution: tuple = None):
        """
        Resize a clip to target resolution.

        Args:
            clip: Video clip to resize
            target_resolution: Target (width, height)

        Returns:
            Resized clip
        """
        target_resolution = target_resolution or DEFAULT_CONFIG["resolution"]
        return clip.resized(target_resolution)

    @staticmethod
    def set_clip_duration(clip, duration: float):
        """
        Set the duration of a clip (loop or cut).

        Args:
            clip: Video clip
            duration: Target duration in seconds

        Returns:
            Clip with adjusted duration
        """
        if clip.duration >= duration:
            return clip.subclipped(0, duration)
        else:
            # Loop the clip to reach target duration
            return clip.with_duration(duration).looped()


if __name__ == "__main__":
    from moviepy import ColorClip

    # Test effects
    effects = Effects()

    # Create test clips
    clip1 = ColorClip(size=(1920, 1080), color=(255, 0, 0)).with_duration(3)
    clip2 = ColorClip(size=(1920, 1080), color=(0, 255, 0)).with_duration(3)

    # Test fade
    faded = effects.apply_fade_in_out(clip1)
    print(f"Faded clip duration: {faded.duration}s")

    # Test crossfade
    crossfaded = effects.crossfade_clips(clip1, clip2, duration=0.5)
    print(f"Crossfaded clip duration: {crossfaded.duration}s")
