import os
import sys
import time
import subprocess
import configparser

# Define the path to the configuration file and the queue file
config_file_path = os.path.expanduser('~/.config/yt-dlp-sc/options.conf')
queue_file_path = os.path.expanduser('~/.config/yt-dlp-sc/queue.txt')

# Check if the configuration file exists
if not os.path.exists(config_file_path):
    print(f"Configuration file not found: {config_file_path}")
    # Create the file with default values and section headers
    with open(config_file_path, 'w') as f:
        f.write("[yt-dlp]\n")
        f.write("download_directory=/home/$USER/Downloads\n")
        f.write("options=-f bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a] -N 8\n")

# Initialize ConfigParser and read the config
config = configparser.ConfigParser()
config.read(config_file_path)

# Get options and download directory
download_directory = config.get('yt-dlp', 'download_directory', fallback='/home/$USER/Downloads/')
options = config.get('yt-dlp', 'options', fallback='-f bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a] -N 2')

# Initialize global variables
download_directory = os.getcwd()  # Default to current working directory
yt_dlp_options = ""  # Default yt-dlp options
retry_delay = 15  # Default retry delay in minutes
queue = []  # In-memory download queue

def ensure_header():
    """Ensure that the configuration file starts with a header."""
    with open(config_file_path, 'r') as f:
        lines = f.readlines()

    # Check if there are any lines in the file
    if len(lines) == 0 or not lines[0].startswith('['):
        # If the file is empty or the first line doesn't start with '[', add the header
        lines.insert(0, "[yt-dlp]\n")

        # Write back to the config file
        with open(config_file_path, 'w') as f:
            f.writelines(lines)

def load_config():
    global download_directory, yt_dlp_options, retry_delay
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            for line in f:
                if line.startswith('download_directory='):
                    download_directory = line.strip().split('=', 1)[1]
                elif line.startswith('yt_dlp_options='):
                    yt_dlp_options = line.strip().split('=', 1)[1]
                elif line.startswith('retry_delay='):
                    retry_delay = int(line.strip().split('=', 1)[1])
    else:
        print("Config file not found, using default values.")

def save_config():
    with open(config_file_path, 'w') as f:
        f.write(f"download_directory={download_directory}\n")
        f.write(f"yt_dlp_options={yt_dlp_options}\n")
        f.write(f"retry_delay={retry_delay}\n")
        ensure_header()  # Ensure the header is present

def load_queue():
    global queue
    if os.path.exists(queue_file_path):
        with open(queue_file_path, 'r') as f:
            queue = [line.strip() for line in f if line.strip()]  # Load non-empty lines
    else:
        print("Queue file not found, starting with an empty queue.")

def save_queue():
    with open(queue_file_path, 'w') as f:
        for link in queue:
            f.write(link + "\n")  # Write each link on a new line

# Clear the download queue
def clear_queue():
    open(queue_file_path, 'w').close()  # Clear the file
    print("Download queue cleared.")

def show_help():
    help_text = """
    Commands:
    - add <link>      : Add a link to the download queue.
    - show            : Show the current download queue and settings.
    - remove <index>  : Remove a link from the queue by index.
    - setdir <path>   : Set the download directory.
    - setdelay <min>  : Set the retry delay in minutes.
    - options <opts>  : Set yt-dlp options.
    - start           : Start the download session.
    - clear           : Clears the download queue manually.
    - help            : Show this help message.
    """
    print(help_text)

def add_to_queue(link):
    global queue  # Ensure we're using the global queue
    queue.append(link)
    save_queue()  # Save the updated queue to the file
    print(f"Added to queue: {link}")

def show_queue():
    print(f"Current settings:")
    print(f"Download directory is set to: {download_directory}")
    print(f"Delay is set to: {retry_delay} minutes")
    print(f"yt-dlp options are set to: {yt_dlp_options}")

    if not queue:
        print("Current download queue is empty.")
        return
    print("Current download queue:")
    for index, link in enumerate(queue):
        print(f"{index}: {link}")

def remove_from_queue(index):
    if 0 <= index < len(queue):
        removed = queue.pop(index)
        save_queue()  # Save the updated queue to the file
        print(f"Removed from queue: {removed}")
    else:
        print("Index out of range.")

def set_download_directory(directory):
    global download_directory
    if os.path.isdir(directory):
        download_directory = directory
        save_config()  # Save the new directory to the config file
        print(f"Download directory set to: {download_directory}")
    else:
        print("Invalid directory. Please provide a valid path.")
    ensure_header()  # Ensure the header is present

def set_retry_delay(delay_str):
    global retry_delay
    try:
        delay = int(delay_str)
        if delay < 0:
            print("Delay cannot be negative.")
            return
        retry_delay = delay
        save_config()  # Save the new delay to the config file
        print(f"Retry delay set to {retry_delay} minutes.")
    except ValueError:
        print("Invalid delay value. Please provide a number.")
    ensure_header()  # Ensure the header is present

def set_yt_dlp_options(options):
    global yt_dlp_options
    yt_dlp_options = options  # Store the full string as is
    save_config()  # Save the new options to the config file
    print(f"yt-dlp options set to: {yt_dlp_options}")
    ensure_header()  # Ensure the header is present

def download_queue():
    global queue
    while queue:
        link = queue.pop(0)  # Get the first link from the queue
        print(f"Starting download: {link} to {download_directory} with yt-dlp options set to: {yt_dlp_options}")
        command = ["yt-dlp"] + yt_dlp_options.split() + [link]  # Build command with options
        try:
            subprocess.run(command, check=True, cwd=download_directory)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {link}: {e}. Retrying in {retry_delay} minutes.")
            queue.append(link)  # Re-add to queue for retry
            save_queue()  # Save updated queue
            time.sleep(retry_delay * 60)  # Delay before retrying
        print(f"Finished downloading: {link}")

def main():
    load_config()  # Load configuration at the start
    load_queue()  # Load the queue at the start

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_queue()
        return
    elif command == 'add':
        if len(sys.argv) < 3:
            print("Please provide a link to add.")
            return
        add_to_queue(sys.argv[2])
    elif command == 'show':
        show_queue()
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Please provide the index to remove.")
            return
        try:
            index = int(sys.argv[2])
            remove_from_queue(index)
        except ValueError:
            print("Invalid index")
    elif command == 'setdir':
        if len(sys.argv) < 3:
            print("Please provide a directory to set.")
            return
        set_download_directory(sys.argv[2])
    elif command == 'setdelay':
        if len(sys.argv) < 3:
            print("Please provide a delay time in minutes.")
            return
        set_retry_delay(sys.argv[2])
    elif command == 'options':
        if len(sys.argv) < 3:
            print("Please provide yt-dlp options to set.")
            return
        set_yt_dlp_options(" ".join(sys.argv[2:]))  # Pass the full options string
    elif command == 'start':
        if not queue:
            print("The queue is empty. Please add links before starting the download.")
            return
        print(f"Starting download session...")
        download_queue()  # Call the download function directly
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()
