from dotenv import load_dotenv
import os
from irc.bot import SingleServerIRCBot, ExponentialBackoff
from irc.client import ServerConnection, Event
import logging
from pathlib import Path
from lang_utils import Translator

class IrcBot(SingleServerIRCBot):
    def __init__(self, server="irc.ppy.sh", port=6667):
        self.translator = Translator(os.getenv("LANGUAGE", "en"))
        
        #Flags
        self.running = True
        
        
        # loading .env
        env_path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_path, override=True)
        
        # connecting to IRC server
        logging.info(f"Initializing IrcBot with nickname: {os.getenv("IRC_NICK")}, server: {server}, port: {port}")
        recon = ExponentialBackoff(min_interval=5, max_interval=30)
        SingleServerIRCBot.__init__(self, [(server, port, os.getenv("IRC_PASSWORD"))], os.getenv("IRC_NICK"), os.getenv("IRC_NICK"), recon=recon)
        self.connection.set_rate_limit(1)

       

    def on_welcome(self, c: ServerConnection, e: Event):
        logging.info(f"Connected to osu!IRC server as {self._nickname}")

    def send_message(self, target: str, text: str):
        if not self.connection.is_connected():
            logging.error("Cannot send message: Not connected to IRC server!")
            try:
                self.connect("irc.ppy.sh", 6667, os.getenv("IRC_NICK"), os.getenv("IRC_PASSWORD"))
                logging.info("Reconnect succesful.")
            except Exception as e:
                logging.error(f"Recconection failed: {e}")
                return
        
        try:
            target = target.replace(" ", "_")
            self.connection.privmsg(target, text)
            logging.info(f"In-Game message was successfully sent to {target}")
        except Exception as e:
            logging.error(f"Error sending message to {target}: {e}")
            