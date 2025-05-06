import logging
from dotenv import load_dotenv
from Main_GUI import MainGui
from Setup_GUI import SetupGui
import os
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(
    
   level=logging.INFO,
   format="%(asctime)s - %(levelname)s - %(message)s",
   datefmt="%Y-%m-%d | %H:%M:%S",
)

logger = logging.getLogger(__name__)

first_time = os.getenv("FIRST_TIME_RUN")

if  first_time == "true":
    logger.info("First time run, opening Setup GUI")
    fgui = SetupGui()
    fgui.mainloop()
    load_dotenv(env_path, override=True)  # Reload the .env file after Setup_GUI
else:
    logger.info("opening Main GUI")
    gui = MainGui()
    gui.mainloop()