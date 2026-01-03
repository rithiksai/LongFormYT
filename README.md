# AI YouTube Video Generator

An end-to-end automated video generation system that researches viral YouTube content, generates scripts, creates voiceovers, and assembles complete videos with anime clips and motion graphics.

## Overview

This tool automates the entire YouTube video creation pipeline:
1. **Research** - Find viral videos from YouTube channels
2. **Analyze** - Calculate virality scores to identify trending content
3. **Script** - Generate engaging scripts using AI
4. **Voiceover** - Create professional narration with text-to-speech
5. **Assemble** - Combine clips, graphics, and audio into final video

## Features

- **Viral Video Research**: Analyze YouTube channels to find top-performing videos
- **Virality Algorithm**: Score videos based on views/days with weighted decay
- **Transcript Extraction**: Pull transcripts from YouTube videos for analysis
- **AI Script Generation**: Generate scripts using Gemini AI with structured output
- **Text-to-Speech**: Create voiceovers with ElevenLabs
- **Video Assembly**: Automatically download clips, add motion graphics, and render final video

## Project Structure

```
LongFormYT/
├── frontend.py              # Streamlit web interface
├── test.py                  # YouTube Data API - viral video research
├── test_pipeline.py         # Test script for full pipeline
├── genScript/
│   └── genScript.py         # AI script generation (Gemini)
├── voiceOver/
│   └── genVoice.py          # ElevenLabs text-to-speech
├── video_content/
│   └── getContent.py        # YouTube transcript extraction
├── video_assembler/
│   ├── __init__.py
│   ├── asset_manager.py     # YouTube clip downloader (yt-dlp)
│   ├── motion_graphics.py   # Text overlays, title cards
│   ├── scene_composer.py    # Scene composition
│   ├── effects.py           # Video effects and transitions
│   ├── video_assembler.py   # Main video generation orchestrator
│   ├── models.py            # Pydantic data models
│   └── config.py            # Configuration settings
└── output/                  # Generated videos
```

## Setup

### 1. Clone and create virtual environment
```bash
git clone <repo-url>
cd LongFormYT
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install system dependencies
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 4. Set up environment variables

Create a `.env` file:
```env
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
ELEVEN_LABS_API=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key  # For tracing (free)
```

## Usage

### Research Viral Videos (Streamlit UI)
```bash
streamlit run frontend.py
```

### Generate a Complete Video
```python
from genScript.genScript import generate_script
from voiceOver.genVoice import generate_full_voiceover
from video_assembler import VideoAssembler

# 1. Generate script
script = generate_script(
    title="Top 10 Anime Moments",
    transcript="Your reference content here..."
)

# 2. Generate voiceover
voiceover_path = generate_full_voiceover(script, "output/voiceover.mp3")

# 3. Assemble video
assembler = VideoAssembler()
video_path = assembler.generate_video(
    script_data=script,
    voiceover_path=voiceover_path,
    output_path="output/final_video.mp4"
)
```

### Test the Pipeline
```bash
# Test motion graphics (no API needed)
python test_pipeline.py --graphics

# Test clip downloading
python test_pipeline.py --download

# Test full video assembly (needs voiceover file)
python test_pipeline.py

# Test complete pipeline (needs all API keys)
python test_pipeline.py --full
```

## API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| YouTube Data API v3 | Research viral videos | [Google Cloud Console](https://console.cloud.google.com/) |
| Gemini | AI script generation | [Google AI Studio](https://makersuite.google.com/) |
| ElevenLabs | Text-to-speech voiceover | [ElevenLabs](https://elevenlabs.io/) |
| OpenAI | Tracing (free) | [OpenAI Platform](https://platform.openai.com/) |

## Output Format

The video assembler generates:
- **Resolution**: 1920x1080 (1080p)
- **FPS**: 30
- **Codec**: H.264 (libx264)
- **Audio**: AAC

## Script Output Format

```json
{
  "script": "Full narration text...",
  "duration_estimate": 300,
  "scenes": [
    {
      "timestamp": "0:00",
      "narration": "Scene narration...",
      "visual_suggestion": "Anime action scene"
    }
  ]
}
```
