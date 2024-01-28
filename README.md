# Steam Userdata Parser

This Python script is designed to monitor specific folders within the Steam directory, primarily focusing on game folders. It checks for the creation of new folders and performs actions based on the folder's relevance to the configured game IDs.

## Features

- Monitors the Steam directory for new folder creation.
- Checks against a list of specified game IDs.

## Installation

To use this script, follow these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/Tom-Hartmann/CounterStrikeConfigParser
   ```
2. Navigate to the script's directory:
   ```bash
   cd CounterStrikeConfigParser
   ```

## Configuration

Before running the script, you need to set up your `config.ini` file. This file should be structured as follows:

```ini
[DEFAULT]
path = "Adjust the path to your steam userdata folder // usually on "C""
userfolder = "Your Steam user folder id3"
game_ids = "game_id1,game_id2,game_id3"
```

- `path`: Your Steam userdata directory path.
- `userfolder`: The name of your user folder within the Steam directory.
- `game_ids`: A comma-separated list of game IDs you want to copy.

## Usage

Run the script with:

```bash
python CounterStrikeConfigParser.py
```

The script will monitor the Steam folder as per your `config.ini` settings.

## Dependencies

- Python 3
- `watchdog`
- `configparser`

Install the required library using pip:

```bash
pip install requirements.txt
```

## Contributing

Contributions are welcome. Please fork this repository and submit a pull request for any enhancements.

## Acknowledgments

- Thanks to ChatGPT for assisting in the development and debugging process.
