# -*- coding: utf-8 -*-
# Sample Python code for youtube.channels.list using API key

import googleapiclient.discovery
import pandas as pd
import matplotlib.pyplot as plt
import re

# Create an API client
    
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyAAinpoN5vrAqmofIhyF2q9NzunAZANoE4"

youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)




def convert_to_seconds(time_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', time_str)
    if match:
        hrs = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)  # If minutes are not present, default to 0
        seconds = int(match.group(3))
        total_seconds = hrs * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        raise ValueError("Invalid time format")


def getVideoViewCount(video_id,df):

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    title = response["items"][0]["snippet"]["localized"]["title"]
    views = response["items"][0]["statistics"]["viewCount"]
    time = response["items"][0]["contentDetails"]["duration"]

    #filter out shorts from the voideoList 
    sec = convert_to_seconds(time)

    if(sec > 90):
        df = pd.concat([df, pd.DataFrame({"Title": [title], "View Count": [int(views)]})], ignore_index=True)
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

    df = pd.DataFrame(columns=["Title","View Count"])

    channelid = getChannelId(name)
    playlistid = getPlaylistId(channelid)
    df = getVideoId(playlistid,df)

    df = df.sort_values(by='View Count',ascending=False,inplace=False)
    #print(df)
    return df



