from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    # api_key="AIzaSyDX_r4s0D2n7ZZVGGXTtV2dI24yQsTcROU",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {   "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain to me how AI works"
        }
    ]
)

# print(response.choices[0].message)
print(response.choices[0].message.content)