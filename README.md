# YouTube Viral Video Research Tool

A research tool to analyze viral videos from YouTube channels and find inspiration for your next video content.

## Purpose

This tool helps content creators research what's working on YouTube by:
- Analyzing recent videos from any YouTube channel
- Identifying top-performing videos by view count
- Filtering out Shorts (only shows long-form content >90 seconds)
- Generating script ideas based on viral video titles

## Features

- **Channel Analysis**: Enter any YouTube channel name to fetch their recent videos
- **View Count Sorting**: Videos are automatically sorted by view count (highest first)
- **Shorts Filter**: Automatically excludes YouTube Shorts to focus on long-form content
- **Script Generation**: Uses AI to generate video script ideas inspired by top-performing titles

## Setup

1. **Clone the repository**

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run frontend.py
```

Then in the web interface:
1. Enter YouTube channel name(s) separated by commas
2. View the video data sorted by view count
3. Get AI-generated script ideas based on top videos

## Project Structure

```
├── frontend.py    # Streamlit web interface
├── test.py        # YouTube Data API integration
├── script.py      # OpenAI script generation
├── main.py        # Main module
└── requirements.txt
```

## Requirements

- Python 3.x
- YouTube Data API v3 key
- OpenAI API key
