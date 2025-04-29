from dotenv import load_dotenv
import os
from irc.bot import SingleServerIRCBot, ExponentialBackoff
from irc.client import ServerConnection, Event
import logging
from pathlib import Path
import asyncio

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

IRC_IP = os.getenv("IRC_IP")
IRC_PORT = int(os.getenv("IRC_PORT"))
IRC_NICK = os.getenv("IRC_NICK")
IRC_PASS = os.getenv("IRC_PASSWORD")
IRC_CHANNEL = IRC_NICK

class IrcBot(SingleServerIRCBot):
    def __init__(self, nickname=IRC_NICK, server=IRC_IP, port=IRC_PORT, password=IRC_PASS):
        logging.info(f"Initializing IrcBot with nickname: {nickname}, server: {server}, port: {port}")
        recon = ExponentialBackoff(min_interval=5, max_interval=30)
        SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname, recon=recon)
        self.connection.set_rate_limit(1)
        self.connected = False
        self.messages_queue = asyncio.Queue()

    def on_welcome(self, c: ServerConnection, e: Event):
        self.connected = True
        logging.info(f"Connected to osu!IRC server as {self._nickname}")

    def send_message(self, target: str, text: str):
        if not self.connection.is_connected():
            logging.error("Cannot send message: Not connected to IRC server!")
            return
        try:
            target = target.replace(" ", "_")
            self.connection.privmsg(target, text)
            logging.info(f"In-Game message was successfully sent to {target}")
        except Exception as e:
            logging.error(f"Error sending message to {target}: {e}")
            
            
