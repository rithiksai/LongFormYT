import test
import pandas as pd

name = input("Enter Channel Name : ")

df = test.start(name)
df.to_csv("out.csv", encoding='utf-8', index=False)