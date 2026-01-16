import youtube_research
import pandas as pd

name = input("Enter Channel Name : ")

df = youtube_research.start(name)
df.to_csv("out.csv", encoding='utf-8', index=False)