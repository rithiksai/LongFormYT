# -*- coding: utf-8 -*-
# Sample Python code for youtube.channels.list using API key

import os
from datetime import datetime, timezone
import googleapiclient.discovery
import pandas as pd
import matplotlib.pyplot as plt
import re

from dotenv import load_dotenv

load_dotenv()
# Create an API client

api_service_name = "youtube"
api_version = "v3"
api_key = os.environ.get("YOUTUBE_API_KEY")

youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)




def convert_to_seconds(time_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', time_str)
    if match:
        hrs = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)  # If minutes are not present, default to 0
        seconds = int(match.group(3) or 0)
        total_seconds = hrs * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        raise ValueError("Invalid time format")


def getVideoViewCount(video_id, df):

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    title = response["items"][0]["snippet"]["localized"]["title"]
    views = int(response["items"][0]["statistics"]["viewCount"])
    time = response["items"][0]["contentDetails"]["duration"]
    published_at = response["items"][0]["snippet"]["publishedAt"]

    # Filter out shorts from the videoList
    sec = convert_to_seconds(time)

    if sec > 90:
        # Calculate days since upload
        publish_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days_old = (now - publish_date).days
        if days_old < 1:
            days_old = 1  # Avoid division issues for videos uploaded today

        # Calculate virality score: views / (days ^ 0.8)
        virality_score = round(views / (days_old ** 0.8), 2)

        # Construct video link
        video_link = f"https://youtube.com/watch?v={video_id}"

        df = pd.concat([df, pd.DataFrame({
            "Title": [title],
            "View Count": [views],
            "Days Old": [days_old],
            "Virality Score": [virality_score],
            "Video Link": [video_link]
        })], ignore_index=True)
    return df
    


def getChannelId(channel_name):
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=channel_name,
        type="channel"
    )
    response = request.execute()

    channel_id = response["items"][0]["id"]["channelId"]

    return channel_id

def getPlaylistId(channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id,
    )
    response = request.execute()
    playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    return playlist_id

def getVideoId(playlist_id,df):
    request_vidid = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=15,
        playlistId=playlist_id
    )
    
    #upload playlist id = UUNUgCUzP__FwGOiLbXU94hQ

    response = request_vidid.execute()

    videos_list = response["items"]

    
    
    for v in videos_list:
        df = getVideoViewCount(v["contentDetails"]["videoId"],df)
    return df

def main():
    return 0
    
if __name__ == "__main__":
    main()
def start(name):

    df = pd.DataFrame(columns=["Title", "View Count", "Days Old", "Virality Score", "Video Link"])

    channelid = getChannelId(name)
    playlistid = getPlaylistId(channelid)
    df = getVideoId(playlistid, df)

    # Normalize virality score to 0-100 scale
    max_score = df["Virality Score"].max()
    if max_score > 0:
        df["Virality Score"] = round((df["Virality Score"] / max_score) * 100, 2)

    df = df.sort_values(by='Virality Score', ascending=False, inplace=False)
    return df



