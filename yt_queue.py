import os
import sys
import time
import subprocess
import configparser
import shutil

# Define the path to the configuration file and the queue file
config_file_path = os.path.expanduser('~/.config/yt-dlp-sc/options.conf')
queue_file_path = os.path.expanduser('~/.config/yt-dlp-sc/queue.txt')
use_temp_folder = "n"

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

def set_temp_folder_option(temp_option):
    options_file = os.path.expanduser("~/.config/yt-dlp-sc/options.conf")
    global use_temp_folder
    if temp_option.lower() == "y":
        use_temp_folder = "y"
    elif temp_option.lower() == "n":
        use_temp_folder = "n"
    else:
        print("Invalid option for temp. Use 'y' or 'n'.")
        return
    
    # Load existing options, modify or add the temp folder option
    if os.path.exists(options_file):
        with open(options_file, "r") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Find and update the 'use_temp_folder' setting
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("use_temp_folder"):
            lines[i] = f"use_temp_folder={use_temp_folder}\n"
            updated = True
            ensure_header()
            break
    
    # If 'use_temp_folder' setting wasn't found, add it
    if not updated:
        lines.append(f"use_temp_folder={use_temp_folder}\n")
        ensure_header()
    
    # Save back to the options file
    with open(options_file, "w") as f:
        f.writelines(lines)
        ensure_header()
    
    print(f"Temporary folder option set to {use_temp_folder}")

# Command handler for temp
if len(sys.argv) > 1 and sys.argv[1] == "temp":
    if len(sys.argv) == 3:
        set_temp_folder_option(sys.argv[2])
    else:
        print("Usage: python yt_queue.py temp <y|n>")

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

def load_options():
    options_file = os.path.expanduser("~/.config/yt-dlp-sc/options.conf")
    options = {}

    if os.path.exists(options_file):
        with open(options_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    options[key] = value
    return options

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
    yt_dlp_folder = os.path.expanduser('~/yt-dlp-sc/')
    temp_folder = os.path.join(yt_dlp_folder, 'temp/')
    archive_file = os.path.join(yt_dlp_folder, 'downloaded_videos.txt')
    
    # Clear the queue file
    open(queue_file_path, 'w').close()  # Clear the queue file
    print("Download queue cleared.")
    
    # Remove all files in the yt-dlp-sc folder
    if os.path.exists(yt_dlp_folder):
        for root, dirs, files in os.walk(yt_dlp_folder, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                print(f"Deleting file: {file_path}")
                os.remove(file_path)  # Delete each file
            for name in dirs:
                dir_path = os.path.join(root, name)
                print(f"Deleting directory: {dir_path}")
                shutil.rmtree(dir_path)  # Delete each directory
        print(f"All contents in {yt_dlp_folder} deleted.")
    else:
        print(f"{yt_dlp_folder} does not exist.")
    
    # Ensure the yt-dlp-sc folder itself is empty
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)  # Delete temp folder
        print(f"Temporary folder {temp_folder} deleted.")
    
    # Delete the archive file
    if os.path.exists(archive_file):
        os.remove(archive_file)  # Delete archive file
        print(f"Archive file {archive_file} deleted.")

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
    - temp <y|n>      : Enables or disables the temporary download folder option.
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
    options = load_options()  # Load the latest configuration options
    use_temp_folder = options.get("use_temp_folder", "n").lower() == "y"  # Check if temp folder is enabled

    # Define the temporary directory if temp folder option is enabled
    if use_temp_folder == "y":
        temp_dir = os.path.expanduser("~/yt-dlp-sc/temp/")  # Temporary folder path
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)  # Create temp folder if it doesn't exist
        download_dir = temp_dir  # Set download directory to the temp folder
        print(f"Downloading to temporary folder: {temp_dir}")
    else:
        download_dir = download_directory  # Use final directory if temp folder is not enabled
        print(f"Downloading directly to final directory: {download_dir}")

    # The archive file to track completed downloads
    download_archive = os.path.expanduser("~/yt-dlp-sc/downloaded_videos.txt")

    while queue:
        link = queue[0]  # Get the first link from the queue
        print(f"Starting download to: {download_dir}")
        print(f"yt-dlp options set to: {yt_dlp_options}")

        # Build the yt-dlp command with the archive and options
        command = ["yt-dlp", "--download-archive", download_archive] + yt_dlp_options.split() + [link]
        retry_count = 0  # Reset retry count for each link

        while retry_count < 3:  # Retry up to 3 times
            try:
                result = subprocess.run(command, check=True, cwd=download_dir, stderr=subprocess.PIPE)
                print(f"Finished downloading: {link}")

                queue.pop(0)  # Remove successfully downloaded link from the queue
                save_queue()  # Save updated queue
                break  # Exit retry loop on success
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr.decode().strip()
                
                if "Sign in to confirm you’re not a bot" in stderr_output:
                    print(f"Error: '{stderr_output}'. Pausing for {retry_delay} minutes.")
                    time.sleep(retry_delay * 60)  # Pause before retry
                    retry_count += 1
                else:
                    print(f"Error downloading {link}: {stderr_output}. Retrying...")
                    time.sleep(retry_delay * 60)
                    retry_count += 1

        if retry_count == 3:
            print(f"Failed to download {link} after 3 attempts. Skipping...")
            queue.pop(0)  # Remove after max retries
            save_queue()

    # Move files from temp folder to final directory if temp folder was used
    if use_temp_folder == "y":
        move_files_to_final_directory(temp_dir)

def move_files_to_final_directory(temp_dir):
    downloaded_files = os.listdir(temp_dir)  # List files in the temp folder
    if not downloaded_files:
        print(f"No files found in {temp_dir} after download.")
        return

    # Move each file to the final download directory
    for filename in downloaded_files:
        temp_file_path = os.path.join(temp_dir, filename)
        final_file_path = os.path.join(download_directory, filename)
        print(f"Moving {temp_file_path} to {final_file_path}")
        shutil.move(temp_file_path, final_file_path)

    print("All downloaded files have been moved to the final directory.")

def move_files_to_final_directory(temp_dir):
    # List all downloaded files in the temporary directory
    downloaded_files = os.listdir(temp_dir)
    if not downloaded_files:
        print(f"Error: No files found in {temp_dir} after download.")
        return

    # Move each downloaded file to the actual download directory
    for filename in downloaded_files:
        temp_file_path = os.path.join(temp_dir, filename)
        final_file_path = os.path.join(download_directory, filename)
        print(f"Moving {temp_file_path} to {final_file_path}")
        shutil.move(temp_file_path, final_file_path)

    print("All downloaded files have been moved to the final directory.")

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
    elif command == 'temp':
        if len(sys.argv) > 1 and sys.argv[1] == "temp":
            if len(sys.argv) == 3:
                set_temp_folder_option(sys.argv[2])
            else:
                print("Usage: python yt_queue.py temp <y|n>")
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()
