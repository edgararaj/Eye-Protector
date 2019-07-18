"""
Python 3.7.0
-> GUI for the eye protector notification system
Written by: Edgar Araújo (edgararaj@gmail.com)
Date (start): 12/04/2019
Date (latest modification): 18/07/2019
"""

import sys
import time
import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk
import psutil
import subprocess

import log

PROGRAM_DATA_FOLDER = "data/"


class App(tk.Tk):
    def __init__(self):
        # Initialize tkinter
        tk.Tk.__init__(self)

        # Set tkinter window properties
        self.title("Eye Protector Control Panel")
        self.iconbitmap(PROGRAM_DATA_FOLDER + "icon_b.ico")
        self.resizable(0, 0)

        # Settings stuff
        self.settings = SettingsHandler(self)
        self.settings.update()

        # Initialize gui
        self.gui()

    def gui(self):
        # FRAME -> Margin Frame
        margin_frame = tk.Frame(self)
        margin_frame.pack(side=tk.BOTTOM, padx=20, pady=20)

        # FRAME -> BG script manager Frame
        bg_script_manager_frame = BGScriptManagerFrame(self, self.settings)
        bg_script_manager_frame.pack(side=tk.TOP, fill=tk.X)

        # FRAME -> Options Frame
        options_frame = tk.Frame(margin_frame)
        options_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # FRAME -> Body Frame
        body_frame = tk.Frame(margin_frame)
        body_frame.pack(side=tk.BOTTOM, pady=20)

        # LABEL -> Title label
        title_label = tk.Label(margin_frame, text="Eye Protector", font=("", 20))
        title_label.pack(side=tk.TOP)

        # BUTTON -> Apply Button
        apply_button = ttk.Button(options_frame, text="Apply", command=self.settings.apply)
        apply_button.pack(side=tk.RIGHT, padx=(5, 0))

        # BUTTON -> Cancel Button
        cancel_button = ttk.Button(options_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # BUTTON -> OK Button
        ok_button = ttk.Button(options_frame, text="OK", command=self.settings.ok)
        ok_button.pack(side=tk.RIGHT, padx=5)

        # Work period setting
        work_period = Setting(
            body_frame,
            settings=self.settings,
            name="work_period_minutes",
            gui_name="Work Period (minutes):"
        )
        work_period.pack(pady=(0, 20))

        # Rest period setting
        rest_period = Setting(
            body_frame,
            settings=self.settings,
            name="rest_period_minutes",
            gui_name="Rest Period (minutes):"
        )
        rest_period.pack(side=tk.RIGHT)


class Setting(tk.Frame):
    def __init__(self, parent, settings, name, gui_name, min_v=1, max_v=60):
        tk.Frame.__init__(self, parent)

        self.settings = settings
        self.name = name
        self.gui_name = gui_name
        self.min_v = min_v
        self.max_v = max_v

        # Add setting object to settings list
        self.settings.settings_list[self.name] = self

        # Declare setting variable
        self.var = tk.IntVar()
        self.var.set(0)

        # Initialize gui
        self.gui()

    def gui(self):
        # Slider
        slider = ttk.Scale(
            self,
            from_=self.min_v,
            to=self.max_v,
            orient=tk.HORIZONTAL,
            length=250,
            command=lambda v: self.var.set(int(float(v)))
        )
        slider.set(self.settings.settings[self.name])
        slider.grid(column=1, row=0, padx=10)

        # Slider Text
        slider_text = tk.Label(self, text=self.gui_name)
        slider_text.grid(column=0, row=0, sticky=tk.E)

        # Slider Value
        slider_value = tk.Label(self, textvariable=self.var, width=len(str(self.max_v)))
        slider_value.grid(column=2, row=0, padx=(0, 10))

        # Reset button
        reset_button = ttk.Button(
            self,
            text="Reset",
            command=lambda: slider.set(self.settings.DEFAULT_SETTINGS[self.name])
        )
        reset_button.grid(column=3, row=0)


class BGScriptManager:
    def __init__(self, name):
        self.name = name
        self.pid = None
        self.running = None
        self.update_running()

    def run(self):
        bg_script_new_process = subprocess.Popen(sys.executable.replace("python.exe", "pythonw.exe") + " " + self.name)

        self.pid = bg_script_new_process.pid
        self.running = True
        log.info("Background script running")

    def stop(self):
        os.system(f"taskkill /F /PID {self.pid}")

        self.pid = None
        self.running = False
        log.info("Background script stopped")

    def restart(self):
        self.stop()
        self.run()

    def update_running(self):
        for pid in psutil.pids():
            process = psutil.Process(pid)
            if process.name() == "pythonw.exe" and len(process.cmdline()) > 1 and self.name in process.cmdline()[-1]:
                self.pid = pid
                self.running = True
                return

        self.running = False


class BGScriptManagerFrame(tk.Frame):
    def __init__(self, parent, settings):
        self.settings = settings
        self.bg_script = BGScriptManager("bg_script.pyw")
        self.settings.bg_script = self.bg_script
        self.settings.bg_script_frame = self

        self.last_bg_script_running_state = None

        tk.Frame.__init__(self, parent)

        # Status label
        self.label = tk.Label(self, fg="white")
        self.label.pack(side=tk.LEFT, padx=20, pady=20)

        # Status run/stop button
        self.button = ttk.Button(self, command=self.button_press)
        self.button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.restart_button = ttk.Button(self, text="Restart", command=self.restart_button_click)
        self.restart_button.pack(side=tk.RIGHT)

        self.settings.update_bg_script_restart_button_state()
        self.update_frame()

    def restart_button_click(self):
        self.bg_script.restart()
        time.sleep(1.5)
        self.settings.update_bg_script_restart_button_state()

    def button_press(self):
        self.restart_button.pack_forget()
        self.bg_script.update_running()

        if self.bg_script.running == self.last_bg_script_running_state:
            if self.bg_script.running:
                self.bg_script.stop()
            else:
                self.bg_script.run()

        self.update_frame()

    def update_frame(self):
        label_text = f"State: {'ON' if self.bg_script.running is True else 'OFF'}"
        frame_bg = ("#00b400" if self.bg_script.running is True else "#b40000")
        label_bg = frame_bg
        button_text = ("Stop" if self.bg_script.running is True else "Run")

        self.label.configure(text=label_text)
        self.label.configure(bg=label_bg)
        self.configure(bg=frame_bg)
        self.button.configure(text=button_text)
        self.last_bg_script_running_state = self.bg_script.running


class SettingsHandler:
    def __init__(self, parent):
        self.parent = parent

        self.bg_script = None
        self.bg_script_frame = None

        self.DEFAULT_SETTINGS = {"work_period_minutes": 45, "rest_period_minutes": 15}
        self.SETTINGS_FILE = Path(r"C:\Eye Protector\settings.json")
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.LIVE_SETTINGS_FILE = Path(r"C:\Eye Protector\live_settings.json")
        self.settings_list = {}

    def live_settings_match_settings(self):
        if self.LIVE_SETTINGS_FILE.is_file():
            with open(self.LIVE_SETTINGS_FILE, "r") as file:
                try:
                    live_settings = json.load(file)
                except json.decoder.JSONDecodeError:
                    log.error("Impossible to read live settings file")
                    return False

            for setting in live_settings.keys():
                if setting not in self.DEFAULT_SETTINGS or live_settings[setting] != self.settings[setting]:
                    return False

            return True

        else:
            log.error("Live settings file not found")
            return False

    def update_bg_script_restart_button_state(self):
        if not self.live_settings_match_settings() and self.bg_script.running:
            self.bg_script_frame.restart_button.pack(side=tk.RIGHT)
        else:
            self.bg_script_frame.restart_button.pack_forget()

    def update(self):
        if self.SETTINGS_FILE.is_file():
            log.info("Updating settings...")

            with open(self.SETTINGS_FILE, "r") as file:
                try:
                    self.settings = json.load(file)
                except json.decoder.JSONDecodeError:
                    log.error("Impossible to read settings file")
                    return

            for setting in self.settings.keys():
                if setting not in self.DEFAULT_SETTINGS:
                    self.settings = self.DEFAULT_SETTINGS.copy()
                    break
            else:
                log.info("Settings successfully updated")

        else:
            log.error("Settings file not found")
            return

    def apply(self):
        self.update()

        counter = 0

        # Get current status of settings variables to apply
        for key in self.settings:
            if self.settings[key] == self.settings_list[key].var.get():
                counter += 1
            else:
                self.settings[key] = self.settings_list[key].var.get()

        if counter != len(self.settings):
            # Write to disk
            log.info("Applying settings...")

            with open(self.SETTINGS_FILE, "w") as file:
                json.dump(self.settings, file, indent=2)

            log.info("Settings successfully saved")
            self.update_bg_script_restart_button_state()

    def ok(self):
        self.apply()
        self.parent.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
