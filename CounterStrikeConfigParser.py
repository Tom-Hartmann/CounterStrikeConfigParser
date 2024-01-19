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
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.check_config_values()

    def check_config_values(self):
        required_keys = ["path", "backup_path", "userfolder", "backup_folder", "max_versions", "game_ids"]
        for key in required_keys:
            if key not in self.config["DEFAULT"] or not self.config["DEFAULT"][key].strip():
                raise ValueError(f"Value for {key} is missing or empty in the configuration file.")

    def get_userfolder_path(self):
        return os.path.join(self.get_path(), self.strip_quotes(self.config.get("DEFAULT", "userfolder")))

    def get_path(self):
        return self.strip_quotes(self.config.get("DEFAULT", "path"))

    def get_backup_path(self):
        return self.strip_quotes(self.config.get("DEFAULT", "backup_path"))

    def get_backup_folder(self):
        return self.strip_quotes(self.config.get("DEFAULT", "backup_folder"))

    def get_max_versions(self):
        max_versions_str = self.config.get("DEFAULT", "max_versions")
        return int(max_versions_str.strip('"')) if max_versions_str else None

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
        
def backup_files(src, dest, max_versions):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    backup_folder = f"{dest}_{timestamp}"
    backup_path = os.path.join(dest, backup_folder)
    os.makedirs(backup_path)
    
    files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src,f))]
    
    for file in files:
        src_file = os.path.join(src,file)
        dest_file = os.path.join(backup_path,file)
        shutil.copy2(src_file,dest_file)
        
    # Cleanup
    if max_versions:
        existing_backups = sorted(Path(dest).iterdir(), key =os.path.getmtime, reverse = True)
        for old_backup in existing_backups[max_versions:]:
            shutil.rmtree(old_backup)

class SteamFolderEventHandler(FileSystemEventHandler):
    def __init__(self, config_parser):
        self.config_parser = config_parser

    def on_created(self, event):
        if event.is_directory:
            new_folder = event.src_path
            game_ids = self.config_parser.get_game_ids()
            userfolder_path = self.config_parser.get_userfolder_path()

            for game_id in game_ids:
                source_game_path = os.path.join(userfolder_path, game_id)
                dest_game_path = os.path.join(new_folder, game_id)

                if os.path.commonpath([source_game_path, dest_game_path]) != source_game_path:
                    if os.path.exists(source_game_path):
                        print(f"Copying from {source_game_path} to {dest_game_path}")
                    try:
                        shutil.copytree(source_game_path, dest_game_path, dirs_exist_ok=True)
                    except Exception as e:
                        print(f"Error copying: {e}")
                else:
                    print(f"Source game path does not exist: {source_game_path}")
            else:
                print("Destination path is a subdirectory of the source. Skipping to prevent recursive copying.")

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

    backup_path = config_parser.get_backup_path()
    backup_folder = config_parser.get_backup_folder()
    max_versions = config_parser.get_max_versions()
    
    print(f"Configuration values:")
    print(f" - Backup Path: {backup_path}")
    print(f" - Backup Folder: {backup_folder}")
    print(f" - Max Versions: {max_versions}")

    create_backup_folder(backup_path, backup_folder)
    monitor_steam_folder(config_parser)

if __name__ == "__main__":
    main()