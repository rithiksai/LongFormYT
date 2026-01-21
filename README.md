# YouTube Video Generator

Automated pipeline that generates YouTube videos from viral content research. Supports both **Long-Form** and **Shorts** video generation.

## Pipelines

### Long-Form Videos
```
Channel Research → Video Selection → Transcript → Script → Voiceover → Video
```

### YouTube Shorts
```
Title → Script (Outcome-First Hook) → Voiceover → AI Images/Video → Short
```

## Features

- **Viral content research** - Find trending videos from YouTube channels
- **AI script generation** - Claude generates engaging scripts with outcome-first hooks
- **Text-to-speech** - ElevenLabs voice generation
- **AI image generation** - Stability AI creates anime-style visuals (Shorts)
- **Video assembly** - Automatic composition with Ken Burns effects

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 3. Configure API keys

Copy `.env.example` to `.env` and add your keys:

```env
YOUTUBE_API_KEY=your_youtube_data_api_key
CLAUDE_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
ELEVEN_LABS_API=your_elevenlabs_api_key
STABILITY_API_KEY=your_stability_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Add background videos (Long-Form)

Place MP4 video files in `assets/videos/` folder. These are used as background clips in long-form videos.

## Usage

### Long-Form Pipeline

```bash
python run_pipeline.py
```

Options:
- `--channel "Channel Name"` - Skip channel input prompt
- `--auto-select 1` - Auto-select video by rank (1-10)
- `--output-dir path/` - Custom output directory

### Shorts Pipeline

```bash
cd ShortsYT
python run_pipeline.py --title "Your Short Title" --mode images
```

Options:
- `--title "Title"` - The topic for the short
- `--mode video|images` - Use background clips or AI-generated images

### Test Video Generation

```bash
python test_video.py
```

## Project Structure

```
LongFormYT/
├── run_pipeline.py      # Long-form pipeline
├── test_video.py        # Test video generation
├── test.py              # YouTube channel research
├── video_content/       # Transcript fetching
│   └── getContent.py
├── genScript/           # Long-form script generation
│   └── genScript.py
├── voiceOver/           # ElevenLabs TTS
│   └── genVoice.py
├── video_assembler/     # Video composition
│   ├── video_assembler.py
│   ├── asset_manager.py
│   └── config.py
├── ShortsYT/            # YouTube Shorts pipeline
│   ├── run_pipeline.py      # Shorts pipeline orchestration
│   ├── gen_script.py        # Shorts script generation (outcome-first hooks)
│   ├── gen_voice.py         # Voice generation
│   ├── gen_images.py        # Stability AI image generation
│   ├── video_assembler.py   # Shorts video composition
│   └── research_shorts.py   # Find viral shorts
├── assets/videos/       # Background video clips
└── output/              # Generated files
```

## API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| YouTube Data API | Research viral videos | [Google Cloud Console](https://console.cloud.google.com/) |
| Claude (Anthropic) | AI script generation | [Anthropic Console](https://console.anthropic.com/) |
| ElevenLabs | Text-to-speech | [ElevenLabs](https://elevenlabs.io/) |
| Stability AI | AI image generation (Shorts) | [Stability AI](https://platform.stability.ai/) |
| Gemini | Alternative AI | [Google AI Studio](https://aistudio.google.com/) |

## Output Specs

### Long-Form
- **Resolution**: 1920x1080 (16:9)
- **FPS**: 30
- **Codec**: H.264

### Shorts
- **Resolution**: 1080x1920 (9:16 vertical)
- **Duration**: ~30 seconds
- **Effects**: Ken Burns (pan/zoom)

## Shorts Hook Strategy

The script generator uses an **outcome-first** approach for maximum viewer retention:

**Wrong** (context first):
- "I started a faceless YouTube channel and..."

**Right** (outcome first):
- "This faceless Short made $47 while I was asleep."

The first 1.5 seconds are critical for engagement.

---

Created with care by [Rithik Sai Motupalli](https://github.com/rithiksai)
