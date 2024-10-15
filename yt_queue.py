import os
import sys
import time
import subprocess
import configparser

# Define the path to the configuration file and the queue file
config_file_path = os.path.expanduser('~/.config/yt-dlp-sc/options.conf')
queue_file_path = os.path.expanduser('~/.config/yt-dlp-sc/queue.txt')

def ensure_header():
    """Ensure that the configuration file starts with a section header [yt-dlp]."""
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as f:
            f.write("[yt-dlp]\n")
            f.write("download_directory=/home/$USER/Downloads\n")
            f.write("options=-f bv*[height<=1080][ext=mp4]+ba*[ext=m4a] -N 2\n")
    else:
        with open(config_file_path, 'r+') as f:
            lines = f.readlines()
            if not lines or not lines[0].startswith("["):
                # Insert header if the first line doesn't start with [
                f.seek(0, 0)
                f.write("[yt-dlp]\n" + "".join(lines))

# Check if the configuration file exists
if not os.path.exists(config_file_path):
    print(f"Configuration file not found: {config_file_path}")
    print(f"Using default configuration")
    ensure_header()

# Initialize ConfigParser and read the config
config = configparser.ConfigParser()
config.read(config_file_path)

# Get options and download directory
download_directory = config.get('yt-dlp', 'download_directory')
options = config.get('yt-dlp', 'yt_dlp_options')

# Initialize global variables
download_directory = os.getcwd()  # Default to current working directory
yt_dlp_options = ""  # Default yt-dlp options
retry_delay = 15  # Default retry delay in minutes
queue = []  # In-memory download queue

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
    - options "opts"  : Set yt-dlp options.
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
        ensure_header()
    else:
        print("Invalid directory. Please provide a valid path.")

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
    ensure_header()

def set_yt_dlp_options(options):
    global yt_dlp_options
    yt_dlp_options = options  # Store the full string as is
    save_config()  # Save the new options to the config file
    print(f"yt-dlp options set to: {yt_dlp_options}")
    ensure_header()

def download_queue():
    global queue
    while queue:
        link = queue[0]  # Get the first link from the queue (don't remove it yet)
        print(f"Starting download to {download_directory}")
        print(f"yt-dlp options set to: {yt_dlp_options}")
        command = ["yt-dlp"] + yt_dlp_options.split() + [link]  # Build command with options
        retry_count = 0  # Reset retry count for each link
        
        while retry_count < 3:  # Set a max retry limit
            try:
                result = subprocess.run(command, check=True, cwd=download_directory, stderr=subprocess.PIPE)
                print(f"Finished downloading: {link}")
                queue.pop(0)  # Remove the successfully downloaded link from the queue
                save_queue()  # Save updated queue
                break  # Exit retry loop if download succeeds
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr.decode().strip()
                
                if "Sign in to confirm you’re not a bot" in stderr_output:
                    print(f"Error: '{stderr_output}'. Pausing for {retry_delay} minutes.")
                    time.sleep(retry_delay * 60)  # Pause for the set retry delay
                    retry_count += 1  # Increment the retry count but keep the same link in the queue
                else:
                    print(f"Error downloading {link}: {stderr_output}. Retrying...")
                    time.sleep(retry_delay * 60)  # Pause before retrying other errors as well
                    retry_count += 1

        if retry_count == 3:
            print(f"Failed to download {link} after 3 attempts. Moving to next link.")
            queue.pop(0)  # Remove the link after max retries
            save_queue()  # Save updated queue

def main():
    load_config()  # Load configuration
    load_queue()  # Load the queue

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
        set_yt_dlp_options(" ".join(sys.argv[2:]))
    elif command == 'start':
        if not queue:
            print("The queue is empty. Please add links before starting the download.")
            return
        download_queue()
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()
