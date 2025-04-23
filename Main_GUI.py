import customtkinter
import tkinter
import sys
import threading
import logging
from Main import start_bot
from Setup_GUI import SetupGui
import asyncio
from dotenv import load_dotenv
load_dotenv()

class ConsoleOutput:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        if message.strip():
            self.widget.configure(state="normal")
            self.widget.insert(tkinter.END, message)
            self.widget.see(tkinter.END)
            self.widget.configure(state="disabled")

    def flush(self):
        pass


class MainGui(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("osu! - Twitch Integration bot")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.console_frame = customtkinter.CTkFrame(self)
        self.console_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
       
        self.settings_frame = customtkinter.CTkFrame(self)
        self.settings_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nse")
        
        # console_frame
        self.console_output = customtkinter.CTkTextbox(self.console_frame, width=360, height=450, wrap=tkinter.WORD, scrollbar_button_color="", scrollbar_button_hover_color="", state="disabled")
        self.console_output.grid(row=0, column=0, padx=20, pady=20)
        
        # redirecting stdout and stderr to the console_output
        sys.stdout = ConsoleOutput(self.console_output)
        sys.stderr = ConsoleOutput(self.console_output)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
            
        # settings buttons - (settings_frame)
        self.start_button = customtkinter.CTkButton(self.settings_frame, text="Start Bot", command=self.start, fg_color="green")
        self.start_button.grid(row=0, column=0, padx=20, pady=(10, 5))
        
        self.setup_button = customtkinter.CTkButton(self.settings_frame, text="API's Config", command=self.api_setup)
        self.setup_button.grid(row=1, column=0, padx=20, pady=5)
        
        self.settings_button = customtkinter.CTkButton(self.settings_frame, text="Settings (będzie dodane)", command=self.test,state="disabled")
        self.settings_button.grid(row=2, column=0, padx=20, pady=5)
        
        self.stop_button = customtkinter.CTkButton(self.settings_frame, text="Stop Bot", command=self.stop, state="disabled", fg_color="darkred")
        self.stop_button.grid(row=3, column=0, padx=20, pady=(300, 5))
        
        self.quit_button = customtkinter.CTkButton(self.settings_frame, text="Quit", command=self.quit, fg_color="darkred")
        self.quit_button.grid(row=4, column=0, padx=20, pady=5)
        
        self.close_program = None
        self.started = False
        

    
    def test(self):
        logging.info("Test button clicked")
        
    def api_setup(self):
        logging.info("API setup button clicked")
        try:
            self.setup_window = SetupGui()
            self.setup_window.mainloop()
        except Exception as e:
            logging.error(f"Error starting API setup: {e}")
        
    def start(self):
        
        logging.info("Starting the bot...")
        
        self.start_button.configure(state="disabled", fg_color="darkorange")
        self.setup_button.configure(state="disabled")
        threading.Thread(target=self.running_background_bot, daemon=True).start()
        self.stop_button.configure(state="normal")
        self.started = True
        
    def running_background_bot(self):
        try:
            self.close_program = start_bot()
        except Exception as e:
            logging.error(f"Error starting bot: {e}")
                
    
    def stop(self):
        if self.close_program:
            logging.info("Stopping the bot...")
            
            asyncio.run(self.close_program())
            
            self.start_button.configure(state="normal", fg_color="green")
            self.setup_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
            self.started = False
            
            logging.info("The bot stopped.")
        
    def quit(self):
        if self.started: 
            self.stop()
            
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        self.after_cancel("all")
        self.destroy()
        