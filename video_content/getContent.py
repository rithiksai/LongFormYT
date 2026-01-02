from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

def get_transcript(video_id):
    """Fetch transcript and return as a single string for LLM processing."""
    fetched_transcript = ytt_api.fetch(video_id)
    full_text = " ".join(snippet.text for snippet in fetched_transcript)
    return full_text

if __name__ == "__main__":
    video_id = "FJ6uvFNc7gI"
    transcript = get_transcript(video_id)
    print(transcript)