from dotenv import load_dotenv
import os
from irc.bot import SingleServerIRCBot, ExponentialBackoff
from irc.client import ServerConnection, Event
import logging
load_dotenv()

IRC_IP = os.getenv("IRC_IP")
IRC_PORT = int(os.getenv("IRC_PORT"))
IRC_NICK = os.getenv("IRC_NICK")
IRC_PASS = os.getenv("IRC_PASSWORD")
IRC_CHANNEL = IRC_NICK

class IrcBot(SingleServerIRCBot):
    def __init__(self, nickname=IRC_NICK, server=IRC_IP, port=IRC_PORT, password=IRC_PASS):
        recon = ExponentialBackoff(min_interval=5, max_interval=30)
        SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname, recon=recon)
        self.connection.set_rate_limit(1)

    def on_welcome(self, c: ServerConnection, e: Event):
        logging.info(f"Connected to osu!IRC server as {self._nickname}")

    def send_message(self, target: str, text: str):
        target = target.replace(" ", "_")
        self.connection.privmsg(target, text)
        logging.info(f"In-Game message was successfully sent to {target}")
