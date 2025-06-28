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
        logging.info(self.translator.t("main-gui-irc-console-info1", server=server, port=port, nick=os.getenv('IRC_NICK')))
        recon = ExponentialBackoff(min_interval=5, max_interval=30)
        SingleServerIRCBot.__init__(self, [(server, port, os.getenv("IRC_PASSWORD"))], os.getenv("IRC_NICK"), os.getenv("IRC_NICK"), recon=recon)
        self.connection.set_rate_limit(1)

       

    def on_welcome(self, c: ServerConnection, e: Event):
        logging.info(self.translator.t("main-gui-irc-console-info2", nickname=self._nickname))

    def send_message(self, target: str, text: str):
        if not self.connection.is_connected():
            logging.error(self.translator.t("main-gui-irc-console-error1"))
            try:
                self.connect("irc.ppy.sh", 6667, os.getenv("IRC_NICK"), os.getenv("IRC_PASSWORD"))
                logging.info(self.translator.t("main-gui-irc-console-info4"))
            except Exception as e:
                logging.error(self.translator.t("main-gui-irc-console-error2"), error = e)
                return
        
        try:
            target = target.replace(" ", "_")
            self.connection.privmsg(target, text)
            logging.info(self.translator.t("main-gui-irc-console-info3"), target=target)
        except Exception as e:
            logging.error(self.translator.t("main-gui-irc-console-error3"),target=target, error = e)
            