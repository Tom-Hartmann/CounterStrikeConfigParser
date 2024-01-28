import os
import sys
import time
import shutil
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser
from pathlib import Path

class SteamConfigParser:
    def __init__(self, config_file):
        print("Config Parser Running!")
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.check_config_values()

    def check_config_values(self):
        required_keys = ["path", "userfolder", "game_ids"]
        for key in required_keys:
            if key not in self.config["DEFAULT"] or not self.config["DEFAULT"][key].strip():
                raise ValueError(f"Value for {key} is missing or empty in the configuration file.")

    def get_userfolder_path(self):
        return os.path.join(self.get_path(), self.strip_quotes(self.config.get("DEFAULT", "userfolder")))

    def get_path(self):
        return self.strip_quotes(self.config.get("DEFAULT", "path"))

    def get_game_ids(self):
        game_ids_str = self.config.get("DEFAULT", "game_ids")
        return [id.strip() for id in game_ids_str.split(",")]

    def strip_quotes(self, value):
        return value.strip('"')

def create_backup_folder(backup_path, backup_folder):
    backup_path = backup_path.strip('"')
    folder_path = os.path.join(backup_path, backup_folder)
    if not os.path.exists(folder_path):
        print(f"Creating backup folder: {folder_path}")
        os.makedirs(folder_path)
        
class SteamFolderEventHandler(FileSystemEventHandler):
    def __init__(self, config_parser):
        self.config_parser = config_parser

    def on_created(self, event):
        if event.is_directory and event.src_path.split(os.sep)[-1].isdigit():
            new_folder = event.src_path
            game_ids = self.config_parser.get_game_ids()
            userfolder_path = self.config_parser.get_userfolder_path()

            new_folder_name = os.path.basename(new_folder)

            if new_folder_name in game_ids:
                print(f"Skipping copying for existing game folder: {new_folder}")
                return

            for game_id in game_ids:
                source_game_path = os.path.join(userfolder_path, game_id)
                dest_game_path = os.path.join(new_folder, game_id)

                if os.path.commonpath([source_game_path, dest_game_path]) == source_game_path:
                    print("Destination path is a subdirectory of the source. Skipping to prevent recursive copying.")
                    continue

                if os.path.exists(source_game_path):
                    print(f"Copying from {source_game_path} to {dest_game_path}")
                    try:
                        shutil.copytree(source_game_path, dest_game_path, dirs_exist_ok=True)
                    except Exception as e:
                        print(f"Error copying: {e}")
                else:
                    print(f"Source game path does not exist: {source_game_path}")

def monitor_steam_folder(config_parser):
    steam_path = os.path.dirname(config_parser.get_path())
    event_handler = SteamFolderEventHandler(config_parser)
    observer = Observer()
    observer.schedule(event_handler, steam_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def monitor_steam_folder(config_parser):
    steam_path = config_parser.get_path()
    event_handler = SteamFolderEventHandler(config_parser)
    observer = Observer()
    observer.schedule(event_handler, steam_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    config_file = "config.ini"
    config_parser = SteamConfigParser(config_file)
    monitor_steam_folder(config_parser)

if __name__ == "__main__":
    main()