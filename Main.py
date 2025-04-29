from twitchAPI.chat import Chat, EventData, ChatMessage, ChatMessage, ChatSub, ChatCommand
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent
import os
import asyncio
from dotenv import load_dotenv
from IRC import IrcBot, IRC_CHANNEL
import re
from osu import Client
from threading import Thread
import logging
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
irc_bot = IrcBot()



# Function to convert seconds to readable time
def convert_seconds_to_readable(seconds: str) -> str:
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours == 0:
        return f'{minutes:g}:{seconds:02g}'
    else:
        return f'{hours:g}:{minutes:02g}:{seconds:02g}'



# Function to get beatmap properties
def get_beatmap_properties(id):
    
    # OSU API credentials
    client_id = os.getenv("OSU_CLIENT_ID")
    client_secret = os.getenv("OSU_CLIENT_SECRET")
    redirect_url = os.getenv("REDIRECT_URL")
    client = Client.from_credentials(client_id, client_secret, redirect_url)
    
    # Getting beatmap properties
    beatmap_SR =  round(client.get_beatmap_attributes(id).star_rating, 2)
    beatmap_artist = client.get_beatmap(id).beatmapset.artist
    beatmap_title = client.get_beatmap(id).beatmapset.title
    beatmap_diff = client.get_beatmap(id).version
    beatmap_bpm = client.get_beatmap(id).bpm
    beatmap_length = convert_seconds_to_readable(client.get_beatmap(id).total_length)
    beatmap_link = f"https://osu.ppy.sh/b/{id}"
    return beatmap_artist, beatmap_title, beatmap_diff, beatmap_SR, beatmap_link, beatmap_bpm , beatmap_length



# Twitch API credentials
TWITCH_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = os.getenv("TWITCH_TARGET_CHANNEL")


# Global variable to track the worker task
worker_task = None

# Function to handle requests
async def request_worker():
    while True:
        try:
            # Wait for a message from the queue
            target, beatmap_id, name = await irc_bot.messages_queue.get()
            
            # Process the beatmap
            beatmap_properties_list = get_beatmap_properties(beatmap_id)
            osu_msg = (
                f"{name}  »  "
                f"[{beatmap_properties_list[4]} {beatmap_properties_list[0]} - {beatmap_properties_list[1]} "
                f"[{beatmap_properties_list[2]}]]   ({beatmap_properties_list[5]} BPM, {beatmap_properties_list[3]}★, "
                f"{beatmap_properties_list[6]})"
            )
            
            # Send the message
            irc_bot.send_message(target, osu_msg)
        except Exception as e:
            logging.error(f"Error sending message: {e}")
        finally:
            # Mark the task as done in the queue
            irc_bot.messages_queue.task_done()


# Listening to the chat messages
async def on_massage(msg: ChatMessage):
    global worker_task  # Use the global variable to track the worker task

    logging.info(f"{msg.user.display_name} - {msg.text}")
    
    # Detecting osu beatmap link
    beatmap_link_pattern = re.compile(r'(https://)?osu.ppy.sh/(b/\d+|beatmapsets/\d+#osu/\d+)')
    match = beatmap_link_pattern.search(msg.text)
    
    if match:
        logging.info(f"Detected osu! beatmap link: {match[0]}")
        # Preparing to send the beatmap_id to the OSUAPI
        beatmap_id = str(match.group(2)).split("/")[-1]
        
        # Add beatmap_id to the queue
        irc_bot.messages_queue.put_nowait((IRC_CHANNEL, beatmap_id, msg.user.display_name))
        await msg.chat.send_message(TARGET_CHANNEL, f"[BOT] {msg.user.display_name} wysłał requesta")
        
        # Start request_worker as a background task if not already running
        if not worker_task or worker_task.done():
            worker_task = asyncio.create_task(request_worker())
    
    logging.info(f"Queue size after adding: {irc_bot.messages_queue.qsize()}")



# !np command
async def np_command(msg: ChatCommand):
    try:
        id_map = open("C://Program Files (x86)/StreamCompanion/Files/Map_ID.txt", "r")
        await msg.chat.send_message(TARGET_CHANNEL, id_map.read())
        id_map.close()
        logging.info("the !np command was used and the currently played beatmap link was displayed")
    except Exception as e:
        logging.error(f"An error occurred while trying to get the currently played map: {e}")
        await msg.chat.send_message(TARGET_CHANNEL, "[BOT] Nie udało się pobrać aktualnie granej mapy")
        
# !pp command
async def pp_command(msg: ChatCommand):
    try:
        id_map = open("C://Program Files (x86)/StreamCompanion/Files/Map_PP.txt", "r")
        await msg.chat.send_message(TARGET_CHANNEL, id_map.read())
        id_map.close()
        logging.info("the !pp command was used and the amount of pp for each acc value was displayed")
    except Exception as e:
        logging.error(f"An error occurred while trying to get the currently pp for a map: {e}")
        await msg.chat.send_message(TARGET_CHANNEL, "[BOT] Nie udało się pobrać PP za mapę")
    

    
# Bot connected successfully    
async def on_ready(ready_event: EventData):
    # Join the channel
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # Print ready message
    logging.info(f"Joined Twitch channel: {TARGET_CHANNEL}")
    
# Bot setup function
async def run_bot():
    
    load_dotenv(env_path, override=True)
    
    if [TWITCH_ID, TWITCH_SECRET, USER_SCOPE, TARGET_CHANNEL].count(None) > 0:
        raise ValueError("Twitch API credentials are blank. check API's config.")
    
    # Authenticate the bot
    bot = await Twitch(TWITCH_ID, TWITCH_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE) 
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)
  
    # Initialize chat class
    chat = await Chat(bot, no_message_reset_time = 2)
    
    # Listen to events
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_massage)
    
    # Register commands
    chat.register_command("np", np_command)
    chat.register_command("pp", pp_command)

    # Start Twitch bot
    chat.start()
    
    # Start IRC bot
    irc_bot_thread = Thread(target=irc_bot.start, name="IRC_BOT_THREAD")
    irc_bot_thread.start()
    
    
        # close the program
    async def close_program():
        await chat.send_message(TARGET_CHANNEL, "[BOT] Request bot został wyłączony")
        chat.stop()
        await bot.close()

        
        
    return close_program

def start_bot():
    return asyncio.run(run_bot())



# make config gui for the bot
    # - settings menu
    
    
# make the bot work with multiple channels
# bug fixing
# add more commands