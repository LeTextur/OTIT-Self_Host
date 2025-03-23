from osu import Client
import os
from dotenv import load_dotenv
load_dotenv()
# 4983056 = ignore
client_id = int(os.getenv('OSU_CLIENT_ID'))
client_secret = os.getenv('OSU_CLIENT_SECRET')
redirect_url = os.getenv("REDIRECT_URL")
user_id = os.getenv("OSU_USER_ID")

client = Client.from_credentials(client_id, client_secret, redirect_url)
beatmap = client.get_beatmap(4907421).beatmapset.artist

print(beatmap)