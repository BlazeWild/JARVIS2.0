import os
from dotenv import load_dotenv

# 1. Ensure this is at the very top
load_dotenv() 

# 2. Retrieve variables manually
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# print all api keys
print("LIVEKIT_URL:", LIVEKIT_URL)
print("LIVEKIT_API_KEY:", LIVEKIT_API_KEY)
print("LIVEKIT_API_SECRET:", LIVEKIT_API_SECRET)