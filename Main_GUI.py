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
        icon = Path(__file__).parent / "OTIT.ico"
        self.iconbitmap(icon)
        
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
        
        self.setup_button = customtkinter.CTkButton(self.settings_frame, text=self.translator.t("main-gui-api-conf-btn"), command=self.opening_api_setup)
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
            self.settings_window = Settings(main_gui=self, on_save_callback=self.enable_settings_button)
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
        
    def opening_api_setup(self):
            load_dotenv(env_path, override=True)
            self.setup_button.configure(state="disabled")
            self.setup_window = SetupGui(main_gui=self, on_save_callback=self.enable_setup_button)
            self.setup_window.protocol("WM_DELETE_WINDOW", lambda: self.closing_api_setup())
            self.setup_window.mainloop()
            
    def enable_setup_button(self):
        self.setup_button.configure(state="normal")
            
    def closing_api_setup(self):
        if self.setup_window:
            self.setup_window.destroy()
            self.setup_window = None
            self.setup_button.configure(state="normal")
        
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

            # Destroy the settings window if open
            if hasattr(self, "settings_window") and self.settings_window is not None:
                try:
                    self.settings_window.destroy()
                except Exception:
                    pass
                self.settings_window = None

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
            
    def refresh_texts(self):
        self.start_button.configure(text=self.translator.t("main-gui-start-btn"))
        self.setup_button.configure(text=self.translator.t("main-gui-api-conf-btn"))
        self.settings_button.configure(text=self.translator.t("main-gui-settings-btn"))
        self.stop_button.configure(text=self.translator.t("main-gui-stop-btn"))
        self.quit_button.configure(text=self.translator.t("main-gui-quit-btn"))
        
        
class Settings(customtkinter.CTk):
    def __init__(self, on_save_callback=None, main_gui=None):
        super().__init__()
        self.translator = Translator(os.getenv("LANGUAGE", "en"))
        self.on_save_callback = on_save_callback
        self.main_gui = main_gui
        # Set the appearance mode and color theme
        customtkinter.set_appearance_mode("System") 
        customtkinter.set_default_color_theme("blue")
        icon = Path(__file__).parent / "OTIT.ico"
        self.iconbitmap(icon)
        

        
        # window title and size
        self.title(f"OTIT | {self.translator.t("settings-gui-label1")}")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Settings frame
        self.frame = customtkinter.CTkScrollableFrame(self, width=400, height=500)
        self.frame.pack(fill="both", expand=True)
        
        self.frame.grid_columnconfigure(0, weight=1)  # label
        
        # row 0
        self.main_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label1"), font=("Nunito", 32))
        self.main_label.grid(row=0, column=0, columnspan=2, padx=(20), pady=(10,5), sticky="ew")
        
        # row 1  # to do 
        self.command_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label2"), font=("Nunito", 20))
        self.command_label.grid(row=1, column=0, padx=(20), pady=(20,5), sticky="w")
        
        # row 2
        self.additional_text = tkinter.Text(self.frame, font=("Nunito", 10), wrap=tkinter.WORD, bg="#2B2B2B", fg="#dce4ee", bd=0, height=3)
        self.additional_text.insert("1.0",self.translator.t("settings-gui-text"))
        self.additional_text.configure(state="disabled")
        self.additional_text.grid(row=2, column=0, pady=5, padx=(20), columnspan=2, sticky="w")
        
        # row 3
        self.pp_switch_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-switch1"), font=("Nunito", 12), anchor="w")
        self.pp_switch_label.grid(row=3, column=0, padx=(20, 0), pady=(5, 0), sticky="w")

        self.pp_switch = customtkinter.CTkSwitch(self.frame, command=self.toggle_widgets, text="", width=110, height=30, switch_width=40, switch_height=20)
        self.pp_switch.grid(row=3, column=1, padx=(0, 20), pady=(5, 0), sticky="e")

        # row 4
        self.pp_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label3"), font=("Nunito", 10), anchor="w")
        
        # row 5
        self.pp_export_file_directory = customtkinter.CTkEntry(self.frame, placeholder_text="PP export file directory", font=("Nunito", 12), state="disabled", width=450)
        
        # col 1
        self.pp_export_file_directory_browse = customtkinter.CTkButton(self.frame, text=self.translator.t("settings-gui-directory-browse-btn"), font=("Nunito", 12), width=50, state="disabled", command=self.pp_file_import_directory)
        
        # row 6
        self.np_switch_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-switch2"), font=("Nunito", 12), anchor="w")
        self.np_switch_label.grid(row=6, column=0, padx=(20, 5), pady=(5, 0), sticky="w")

        self.np_switch = customtkinter.CTkSwitch(self.frame, command=self.toggle_widgets, text="", width=110, height=30, switch_width=40, switch_height=20)
        self.np_switch.grid(row=6, column=1, padx=(5, 20), pady=(5, 0), sticky="e")

        # row 7
        self.np_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label4"), font=("Nunito", 10), anchor="w")
        
        # row 8
        self.np_export_file_directory = customtkinter.CTkEntry(self.frame, placeholder_text="NP export file directory", font=("Nunito", 12), state="disabled", width=250)
        
        # col 1
        self.np_export_file_directory_browse = customtkinter.CTkButton(self.frame, text=self.translator.t("settings-gui-directory-browse-btn"), font=("Nunito", 12), width=50, state="disabled", command=self.np_file_import_directory)
        
        # row 9
        self.lang_main_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label5"), font=("Nunito", 20))
        self.lang_main_label.grid(row=9, column=0, padx=(20), pady=(20,5), sticky="w")
        
        # row 10 
        self.lang_label = customtkinter.CTkLabel(self.frame, text="Choose language" , font=("Nunito", 12), anchor="w")
        self.lang_label.grid(row=10, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        # Dynamically get available languages from lang folder
        lang_dir = Path(__file__).parent / "lang"
        lang_files = [f for f in os.listdir(lang_dir) if f.endswith(".json")]
        self.available_languages = [os.path.splitext(f)[0] for f in lang_files]

        self.language_var = customtkinter.StringVar(value=os.getenv("LANGUAGE", "en"))
        self.language_menu = customtkinter.CTkOptionMenu(self.frame, values=self.available_languages, variable=self.language_var, command=self.set_language)
        
        # row 11
        self.language_menu.grid(row=11, column=0, padx=20, sticky="ew")
        
        #row 12 min label
        self.min_difficulty_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label6"), font=("Nunito", 12), anchor="w")
        self.min_difficulty_label.grid(row=12, column=0, padx=20, pady=(20, 0), sticky="ew", columnspan=2)
        
        # row 13 min slider
        diff_limit_str = os.getenv("DIFF_LIMIT")
        
        try:
            self.saved_difficulty_limit = diff_limit_str.split(",")
        except Exception:
            self.saved_difficulty_limit = [0,15]
        
        self.min_difficulty_slider = customtkinter.CTkSlider(self.frame,width=350, number_of_steps=30, from_=0, to=15, command=lambda value: self.update_difficulty_variable(value, which_slider=False))
        self.min_difficulty_slider.set(float(self.saved_difficulty_limit[0]))
        self.min_difficulty_slider.grid(row=13, column=0, padx=20, pady=(2,0), sticky="ew")  
        
        # row 14 variable label for min slider
        self.min_difficulty_variable = customtkinter.CTkLabel(self.frame, text=f"{self.min_difficulty_slider.get():.1f}",font=("Nunito", 16))
        self.min_difficulty_variable.grid(row=14, column=0, padx=20, pady=(0, 10), sticky="w")
        
        #row 15 max label
        self.max_difficulty_label = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-label7"), font=("Nunito", 12), anchor="w")
        self.max_difficulty_label.grid(row=15, column=0, padx=20, pady=(0, 0), sticky="ew", columnspan=2)
        
        # row 16 max slider
        self.max_difficulty_slider = customtkinter.CTkSlider(self.frame,width=350, number_of_steps=30, from_=0, to=15,command=lambda value: self.update_difficulty_variable(value, which_slider=True))
        self.max_difficulty_slider.set(float(self.saved_difficulty_limit[1]))
        self.max_difficulty_slider.grid(row=16, column=0, padx=20, pady=(2,0), sticky="ew")
        
        # row 17 variable label for max slider
        self.max_difficulty_variable = customtkinter.CTkLabel(self.frame, text=f"{self.min_difficulty_slider.get():.1f}",font=("Nunito", 16))
        self.max_difficulty_variable.grid(row=17, column=0, padx=20, pady=(0, 10), sticky="w")
                
        # row 18 warning for bad slider variables
        self.warning_slider_note = customtkinter.CTkLabel(self.frame, text=self.translator.t("settings-gui-diff-limit-warning"), font=("Nunito", 12), text_color="red")

        self.update_difficulty_variable(value=self.saved_difficulty_limit[0], which_slider=False)
        self.update_difficulty_variable(value=self.saved_difficulty_limit[1], which_slider=True)
        
        # row 30
        self.settings_tutorial = customtkinter.CTkButton(self.frame, text=self.translator.t("settings-gui-tutorial-btn"), font=("Nunito", 12), width=100, state="disabled")
        self.settings_tutorial.grid(row=30, column=0, padx=(20,5), pady=(60,20), sticky="w")
        
        # col 1
        self.settings_buttons = customtkinter.CTkButton(self.frame, text=self.translator.t("settings-gui-save-btn"), font=("Nunito", 12),  width=100, command=self.save_path_entries)
        self.settings_buttons.grid(row=30, column=1, padx=(0,20), pady=(60,20), sticky="e")
        
        
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
        
    def update_difficulty_variable(self, value, which_slider):
        # Calculate label position under the handler
        slider_min = 0
        slider_max = 15
        slider_width = 185
        rel_x = (float(value) - slider_min) / (slider_max - slider_min)
        x = 17 + rel_x * slider_width
        
        # checking if minimum difficulty limit is higher to show warning text and indicators
        self.slider_min_value = self.min_difficulty_slider.get()
        self.slider_max_value = self.max_difficulty_slider.get()
        if self.slider_max_value == 0:
            self.slider_max_value = self.slider_max_value + self.slider_min_value
        if self.slider_min_value > self.slider_max_value:
            self.warning_slider_note.grid(row=18, columnspan=2, column=0,padx=(20,0), pady=(0, 10), sticky="w")
        else:
            self.warning_slider_note.grid_forget()
        
        # checking which slider must be updated
        if which_slider:
            if value == 0 or value == 15:
                self.max_difficulty_variable.configure(text="∞ ★")
                x = x+6
            else:
                self.max_difficulty_variable.configure(text=f"{float(value):.1f}★")
            
            self.max_difficulty_variable.grid(row=17, column=0, padx=(x,0), pady=(0, 10), sticky="w", columnspan=2)
        else:
            self.min_difficulty_variable.configure(text=f"{float(value):.1f}★")
            self.min_difficulty_variable.grid(row=14, column=0, padx=(x,0), pady=(0, 10), sticky="w", columnspan=2)
            

        
    def toggle_widgets(self):
        
        if self.pp_switch.get():  # If PP is enabled
            
            self.pp_label.grid(row=4, column=0, padx=20, pady=(5, 0), sticky="ew", columnspan=2)
            
            self.pp_export_file_directory.configure(state="normal")
            self.pp_export_file_directory.grid(row=5, column=0, padx=(20, 5), pady=(5, 2), sticky="ew")
            
            self.pp_export_file_directory_browse.configure(state="normal")
            self.pp_export_file_directory_browse.grid(row=5, column=1, padx=(0,20), pady=(5, 2), sticky="ew")
            
            
        else:  # If PP is disabled
            
            self.pp_export_file_directory.configure(state="disabled")
            self.pp_export_file_directory.grid_forget()
            
            self.pp_export_file_directory_browse.configure(state="disabled")
            self.pp_export_file_directory_browse.grid_forget()
            
            self.pp_label.grid_forget()
            
            
        if self.np_switch.get():  # If NP is enabled
            
            self.np_label.grid(row=7, column=0, padx=20, pady=(5, 0), sticky="ew", columnspan=2)
            
            self.np_export_file_directory.configure(state="normal")
            self.np_export_file_directory.grid(row=8, column=0, padx=(20, 5), pady=(2, 5), sticky="ew")
              
            self.np_export_file_directory_browse.configure(state="normal")
            self.np_export_file_directory_browse.grid(row=8, column=1, padx=(0,20), pady=(2, 5), sticky="ew")
            
            
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
        error_text1 = self.translator.t("settings-gui-messagebox-error1")
        error_text2 = self.translator.t("settings-gui-messagebox-error2")
        
        
        # saving difficulty limits per request
        self.slider_min_value = self.min_difficulty_slider.get()
        self.slider_max_value = self.max_difficulty_slider.get()
        
        if self.slider_min_value > self.slider_max_value:
            tkinter.messagebox.showerror("bad variable error", error_text2)
            return
        else:
            set_key(dotenv_path=env_path, key_to_set="DIFF_LIMIT", value_to_set=f"{self.slider_min_value},{self.slider_max_value}", quote_mode="never")
        
        #saving for np
        if self.np_switch.get():
            np_file_directory = self.np_export_file_directory.get()
            
            if np_file_directory == "":
                logging.error(self.translator.t("settings-gui-error1"))
                tkinter.messagebox.showerror("Blank Entry error" , error_text1)
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
                tkinter.messagebox.showerror("Blank Entry error" , error_text1)
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
        
    def set_language(self, lang_code):
        self.translator.set_language(lang_code)
        self.refresh_texts()

    def refresh_texts(self):
        self.title(f"OTIT | {self.translator.t("settings-gui-label1")}")
        self.main_label.configure(text=self.translator.t("settings-gui-label1"))
        self.additional_text.configure(state="normal")
        self.additional_text.delete("1.0", tkinter.END)
        self.additional_text.insert("1.0", self.translator.t("settings-gui-text"))
        self.additional_text.configure(state="disabled")
        self.pp_switch_label.configure(text=self.translator.t("settings-gui-switch1"))
        self.pp_label.configure(text=self.translator.t("settings-gui-label2"))
        self.pp_export_file_directory_browse.configure(text=self.translator.t("settings-gui-directory-browse-btn"))
        self.np_switch_label.configure(text=self.translator.t("settings-gui-switch2"))
        self.np_label.configure(text=self.translator.t("settings-gui-label3"))
        self.np_export_file_directory_browse.configure(text=self.translator.t("settings-gui-directory-browse-btn"))
        self.settings_tutorial.configure(text=self.translator.t("settings-gui-tutorial-btn"))
        self.settings_buttons.configure(text=self.translator.t("settings-gui-save-btn"))
        self.min_difficulty_label.configure(text=self.translator.t("settings-gui-label6"))
        self.max_difficulty_label.configure(text=self.translator.t("settings-gui-label7"))
        self.warning_slider_note.configure(text=self.translator.t("settings-gui-diff-limit-warning"))
        self.command_label.configure(text=self.translator.t("settings-gui-label2"))
        
        load_dotenv(dotenv_path=env_path, override=True)

        if self.main_gui is not None:
            self.main_gui.translator = self.translator
            self.main_gui.refresh_texts()