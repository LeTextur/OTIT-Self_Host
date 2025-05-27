import customtkinter
from tkinter import messagebox, END, WORD, Text, INSERT, filedialog
from dotenv import load_dotenv, set_key
from pathlib import Path
import logging
import os
import webbrowser

class SetupGui(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        logging.info("Starting GUI")
        
        env_path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_path, override=True)

        # Set the appearance mode and color theme
        customtkinter.set_appearance_mode("System") 
        customtkinter.set_default_color_theme("blue")  

        self.first_time = os.getenv("FIRST_TIME_RUN")
        self.saved_entries = {}
        self.tutorial_window = None  # Reference to the Tutorial window
        
        if self.first_time == "false":
            self.load_local_env()
        
        # window title and size
        self.title("osu! - Twitch Integration tool | API's config")
        self.geometry("400x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.resizable(False, False)
        
        # Create the main frame
        self.title_page = customtkinter.CTkLabel(self, text="Config Twitch API", font=("Nunito", 20))
        self.title_page.grid(row=0, column=0, padx=20, pady=20, columnspan=2)
        
        self.buttonN = customtkinter.CTkButton(self, text="Next")
        self.buttonN.grid(row=5, column=1, sticky="ew", padx=(5, 20), pady=20)
        
        self.buttonP = customtkinter.CTkButton(self, text="Previous")
        self.buttonP.grid(row=5, column=0, sticky="ew", padx=(20, 5), pady=20)
        
        self.progressbar = customtkinter.CTkProgressBar(self, width=250)
        self.progressbar.grid(row=6, column=0, columnspan=2)
        
        self.tutorial_button = customtkinter.CTkButton(self, text="Tutorial", command= lambda:  self.opening_tutorial())
        self.tutorial_button.grid(row=7, column=0, padx=5, pady=(40,0), sticky="ew")
        
        self.import_settings_button = customtkinter.CTkButton(self, text="Import settings", command=lambda: self.import_settings())
        self.import_settings_button.grid(row=7, column=1, columnspan=2, padx=5, pady=(40, 0), sticky="ew")
        
        self.first_page()
        
    def load_local_env(self):
        env_path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_path, override=True)
        logging.info("Loading saved entries from .env file")
        self.saved_entries["TWITCH_ID"] = os.getenv("TWITCH_CLIENT_ID", "")
        self.saved_entries["TWITCH_SECRET"] = os.getenv("TWITCH_CLIENT_SECRET", "")
        self.saved_entries["TWITCH_CHANNEL"] = os.getenv("TWITCH_TARGET_CHANNEL", "")
        self.saved_entries["OSU_ID"] = os.getenv("OSU_CLIENT_ID", "")
        self.saved_entries["OSU_SECRET"] = os.getenv("OSU_CLIENT_SECRET", "")
        self.saved_entries["IRC_NICK"] = os.getenv("IRC_NICK", "")
        self.saved_entries["IRC_PASSWORD"] = os.getenv("IRC_PASSWORD", "")
        
    def import_settings(self):
        executable_path = filedialog.askopenfilename(title="Select the .exe file from previous version of OTIT", filetypes=(("Executable", "*.exe"), ("All files", "*.*")))

        if executable_path:
            # Replace the .exe file name with "_internal/.env"
            base_dir = os.path.dirname(executable_path)
            new_path = os.path.join(base_dir, "_internal/.env")
            print(f"Loading .env file from: {new_path}")

            # Path to the local .env file
            local_env_path = Path(__file__).parent / ".env"

            # Import all variables from new_path to the local .env file
            with open(new_path, "r") as source_env:
                for line in source_env:
                    # Skip comments and empty lines
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        set_key(local_env_path, key, value, quote_mode="never")
            
            self.load_local_env()
            
            current_page = self.title_page.cget("text")
            if current_page == "Config Twitch API":
                
                if "TWITCH_CHANNEL" in self.saved_entries and self.saved_entries["TWITCH_CHANNEL"] != "": 
                    self.TWITCH_CHANNEL.insert(0, self.saved_entries.get("TWITCH_CHANNEL"))
                    
                if "TWITCH_ID" in self.saved_entries and self.saved_entries["TWITCH_ID"] != "": 
                    self.TWITCH_ID.insert(0, self.saved_entries.get("TWITCH_ID"))
                    
                if "TWITCH_SECRET" in self.saved_entries and self.saved_entries["TWITCH_SECRET"] != "": 
                    self.TWITCH_SECRET.insert(0, self.saved_entries.get("TWITCH_SECRET"))
                
            elif current_page == "Config osu! API":
                        
                if "OSU_ID" in self.saved_entries and self.saved_entries["OSU_ID"] != "": 
                    self.OSU_ID.insert(0, self.saved_entries.get("OSU_ID")) 
                    
                if "OSU_SECRET" in self.saved_entries and self.saved_entries["OSU_SECRET"] != "": 
                    self.OSU_SECRET.insert(0, self.saved_entries.get("OSU_SECRET"))
                
            elif current_page == "Config IRC connection":
                        
                if "IRC_NICK" in self.saved_entries and self.saved_entries["IRC_NICK"] != "": 
                    self.IRC_NICK.insert(0, self.saved_entries.get("IRC_NICK"))
            
                if "IRC_PASSWORD" in self.saved_entries and self.saved_entries["IRC_PASSWORD"] != "": 
                    self.IRC_PASSWORD.insert(0, self.saved_entries.get("IRC_PASSWORD"))
            
                
        
    def opening_tutorial(self):
        self.tutorial_button.configure(state="disabled")
        current_page = self.title_page.cget("text")
        self.tutorial_window = Tutorial(self, current_page)  # Store the Tutorial window reference
        self.tutorial_window.protocol("WM_DELETE_WINDOW", lambda: self.closing_tutorial())
        self.tutorial_window.mainloop()
            
    def closing_tutorial(self):
        if self.tutorial_window:
            self.tutorial_window.destroy()
            self.tutorial_window = None
        self.tutorial_button.configure(state="normal")
        
        
    def save_entries(self):
        # Save the entries to the dictionary
        current_page = self.title_page.cget("text")
        
        if current_page == "Config Twitch API":
            if hasattr(self, "TWITCH_ID") and hasattr(self, "TWITCH_SECRET") and hasattr(self, "TWITCH_CHANNEL"):
                self.saved_entries["TWITCH_ID"] = self.TWITCH_ID.get()  
                self.saved_entries["TWITCH_SECRET"] = self.TWITCH_SECRET.get()
                self.saved_entries["TWITCH_CHANNEL"] = self.TWITCH_CHANNEL.get()
        
        elif self.title_page.cget("text") == "Config osu! API":
            if hasattr(self, "OSU_ID") and hasattr(self, "OSU_SECRET"):
                self.saved_entries["OSU_ID"] = self.OSU_ID.get()
                self.saved_entries["OSU_SECRET"] = self.OSU_SECRET.get()
       
        elif self.title_page.cget("text") == "Config IRC connection":
            if hasattr(self, "IRC_NICK") and hasattr(self, "IRC_PASSWORD"):
                self.saved_entries["IRC_NICK"] = self.IRC_NICK.get()
                self.saved_entries["IRC_PASSWORD"] = self.IRC_PASSWORD.get()
    
    
    #Config Twitch API page
    def first_page(self):
        
        if hasattr(self, "OSU_ID"):
            self.OSU_ID.grid_forget()
        if hasattr(self, "OSU_SECRET"):
            self.OSU_SECRET.grid_forget()
        
        if self.first_time == "false": self.save_entries()

        logging.info("changed to first page gui")
        
        self.title_page.configure(text="Config Twitch API")
        
        self.TWITCH_CHANNEL = customtkinter.CTkEntry(self, placeholder_text="Twitch Channel", width=250)
        self.TWITCH_CHANNEL.grid(row=2, column=0, pady=(0,10), padx=(20, 5), sticky="ew")
        
        if "TWITCH_CHANNEL" in self.saved_entries and self.saved_entries["TWITCH_CHANNEL"] != "": self.TWITCH_CHANNEL.insert(0, self.saved_entries.get("TWITCH_CHANNEL"))
         
        self.TWITCH_ID = customtkinter.CTkEntry(self, placeholder_text="Twitch Client ID", width=250)
        self.TWITCH_ID.grid(row=2, column=1, pady=(0,10), padx=(5, 20), sticky="ew")
        
        if "TWITCH_ID" in self.saved_entries and self.saved_entries["TWITCH_ID"] != "": self.TWITCH_ID.insert(0, self.saved_entries.get("TWITCH_ID"))
        
        self.TWITCH_SECRET = customtkinter.CTkEntry(self, placeholder_text="Twitch Client SECRET", width=300, show="*")
        self.TWITCH_SECRET.grid(row=4, column=0, padx=20, pady=(10,10), columnspan=2)
        
        if "TWITCH_SECRET" in self.saved_entries and self.saved_entries["TWITCH_SECRET"] != "": self.TWITCH_SECRET.insert(0, self.saved_entries.get("TWITCH_SECRET"))
        
        self.buttonP.configure(state="disabled")
        self.buttonN.configure(command=lambda: self.second_page() , text="Next")
        
        self.progressbar.set(0.1)
        
        if self.tutorial_window:
            self.tutorial_window.update_guide_text(self.title_page.cget("text"))
        
        
    #Config osu! API page
    def second_page(self):
        logging.info("changed to second page gui")
          
        if hasattr(self, "TWITCH_CHANNEL"):
            self.TWITCH_CHANNEL.grid_forget()
        if hasattr(self, "TWITCH_ID"):
            self.TWITCH_ID.grid_forget()
        if hasattr(self, "TWITCH_SECRET"):
            self.TWITCH_SECRET.grid_forget()
        if hasattr(self, "IRC_NICK"):
            self.IRC_NICK.grid_forget()
        if hasattr(self, "IRC_PASSWORD"):
            self.IRC_PASSWORD.grid_forget()
        
        self.save_entries()
        
        self.title_page.configure(text="Config osu! API")

        self.OSU_ID = customtkinter.CTkEntry(self, placeholder_text="osu! API ID", width=300)
        self.OSU_ID.grid(row=2, column=0, padx=20, pady=(0,10), columnspan=2)
        
        if "OSU_ID" in self.saved_entries and self.saved_entries["OSU_ID"] != "": self.OSU_ID.insert(0, self.saved_entries.get("OSU_ID")) 
        
        self.OSU_SECRET = customtkinter.CTkEntry(self, placeholder_text="osu! API SECRET", width=300, show="*")
        self.OSU_SECRET.grid(row=3, column=0, padx=20, pady=(10,10), columnspan=2)
        
        if "OSU_SECRET" in self.saved_entries and self.saved_entries["OSU_SECRET"] != "": self.OSU_SECRET.insert(0, self.saved_entries.get("OSU_SECRET"))
        
        
        self.buttonP.configure(command=lambda: self.first_page(), state="normal")
        self.buttonN.configure(command=lambda: self.third_page(), text="Next")
        
        self.progressbar.set(0.5)
        
        if self.tutorial_window:
            self.tutorial_window.update_guide_text(self.title_page.cget("text"))
    
    #Config IRC page
    def third_page(self):
        logging.info("changed to third page gui")
        
        if hasattr(self, "OSU_ID"):
            self.OSU_ID.grid_forget()
        if hasattr(self, "OSU_SECRET"):
            self.OSU_SECRET.grid_forget()
        
        
        self.save_entries()
        
        self.title_page.configure(text="Config IRC connection")
        
        self.IRC_NICK = customtkinter.CTkEntry(self, placeholder_text="IRC nick", width=300,)
        self.IRC_NICK.grid(row=2, column=0, padx=20, pady=(0,10), columnspan=2)
        
        if "IRC_NICK" in self.saved_entries and self.saved_entries["IRC_NICK"] != "": 
            self.IRC_NICK.insert(0, self.saved_entries.get("IRC_NICK"))
        
        self.IRC_PASSWORD = customtkinter.CTkEntry(self, placeholder_text="IRC password", width=300, show="*")
        self.IRC_PASSWORD.grid(row=3, column=0, padx=20, pady=(10,10), columnspan=2)
        
        if "IRC_PASSWORD" in self.saved_entries and self.saved_entries["IRC_PASSWORD"] != "": 
            self.IRC_PASSWORD.insert(0, self.saved_entries.get("IRC_PASSWORD"))
        
        self.buttonP.configure(command=lambda: self.second_page(), state="normal")
        self.buttonN.configure(text="Finish", command=lambda: self.on_closing())
        
        self.progressbar.set(0.9)
        
        if self.tutorial_window:
            self.tutorial_window.update_guide_text(self.title_page.cget("text"))

    
    def on_closing(self):
        self.save_entries()
        
           # Close the tutorial window if it is open
        if self.tutorial_window:
            self.tutorial_window.destroy()
            self.tutorial_window = None
        
        #checking if all fields are filled
        missing_keys = [key for key, value in self.saved_entries.items() if value == ""]
        
        if missing_keys:
                logging.error(f"Missing value for {', '.join(missing_keys)}")
                messagebox.showerror("Nastąpił błąd", f"Proszę wypełnić wszystkie Pola.\nBrakujące pola: {', '.join(missing_keys)}")
                return
            
        #saving to .env file
        env_path = Path(__file__).parent / ".env"
        
        set_key(dotenv_path=env_path, key_to_set="TWITCH_CLIENT_ID", value_to_set=self.saved_entries["TWITCH_ID"], quote_mode= "never")
        set_key(dotenv_path=env_path, key_to_set="TWITCH_CLIENT_SECRET", value_to_set=self.saved_entries["TWITCH_SECRET"], quote_mode= "never")
        set_key(dotenv_path=env_path, key_to_set="TWITCH_TARGET_CHANNEL", value_to_set=self.saved_entries["TWITCH_CHANNEL"], quote_mode= "never")
        
        set_key(dotenv_path=env_path, key_to_set="OSU_CLIENT_ID", value_to_set=self.saved_entries["OSU_ID"], quote_mode= "never")
        set_key(dotenv_path=env_path, key_to_set="OSU_CLIENT_SECRET", value_to_set=self.saved_entries["OSU_SECRET"], quote_mode= "never")
        
        set_key(dotenv_path=env_path, key_to_set="IRC_NICK", value_to_set=self.saved_entries["IRC_NICK"], quote_mode= "never")
        set_key(dotenv_path=env_path, key_to_set="IRC_PASSWORD", value_to_set=self.saved_entries["IRC_PASSWORD"], quote_mode= "never")
        set_key(dotenv_path=env_path, key_to_set="FIRST_TIME_RUN", value_to_set="false", quote_mode= "never")


        logging.info("Saved entries to .env file")
        self.after_cancel("all")
        self.destroy()
        
        if self.first_time == "true":
                from Main_GUI import MainGui
                logging.info("opening Main GUI")
                gui = MainGui()
                gui.mainloop()
        
        return
            
            
class Tutorial(customtkinter.CTk):
    def __init__(self, parent, current_page):
        super().__init__()
        self.parent = parent
        logging.info("Starting tutorial")
        
        # Set the appearance mode and color theme
        customtkinter.set_appearance_mode("System") 
        customtkinter.set_default_color_theme("blue") 
        
        # window title and size
        self.title("Tutorial")
        self.geometry("400x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.resizable(False, False)
        
        self.guide_text = Text(self, font=("Nunito", 15), wrap=WORD, state="disabled", width=390, height=290, bg="#282424", fg="white", bd=0)
        self.guide_text.grid(row=0, column=0, padx=5, pady=5)
        
        self.update_guide_text(current_page)
        
    def update_guide_text(self, current_page):
        self.guide_text.configure(state="normal")
        self.guide_text.delete("1.0", END)
        
        start_text = "Wejdź na stronę: \n"
        
        if current_page == "Config Twitch API":
            self.insert_hyperlink(
                start_text,
                "https://dev.twitch.tv/console/apps",
                " i zarejestruj nową aplikację. W pierwszym polu wpisz nazwę aplikacji, w drugim URL przekierowania: http://localhost:17563 . Kategoria aplikacji wybierz Game Integration a typ klienta na Poufne. Po rejestracji, kliknij zarządzaj obok twojej aplikacji. Na dole strony znajdziesz Identyfikator klienta (Twitch Client ID) oraz do stworzenia Hasło klienta (Twitch Client SECRET)."
                
            )
            
        elif current_page == "Config osu! API":
            self.insert_hyperlink(
                start_text,
                "https://osu.ppy.sh/home/account/edit",
                ". Zjedź na dół strony i kliknij w przycisk Nowa aplikacja OAuth. W pierwszym polu wpisz nazwę aplikacji, w drugim URL przekierowania: http://localhost:17563 . Po stworzeniu aplikacji, klikając na edit możesz zobaczyć Client ID i Client Secret (client key)."
                
            )
            
        elif current_page == "Config IRC connection":
            self.insert_hyperlink(
                start_text,
                "https://osu.ppy.sh/home/account/edit",
                ". Na samym dole strony znajdziesz sekcję IRC. Po kliknięciu w przycisk Nowe Hasło starszego IRC pojawi się hasło oraz nick."
            )
            
            
        else:
            logging.error("Unknown page")
        
        
        self.guide_text.configure(state="disabled")
        
    def insert_hyperlink(self, start_text, url, end_text):
        
        self.guide_text.insert(END, start_text)
        start_index = self.guide_text.index(INSERT)
        self.guide_text.insert(END, url)
        end_index = self.guide_text.index(INSERT)
        self.guide_text.insert(END, end_text)
        
        # Add a tag for the hyperlink
        self.guide_text.tag_add("hyperlink", start_index, end_index)
        self.guide_text.tag_config("hyperlink", foreground="#7eaaff", underline=True)
        
        # Bind events for the hyperlink tag
        self.guide_text.tag_bind("hyperlink", "<Button-1>", lambda e: self.open_url(url))  # Open URL on click
        self.guide_text.tag_bind("hyperlink", "<Enter>", lambda e: self.guide_text.config(cursor="hand2"))  # Change cursor to hand2
        self.guide_text.tag_bind("hyperlink", "<Leave>", lambda e: self.guide_text.config(cursor=""))  # Reset cursor
        
    def open_url(self, url):
        webbrowser.open_new(url)