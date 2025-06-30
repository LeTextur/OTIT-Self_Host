import tkinter.filedialog
import tkinter.messagebox
import customtkinter
import tkinter
import sys
import os
import threading
import logging
from Main import TwitchBot
from Setup_GUI import SetupGui
import asyncio
from dotenv import load_dotenv, set_key
from pathlib import Path
from lang_utils import Translator

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class ConsoleOutput:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        if message.strip() and self.widget:
            if self.widget:
                self.widget.configure(state="normal")
                self.widget.insert(tkinter.END, message)
                self.widget.see(tkinter.END)
                self.widget.configure(state="disabled")

    def flush(self):
        pass


class MainGui(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.translator = Translator(os.getenv("LANGUAGE", "en"))
        
        self.title("OTIT | Main GUI")
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
        logging.getLogger().setLevel(logging.INFO)
            
        # settings buttons - (settings_frame)
        self.start_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-start-btn"), command=self.start, fg_color="green")
        self.start_button.grid(row=0, column=0, padx=20, pady=(10, 5))
        
        self.setup_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-api-conf-btn"), command=self.api_setup)
        self.setup_button.grid(row=1, column=0, padx=20, pady=5)
        
        self.settings_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-settings-btn"), command=self.opening_settings)
        self.settings_button.grid(row=2, column=0, padx=20, pady=5)
        
        self.stop_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-stop-btn"), command=self.stop, state="disabled", fg_color="darkred")
        self.stop_button.grid(row=3, column=0, padx=20, pady=(300, 5))
        
        self.quit_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-quit-btn"), command=self.quit, fg_color="darkred")
        self.quit_button.grid(row=4, column=0, padx=20, pady=5)
        
        self.close_program = None
        self.started = False
        
        self.twitch_bot = None  # Store the instance here

        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()
        

        

        
    def opening_settings(self):
            load_dotenv(env_path, override=True)
            self.settings_button.configure(state="disabled")
            self.settings_window = Settings(on_save_callback=self.enable_settings_button)
            self.settings_window.protocol("WM_DELETE_WINDOW", lambda: self.closing_settings())
            self.settings_window.mainloop()

        # Re-enable the Settings button
    def enable_settings_button(self):
        self.settings_button.configure(state="normal")
            
    def closing_settings(self):
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
            self.settings_button.configure(state="normal")
        
    def api_setup(self):
            load_dotenv(env_path, override=True)
            
            self.setup_window = SetupGui()
            self.setup_window.mainloop()
        
    def start(self):
        if self.twitch_bot is None:
            self.twitch_bot = TwitchBot(loop=self.loop)
        
        logging.info(self.translator.t("main-gui-console-info1"))
        self.start_button.configure(state="disabled", fg_color="darkorange")
        self.setup_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._start_async, daemon=True).start()
        
        self.started = True
        
        
    def _start_async(self):
        asyncio.run_coroutine_threadsafe(self.twitch_bot.start_TwitchBot(), self.loop)
    
    def stop(self):
        if self.twitch_bot is not None:
            asyncio.run_coroutine_threadsafe(self.twitch_bot.stop_TwitchBot(), self.loop)
        self.started = False
        logging.info(self.translator.t("main-gui-console-info2"))
        self.start_button.configure(state="normal", fg_color="green")
        self.setup_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

        
    def quit(self):
            # Stop the bot if running
            if self.started and self.twitch_bot is not None:
                asyncio.run_coroutine_threadsafe(self.twitch_bot.stop_TwitchBot(), self.loop)
                self.started = False

            # Stop the asyncio event loop
            if self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.loop_thread.join(timeout=2)  # Wait for the thread to finish

            # Restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            # Destroy the GUI window
            self.destroy()

    def _finalize_quit(self):
        try:
            # Wait for the event loop thread to finish
            if hasattr(self, "loop_thread"):
                self.loop_thread.join(timeout=2)
            # Now close the loop
            if hasattr(self, "loop"):
                self.loop.close()
        except Exception as e:
            logging.error(self.translator.t("main-gui-console-error1"), error = e)
        finally:
            os._exit(0)
        
class Settings(customtkinter.CTk):
    def __init__(self, on_save_callback=None):
        super().__init__()
        self.translator = Translator(os.getenv("LANGUAGE", "en"))
        self.on_save_callback = on_save_callback
        
        # Set the appearance mode and color theme
        customtkinter.set_appearance_mode("System") 
        customtkinter.set_default_color_theme("blue") 
        
        self.grid_columnconfigure(0, weight=1)

        
        # window title and size
        self.title("OTIT | commands config")
        self.geometry("360x500")
        self.resizable(False, False)
        
        self.command_label = customtkinter.CTkLabel(self, text=self.translator.t("settings-gui-label1"), font=("Nunito", 20))
        self.command_label.grid(row=0, column=0, padx=20, pady=(20,5), columnspan=2)
        
        self.additional_text = tkinter.Text(self, font=("Nunito", 10), wrap=tkinter.WORD, bg="#282424", fg="#dce4ee", bd=0, height=3)
        self.additional_text.insert("1.0",self.translator.t("settings-gui-text"))
        self.additional_text.configure(state="disabled")
        self.additional_text.grid(row=1, column=0, pady=5, padx=20, columnspan=2)
        
        self.pp_switch = customtkinter.CTkSwitch(self, text=self.translator.t("settings-gui-switch1"), font=("Nunito", 12), command=self.toggle_widgets)
        self.pp_switch.grid(row=2, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.pp_label = customtkinter.CTkLabel(self, text=self.translator.t("settings-gui-label2"), font=("Nunito", 10), anchor="w")
        
        self.pp_export_file_directory = customtkinter.CTkEntry(self, placeholder_text="PP export file directory", font=("Nunito", 12), state="disabled", width=450)
        
        self.pp_export_file_directory_browse = customtkinter.CTkButton(self, text=self.translator.t("settings-gui-directory-browse-btn"), font=("Nunito", 12), width=50, state="disabled", command=self.pp_file_import_directory)
        
        
        self.np_switch = customtkinter.CTkSwitch(self, text=self.translator.t("settings-gui-switch2"), font=("Nunito", 12), command=self.toggle_widgets)
        self.np_switch.grid(row=5, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.np_label = customtkinter.CTkLabel(self, text=self.translator.t("settings-gui-label3"), font=("Nunito", 10), anchor="w")
        
        self.np_export_file_directory = customtkinter.CTkEntry(self, placeholder_text="NP export file directory", font=("Nunito", 12), state="disabled", width=250)
        
        self.np_export_file_directory_browse = customtkinter.CTkButton(self, text=self.translator.t("settings-gui-directory-browse-btn"), font=("Nunito", 12), width=50, state="disabled", command=self.np_file_import_directory)
        
        
        self.settings_tutorial = customtkinter.CTkButton(self, text=self.translator.t("settings-gui-tutorial-btn"), font=("Nunito", 12), width=100, state="disabled")
        self.settings_tutorial.grid(row=8, column=0, padx=(20,5), pady=(80,20), sticky="w")
        
        self.settings_buttons = customtkinter.CTkButton(self, text=self.translator.t("settings-gui-save-btn"), font=("Nunito", 12),  width=100, command=self.save_path_entries)
        self.settings_buttons.grid(row=8, column=1, padx=(0,20), pady=(80,20), sticky="e")
        
        #check if PP command was enabled
        if os.getenv("PP_ENABLED") == "true":
            self.pp_switch.select()
            self.toggle_widgets()
            if os.getenv("PP_FILE_PATH"):
                self.pp_export_file_directory.insert(0, os.getenv("PP_FILE_PATH"))
        
        #check if NP command was enabled
        if os.getenv("NP_ENABLED") == "true":
            self.np_switch.select()
            self.toggle_widgets()
            if os.getenv("NP_FILE_PATH"):
                self.np_export_file_directory.insert(0, os.getenv("NP_FILE_PATH"))
        
        
        
    def toggle_widgets(self):
        
        if self.pp_switch.get():  # If PP is enabled
            
            self.pp_label.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="ew", columnspan=2)
            
            self.pp_export_file_directory.configure(state="normal")
            self.pp_export_file_directory.grid(row=4, column=0, padx=(20, 5), pady=(2, 5), sticky="ew")
            
            self.pp_export_file_directory_browse.configure(state="normal")
            self.pp_export_file_directory_browse.grid(row=4, column=1, padx=(0,20), pady=(2, 5), sticky="ew")
            
            
        else:  # If PP is disabled
            
            self.pp_export_file_directory.configure(state="disabled")
            self.pp_export_file_directory.grid_forget()
            
            self.pp_export_file_directory_browse.configure(state="disabled")
            self.pp_export_file_directory_browse.grid_forget()
            
            self.pp_label.grid_forget()
            
            
        if self.np_switch.get():  # If NP is enabled
            
            self.np_label.grid(row=6, column=0, padx=20, pady=(5, 0), sticky="ew", columnspan=2)
            
            self.np_export_file_directory.configure(state="normal")
            self.np_export_file_directory.grid(row=7, column=0, padx=(20, 5), pady=(2, 5), sticky="ew")
              
            self.np_export_file_directory_browse.configure(state="normal")
            self.np_export_file_directory_browse.grid(row=7, column=1, padx=(0,20), pady=(2, 5), sticky="ew")
            
            
        else:  # If NP id disabled
            
            self.np_export_file_directory.configure(state="disabled")
            self.np_export_file_directory.grid_forget()
            
            self.np_export_file_directory_browse.configure(state="disabled")
            self.np_export_file_directory_browse.grid_forget()
            
            self.np_label.grid_forget()
            
            
    #look for txt file directory and insert it in entry
    def pp_file_import_directory(self):
        self.pp_file_path = tkinter.filedialog.askopenfilename(title="Select PP file directory", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.pp_file_path:
            self.pp_export_file_directory.delete(0, tkinter.END)
            self.pp_export_file_directory.insert(0, self.pp_file_path)
        
    def np_file_import_directory(self):
        self.np_file_path = tkinter.filedialog.askopenfilename(title="Select NP file directory", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.np_file_path:
            self.np_export_file_directory.delete(0, tkinter.END)
            self.np_export_file_directory.insert(0, self.np_file_path)
    
    
    #store entries in to .env file        
    def save_path_entries(self):
        
        #saving for np
        if self.np_switch.get():
            np_file_directory = self.np_export_file_directory.get()
            
            if np_file_directory == "":
                logging.error(self.translator.t("settings-gui-error1"))
                tkinter.messagebox.showerror("Blank Entry error" , self.translator.t("settings-gui-messagebox-error"))
                return
                
            elif os.getenv("NP_FILE_PATH") != np_file_directory:
                set_key(dotenv_path=env_path, key_to_set="NP_FILE_PATH", value_to_set=np_file_directory,)
            set_key(dotenv_path=env_path, key_to_set="NP_ENABLED", value_to_set="true", quote_mode="never")
        else: set_key(dotenv_path=env_path, key_to_set="NP_ENABLED", value_to_set="false", quote_mode="never")
        
        #saving for pp
        if self.pp_switch.get():
            pp_file_directory = self.pp_export_file_directory.get()
            
            if pp_file_directory == "":
                logging.error(self.translator.t("settings-gui-error2"))
                tkinter.messagebox.showerror("Blank Entry error" , self.translator.t("settings-gui-messagebox-error"))
                return
            
            elif os.getenv("PP_FILE_PATH") != pp_file_directory:
                set_key(dotenv_path=env_path, key_to_set="PP_FILE_PATH", value_to_set=pp_file_directory)
            set_key(dotenv_path=env_path, key_to_set="PP_ENABLED", value_to_set="true", quote_mode="never")
        else: set_key(dotenv_path=env_path, key_to_set="PP_ENABLED", value_to_set="false", quote_mode="never")
        
        self.after_cancel("all")
        
        if self.on_save_callback:
            self.on_save_callback()
            
        self.destroy()
        logging.info(self.translator.t("main-gui-console-info3"))

