"""Research YouTube channel for Shorts."""

import os
from datetime import datetime, timezone
import re
import googleapiclient.discovery
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
api_key = os.environ.get("YOUTUBE_API_KEY")

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=api_key
)


def convert_to_seconds(time_str):
    """Convert YouTube duration format (PT1M30S) to seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', time_str)
    if match:
        hrs = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hrs * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return 0


def get_video_details(video_id, df):
    """Get video details and add to DataFrame if it's a Short."""
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    if not response.get("items"):
        return df

    item = response["items"][0]
    title = item["snippet"]["localized"]["title"]
    views = int(item["statistics"].get("viewCount", 0))
    time = item["contentDetails"]["duration"]
    published_at = item["snippet"]["publishedAt"]

    # Filter FOR shorts (duration <= 60 seconds)
    sec = convert_to_seconds(time)

    if sec <= 60 and sec > 0:  # Only include shorts
        # Calculate days since upload
        publish_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days_old = (now - publish_date).days
        if days_old < 1:
            days_old = 1

        # Calculate virality score: views / (days ^ 0.8)
        virality_score = round(views / (days_old ** 0.8), 2)

        # Construct video link
        video_link = f"https://youtube.com/shorts/{video_id}"

        df = pd.concat([df, pd.DataFrame({
            "Title": [title],
            "View Count": [views],
            "Duration": [sec],
            "Days Old": [days_old],
            "Virality Score": [virality_score],
            "Video Link": [video_link]
        })], ignore_index=True)

    return df


def get_channel_id(channel_name):
    """Get channel ID from channel name."""
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=channel_name,
        type="channel"
    )
    response = request.execute()

    if not response.get("items"):
        raise ValueError(f"Channel '{channel_name}' not found")

    return response["items"][0]["id"]["channelId"]


def get_playlist_id(channel_id):
    """Get uploads playlist ID from channel ID."""
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id,
    )
    response = request.execute()

    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_videos_from_playlist(playlist_id, df, max_results=50):
    """Get videos from playlist and filter for shorts."""
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=max_results,
        playlistId=playlist_id
    )
    response = request.execute()

    videos_list = response.get("items", [])

    for v in videos_list:
        df = get_video_details(v["contentDetails"]["videoId"], df)

    return df


def research_channel(channel_name):
    """
    Research a YouTube channel for Shorts.

    Args:
        channel_name: Name of the YouTube channel

    Returns:
        DataFrame with shorts sorted by virality score
    """
    print(f"  Researching channel: {channel_name}")

    df = pd.DataFrame(columns=["Title", "View Count", "Duration", "Days Old", "Virality Score", "Video Link"])

    channel_id = get_channel_id(channel_name)
    print(f"  Found channel ID: {channel_id}")

    playlist_id = get_playlist_id(channel_id)
    df = get_videos_from_playlist(playlist_id, df)

    if df.empty:
        print("  No shorts found for this channel")
        return df

    # Normalize virality score to 0-100 scale
    max_score = df["Virality Score"].max()
    if max_score > 0:
        df["Virality Score"] = round((df["Virality Score"] / max_score) * 100, 2)

    # Sort by virality score
    df = df.sort_values(by='Virality Score', ascending=False)

    print(f"  Found {len(df)} shorts")

    return df


def display_shorts(df, max_display=10):
    """Display shorts in a formatted table."""
    print("\n" + "=" * 70)
    print("  TOP SHORTS")
    print("=" * 70)

    df_display = df.head(max_display)

    print(f"\n{'#':<3} {'Title':<40} {'Views':<12} {'Virality':<10}")
    print("-" * 70)

    for i, (_, row) in enumerate(df_display.iterrows(), 1):
        title = row['Title'][:37] + "..." if len(row['Title']) > 40 else row['Title']
        views = f"{row['View Count']:,}"
        virality = f"{row['Virality Score']:.0f}"
        print(f"{i:<3} {title:<40} {views:<12} {virality:<10}")

    print("-" * 70)
    return df_display


def select_short(df_display):
    """Let user select a short from the list."""
    while True:
        try:
            choice = input(f"\nSelect a short (1-{len(df_display)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(df_display):
                selected = df_display.iloc[idx]
                print(f"\n  Selected: {selected['Title']}")
                return selected['Title']
            else:
                print(f"Invalid selection. Please enter 1-{len(df_display)}.")
        except ValueError:
            print("Please enter a number.")


if __name__ == "__main__":
    # Test
    channel = input("Enter channel name: ")
    df = research_channel(channel)
    if not df.empty:
        df_display = display_shorts(df)
        title = select_short(df_display)
        if title:
            print(f"\nSelected title: {title}")
