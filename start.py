import logging
from dotenv import load_dotenv
from Main_GUI import MainGui
from Setup_GUI import SetupGui
import os

logging.basicConfig(
    
   level=logging.INFO,
   format="%(asctime)s - %(levelname)s - %(message)s",
   datefmt="%Y-%m-%d | %H:%M:%S",

)

logger = logging.getLogger(__name__)

load_dotenv()

first_time = os.getenv("FIRST_TIME_RUN")

if  first_time == "true":
    logger.info("First time run, opening Setup GUI")
    fgui = SetupGui()
    fgui.mainloop()
else:
    logger.info("opening Main GUI")
    gui = MainGui()
    gui.mainloop()