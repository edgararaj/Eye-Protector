"""
Python 3.7.0
-> Background script for the eye protector notification system
Written by: Edgar Araújo (edgararaj@gmail.com)
Date (start): 12/04/2019
Date (latest modification): 22/06/2019
"""

import json
import time
from pathlib import Path
from win10toast import ToastNotifier
import psutil
import os

import log

PROGRAM_DATA_FOLDER = "data/"


def script_already_running():
    instances = 0

    for pid in psutil.pids():
        process = psutil.Process(pid)
        if process.name() == "pythonw.exe" and len(process.cmdline()) > 1 and os.path.basename(__file__) in process.cmdline()[-1]:
            instances += 1
            if instances > 1:
                return True

    return False


class SettingsHandler:
    def __init__(self):
        self.SETTINGS_FILE = Path(r"C:\Eye Protector\settings.json")
        self.LIVE_SETTINGS_FILE = Path(r"C:\Eye Protector\live_settings.json")
        self.DEFAULT_SETTINGS = {"rest_period_minutes": 15, "work_period_minutes": 45}
        self.settings = self.DEFAULT_SETTINGS.copy()

    def write_live_settings(self):
        with open(self.LIVE_SETTINGS_FILE, "w") as file:
            json.dump(self.settings, file, indent=2)

    def update(self):
        if self.SETTINGS_FILE.is_file():
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
            log.error("File not found")
            return


if __name__ == "__main__":
    if script_already_running():
        exit(1)

    settings = SettingsHandler()
    settings.update()
    settings.write_live_settings()

    print(f"BG script running with settings: {settings.settings}")

    toaster = ToastNotifier()

    while True:
        time.sleep(settings.settings["work_period_minutes"] * 60)

        toaster.show_toast(
            "Eye Protector",
            f"Give your eyes a rest for at least {settings.settings['rest_period_minutes']} minutes.",
            icon_path=PROGRAM_DATA_FOLDER + "icon_w.ico",
            threaded=True
        )

        time.sleep(settings.settings["rest_period_minutes"] * 60)
