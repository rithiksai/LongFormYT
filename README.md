# YouTube Video Generator

Automated pipeline that generates YouTube videos from viral content research.

## Pipeline

```
Channel Research → Video Selection → Transcript → Script → Voiceover → Video
```

1. **Research** - Find viral videos from a YouTube channel
2. **Select** - Pick a video based on virality score
3. **Transcript** - Fetch the video's transcript
4. **Script** - AI generates a new script from the content
5. **Voiceover** - Text-to-speech generates narration
6. **Video** - Combines background clips with voiceover

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
GEMINI_API_KEY=your_gemini_api_key
ELEVEN_LABS_API=your_elevenlabs_api_key
```

### 4. Add background videos

Place MP4 video files in `assets/videos/` folder. These are used as background clips in the generated video.

## Usage

### Full Pipeline

```bash
python run_pipeline.py
```

Options:
- `--channel "Channel Name"` - Skip channel input prompt
- `--auto-select 1` - Auto-select video by rank (1-10)
- `--output-dir path/` - Custom output directory

### Test Video Generation

To test video assembly without using API credits:

```bash
python test_video.py
```

Edit paths in `test_video.py` to use your existing script/voiceover files.

## Project Structure

```
LongFormYT/
├── run_pipeline.py      # Main pipeline script
├── test_video.py        # Test video generation
├── test.py              # YouTube channel research
├── video_content/       # Transcript fetching
│   └── getContent.py
├── genScript/           # AI script generation
│   └── genScript.py
├── voiceOver/           # ElevenLabs TTS
│   └── genVoice.py
├── video_assembler/     # Video composition
│   ├── video_assembler.py
│   ├── asset_manager.py
│   └── config.py
├── assets/videos/       # Background video clips (add your own)
└── output/              # Generated files
    ├── scripts/
    ├── voiceovers/
    └── videos/
```

## API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| YouTube Data API | Research viral videos | [Google Cloud Console](https://console.cloud.google.com/) |
| Gemini | AI script generation | [Google AI Studio](https://aistudio.google.com/) |
| ElevenLabs | Text-to-speech | [ElevenLabs](https://elevenlabs.io/) |

## Output

- **Resolution**: 1920x1080 (1080p)
- **FPS**: 30
- **Codec**: H.264
- **Audio**: AAC

Created with ❤️ by [Rithik Sai Motupalli](https://github.com/rithiksai)