from dotenv import load_dotenv
load_dotenv()  # Must run BEFORE importing test.py

import streamlit as st
import test
import script
import pandas as pd

c_name = st.text_input("Enter channel names seperated with commas :")

list = c_name.split(",")

df = pd.DataFrame()
str = ""
for name in list:
    if len(name) > 0:
        df = test.start(name)
        st.dataframe(df)

        i = 0 
        for t in df["Title"]:
            i += 1
            if i == 1:
                str += t

    #     script = script.callAPI(str)

    # st.write(script)
