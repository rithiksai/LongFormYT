import os
from openai import OpenAI

def callAPI(arg) :
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    completion = client.chat.completions.create(
        messages=[
            {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "you are a anime enthusiast and a very good story narrator who can spin up awesome stories"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Generate a youtube video srcipt using the Title as given below : " + arg + " .Let the video be of 4-5 minutes of length. add your own twist and humur to keep the audience entertained and also suggest a similar title for the youtube video"
            }
        ]
        }
        ],
        model="gpt-3.5-turbo",
    )
    return completion.choices[0].message.content
    

#print(completion.choices[0].message)