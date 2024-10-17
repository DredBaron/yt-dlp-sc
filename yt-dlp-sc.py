import os
import sys
import subprocess
import configparser
import shutil
import requests
from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
import re

# Text colors
class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKRED = '\033[91m'
    ERROR = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Define the path to the configuration and queue files
config_file_path = os.path.expanduser("~/.config/yt-dlp-sc/options.conf")
queue_file_path = os.path.expanduser("~/.config/yt-dlp-sc/queue.txt")
config = configparser.ConfigParser()

# Initialize global variables
download_directory = "~"
temp_download_directory = "~"
use_temp_folder = ""
yt_dlp_options = ""
queue = []

# Writes the default settings to the options file if the file is either blank or does not exist
def write_default_options():
    global config_file_path
    default_options = """[yt-dlp]
download_directory=~/Downloads
temp_download_directory=~/yt-dlp-sc/
yt_dlp_options=-f 'bv*[height<=1080][ext=mp4]+ba*[ext=m4a]' -N 2
use_temp_folder=False
suppress_output=True"""
        
    if os.path.exists(config_file_path):
        print(f"{bcolors.ERROR}DEBUG:{bcolors.ENDC} config file exists, not sure of contents.")
        print(f"Populating existing configuration file with default settings.")

    if not os.path.exists(config_file_path):
        print(f"{bcolors.ERROR}DEBUG:{bcolors.ENDC} config file does not exist.")
        os.makedirs(os.path.expanduser("~/.config/yt-dlp-sc/"))
        print(f"{bcolors.OKGREEN}Created ~/.config/yt-dlp-sc/{bcolors.ENDC}")
        print(f"{bcolors.ERROR}Configuration file not found:{bcolors.ENDC} {config_file_path}")
        print(f"Creating configuration file with default settings.")
        with open(config_file_path, 'w') as f:
            f.writelines(default_options)
        return
    
    if not os.access(os.path.expanduser("~/.config/"), os.W_OK) or not os.path.exists(os.path.expanduser("~/.config/")):
        print(f"{bcolors.ERROR}DEBUG:{bcolors.ENDC} ~/.config not writable")
        print(f"{bcolors.ERROR}Error:{bcolors.ENDC} ~/.config either does not exist, or cannot be written to.")
        print(f"{bcolors.OKCYAN}Please run:{bcolors.ENDC} mkdir ~/.config/yt-dlp-sc/ && chown -R $USER:$USER ~/.config/yt-dlp-sc/")
        return
        
        with open(config_file_path, 'w') as f:
            f.writelines(default_options)
        return
    if os.access(os.path.expanduser("~/.config/"), os.W_OK) and os.path.exists(os.path.expanduser("~/.config/")) and os.path.exists(config_file_path):
        return

# Checks if a directory exists and is writable
def is_writable(directory):
    if os.path.isdir(directory) and os.access(directory, os.W_OK):
        return True
    else:
        return False

# Checks if the input file is empty, ignoring whitespace
def is_file_blank(file_path):
    if not os.path.exists(file_path):
        return True
    with open(file_path, 'r') as f:
        content = f.read()
        return not content.strip()

# Checks for the presence of the header "[yt-dlp]" in the options file
def check_header(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.readlines()
    except FileNotFoundError:
        content = []
    if not any(line.strip() == "[yt-dlp]" for line in content):
        return False
    else:
        return True

# Prepends a string to the beginning of a file
def prepend_line_to_file(file_path, line):
    # Read the existing contents of the file
    with open(file_path, 'r') as f:
        content = f.readlines()
    
    # Prepend the new line to the content
    content.insert(0, line + '\n')  # Add a newline at the end of the line

    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.writelines(content)

# Check if the configuration file exists and isn't empty, and loads the user settings if it finds it.
if os.path.exists(config_file_path) and not os.stat(config_file_path).st_size == 0:
    if not check_header(config_file_path):
        prepend_line_to_file(config_file_path, "[yt-dlp]")
    else:
        config.read(config_file_path)
        download_directory = config.get('yt-dlp', 'download_directory')
        temp_download_directory = config.get('yt-dlp', 'temp_download_directory')
        yt_dlp_options = config.get('yt-dlp', 'yt_dlp_options')
        use_temp_folder = config.getboolean('yt-dlp', 'use_temp_folder')
        suppress_output = config.getboolean('yt-dlp', 'suppress_output')

# Check if the configuration file exists but is only blank/whitespace.
elif is_file_blank(config_file_path):
    write_default_options()

# Reads and loads the options from the options file into memory
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

    else:
        print(f"Error: Problem loading OPTIONS.CONF")
        return

# Reads and loads the queue from the queue file into active queue memory
def load_queue():
    global queue
    if os.path.exists(queue_file_path):
        with open(queue_file_path, 'r') as f:
            queue = [line.strip() for line in f if line.strip()]  # Load non-empty lines
    else: # Write an empty queue file
        print(f"{bcolors.ERROR}Queue file not found,{bcolors.ENDC} generating empty queue.")
        with open(queue_file_path, 'w') as f:
            pass

# Saves the updated set_temp_folder to the options file
def set_temp_directory_option(temp_folder_option):
    global use_temp_folder
    if temp_folder_option.lower() == "y":
        use_temp_folder = True
        save_config()
        return True
        print(f"Temporary folder option is {bcolors.OKGREEN}enabled{bcolors.ENDC}.")
    elif temp_folder_option.lower() == "n":
        use_temp_folder = False
        save_config()
        print(f"Temporary folder option is {bcolors.OKRED}disabled{bcolors.ENDC}.")
        return False
    else:
        print(f"Usage: temp <y|n>")

def set_suppress_option(suppress_option):
    global suppress_output
    if suppress_option.lower() == "y":
        suppress_output = True
        save_config()
        print(f"Suppress option is {bcolors.OKGREEN}enabled{bcolors.ENDC}.")
        return True
    elif suppress_option.lower() == "n":
        suppress_output = False
        save_config()
        print(f"Suppress option is {bcolors.OKRED}disabled{bcolors.ENDC}.")
        return False
    else:
        print(f"Usage: supp <y|n>")

# Saves the updated temp_directory_option to the options file
def set_temp_directory(directory):
    global temp_download_directory
    global download_directory
    if directory == download_directory:
        print(f"{bcolors.ERROR}Error: {bcolors.ENDC}Temporary download folder and destination download folder are the same. It is better to disable the temporary folder.")
        return
    if is_writable(directory):
        temp_download_directory = directory
        save_config()
        print(f"Directory set to: {temp_download_directory}")
    elif not is_writable(directory) and os.path.isdir(directory):
        print(f"Specified directory does not have write permission.")
    else:
        print(f"Invalid directory. Please provide a valid path.")
        return

# Saves the updated download_directory to the options file
def set_download_directory(directory):
    global temp_download_directory
    global download_directory
    if directory == temp_download_directory:
        print(f"{bcolors.ERROR}Error: {bcolors.ENDC}Temporary download folder and destination download folder are the same.")
        print(f"It is better to disable the temporary folder.")
        return
    if is_writable(directory):
        download_directory = directory
        save_config()
        print(f"Download directory set to: {download_directory}")
    elif not is_writable(directory) and os.path.isdir(directory):
        print(f"Specified directory does not have write permission.")
    else:
        print(f"Invalid directory. Please provide a valid path.")
        return

# Saves the updated yt_dlp_options to the options file
def set_yt_dlp_options(options):
    global yt_dlp_options
    yt_dlp_options = options
    save_config()
    print(f"yt-dlp options set to: {yt_dlp_options}")

# Saves the updated config to the config file
def save_config():
    with open(config_file_path, 'w') as f:
        f.write(f"[yt-dlp]\n")
        f.write(f"download_directory={download_directory}\n")
        f.write(f"temp_download_directory={temp_download_directory}\n")
        f.write(f"yt_dlp_options={yt_dlp_options}\n")
        f.write(f"use_temp_folder={use_temp_folder}\n")
        f.write(f"suppress_output={suppress_output}\n")

# Save the updated queue to the queue file
def save_queue():
    with open(queue_file_path, 'w') as f:
        for link in queue:
            f.write(link + "\n")

# Clear the download queue and temporary download folder
def clear_queue():
    yt_dlp_folder = os.path.expanduser(temp_download_directory)
    archive_file = os.path.join(yt_dlp_folder, 'downloaded_videos.txt')
    
    # Clear the queue file
    open(queue_file_path, 'w').close()  # Clear the queue file
    print(f"Download queue cleared.")
    
    # Remove temp download folder
    if os.path.exists(yt_dlp_folder):
        for root, dirs, files in os.walk(yt_dlp_folder, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                print(f"Deleting file: {file_path}")
                os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                print(f"Deleting temporary download folder")
                shutil.rmtree(dir_path)
        print(f"All contents in {yt_dlp_folder} cleared.")
    else:
        print(f"{yt_dlp_folder} does not exist.")
    
    # Delete the archive file
    if os.path.exists(archive_file):
        os.remove(archive_file)
        print(f"Archive file {archive_file} deleted.")

# Prints the help menu
def show_help():
    help_text = """  Commands:
    - add <link>      : Add a link to the download queue.
    - show            : Show the current download queue and settings.
    - remove <index>  : Remove a link from the queue by index.
    - setdir <path>   : Set the download directory.
    - setdelay <min>  : Set the retry delay in minutes. *FEATURE HAS BEEN DISABLED*, see release 1.3.0 for notes.
    - options "opts"  : Set yt-dlp options.
    - start           : Start the download session.
    - clear           : Clears the download queue manually.
    - temp <y|n>      : Enables or disables the temporary download folder option.
    - settemp <path>  : Sets the temporary download directory.
    - supp <y|n>      : Enables or disables the yt-dlp output suppression, showing only the progress bar
    - help            : Show this help message.
    """
    # Clears the terminal
    #print(f"\033c")
    print(help_text)

# Adds input link to the queue
def add_to_queue(link):
    global queue
    queue.append(link)
    save_queue()
    print(f"Added to queue: {link}")

    if not queue:
        print(f"Current download queue is empty.")
        return
    print(f"Current download queue:")
    for index, link in enumerate(queue):
        print(f"{index}: {link}")

# Removes link at input index from queue
def remove_from_queue(index):
    if 0 <= index < len(queue):
        removed = queue.pop(index)
        save_queue()
        print(f"Removed from queue: {removed}")
    else:
        print(f"Index out of range.")

# Ping a URL, and remove from queue if no answer
def check_ping(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        elif response.status_code != 200:
            raise Exception(f"{bcolors.ERROR}Error:{bcolors.ENDC} {response.status_code}")
    except (requests.ConnectionError, requests.Timeout) as e:
        print(f"URL {url} is not responding.")
        queue.pop(0)
        save_queue()
        return False
    except Exception as e:
        print(f"Error with {url}: {e}.")
        return False

def contains_substring(main_string, substring):
    
    return substring in main_string

def extract_download_details(line):
    # Extract the fragment number, total fragments, ETA, download speed, and total size
    fragment_match = re.search(r"\(frag (\d+)/(\d+)\)", line)
    eta_match = re.search(r"ETA (\d{2}:\d{2})", line)
    speed_match = re.search(r"at\s+([~\d.]+[A-Za-z]+/s)", line)
    size_match = re.search(r"of ~\s+([~\d.]+[A-Za-z]+)", line)

    # Extract fragments, ETA, download speed, and total size if available
    current_fragment = fragment_match.group(1) if fragment_match else "?"
    total_fragment = fragment_match.group(2) if fragment_match else "?"
    eta = eta_match.group(1) if eta_match else "N/A"
    speed = speed_match.group(1) if speed_match else "N/A"
    total_size = size_match.group(1) if size_match else "N/A"

    return current_fragment, total_fragment, eta, speed, total_size

def format_download_status(line):
    # Extract the relevant information from the line
    current_fragment, total_fragment, eta, speed, total_size = extract_download_details(line)

    # Format the output line
    formatted_line = f"Downloading fragment {current_fragment}/{total_fragment} | ETA: {eta} at ~ {speed} | Total size ~ {total_size}"

    return formatted_line

# Starts the downloading of each link in queue, sequentially.
def download_queue():
    global download_archive
    global temp_download_directory
    global suppress_output
    global queue

    # Check if temporary folder option is enabled
    if use_temp_folder:
        current_download_directory = os.path.expanduser(temp_download_directory)
        print(f"Temporary folder is {bcolors.OKGREEN}enabled{bcolors.ENDC}.")
        print(f"Downloading to temporary folder: {current_download_directory}\n")
    else:
        # Use final directory if temp folder is not enabled
        current_download_directory = os.path.expanduser(download_directory)
        print(f"Temporary folder is {bcolors.OKRED}disabled{bcolors.ENDC}.")
        print(f"Downloading directly to final directory: {current_download_directory}\n")
    
    # Check if the suppress option is enabled
    if suppress_output:
        print(f"Suppression is {bcolors.OKGREEN}enabled{bcolors.ENDC}.\n")
    else:
        print(f"Suppression is {bcolors.OKRED}disabled{bcolors.ENDC}.\n")

    while queue:
        # Get the first link from the queue
        link = queue[0]
              
        print(f"{bcolors.OKGREEN}Checking Queue URL:{bcolors.ENDC} {link}")
        if "www.youtube.com/" not in link:
            print(f"URL is not from Youtube, removing from queue.\n")
            queue.pop(0)
            save_queue()
        else:
            print(f"{bcolors.OKCYAN}URL looks like it belongs to Youtube.{bcolors.ENDC}\n")
            print(f"{bcolors.OKCYAN}Checking responsiveness{bcolors.ENDC}\n")
        
        if not check_ping(link):
            print(f"{bcolors.ERROR}Removing URL:{bcolors.ENDC} {link}\n")
            queue.pop(0)
            save_queue()
            continue

        print(f"{bcolors.OKGREEN}URL is responsive. Proceeding with download{bcolors.ENDC}\n")            

        if use_temp_folder:
            download_archive = os.path.expanduser("~/yt-dlp-sc/downloaded_videos.txt")
            command = ["yt-dlp", "--download-archive", download_archive] + yt_dlp_options.split() + [link]
            print(f"{bcolors.OKCYAN}Command (pretty):{bcolors.ENDC} {" ".join(command)}\n")
            print(f"{bcolors.OKCYAN}Command (raw):{bcolors.ENDC} {command}\n")
        elif not use_temp_folder:
            command = ["yt-dlp"] + yt_dlp_options.split() + [link]
            download_archive = os.path.expanduser("~/yt-dlp-sc/downloaded_videos.txt")
            print(f"{bcolors.OKCYAN}Command (pretty):{bcolors.ENDC} {" ".join(command)}\n")
            print(f"{bcolors.OKCYAN}Command (raw):{bcolors.ENDC} {command}\n")
            
        if suppress_output:
            initial_panel = Panel("Starting Download...", border_style="green")
            with Live(initial_panel, refresh_per_second = 1) as live:
                try:
                    process = subprocess.Popen(
                        command,
                        cwd=os.path.expanduser(current_download_directory),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )

                    panel = Panel("Downloading...", border_style="green")
                    live.update(initial_panel)
                    
                    # Process yt-dlp output in real-time
                    for line in process.stdout:
                        if "[download]" in line and "%" in line and "ETA" in line:
                            formatted_line = format_download_status(line)
                            panel = Panel(formatted_line, title="Download Progress", border_style="green")
                            live.update(panel)
                        if "[Merger]" in line and "Merging" in line:
                            formatted_line = f"Merging files into final file"
                            panel = Panel(formatted_line, title="Merging Progress", border_style="blue")
                            live.update(panel)

                    print(f"{bcolors.OKGREEN}Finished downloading:{bcolors.ENDC} {link}\n")
                    queue.pop(0)
                    save_queue()

                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode().strip()
                    print(f"{bcolors.ERROR}Error occurred while downloading: {stderr_output}{bcolors.ENDC}")
                    break
                
                

        elif not suppress_output:
            try:
                subprocess.run(command, check=True, cwd=os.path.expanduser(current_download_directory), stderr=subprocess.PIPE)
                print(f"{bcolors.OKGREEN}Finished downloading:{bcolors.ENDC} {link}\n")
                queue.pop(0)
                save_queue()
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr.decode().strip()
                print(f"{bcolors.ERROR}Error occurred while downloading: {stderr_output}{bcolors.ENDC}")
                break        

    # Move files from temp folder to final directory if temp folder was used
    if use_temp_folder:
        move_files_to_final_directory(download_directory)

# Moves all files in the temporary download directory to the proper download folder.
def move_files_to_final_directory(temp_dir):
    downloaded_files = os.listdir(temp_dir)
    if not downloaded_files:
        print(f"No files found in {temp_dir} after download.")
        return
    # Move each file to the proper download directory
    for filename in downloaded_files:
        if filename == "downloaded_videos.txt":
            global download_directory
            os.remove(os.path.join(temp_dir, filename))
            continue
        temp_file_path = os.path.join(temp_dir, filename)
        final_file_path = os.path.join(config.get('yt-dlp', 'download_directory'), filename)
        print(f"Moving {temp_file_path} to {final_file_path}")
        shutil.move(temp_file_path, final_file_path)
    clear_queue()
    print(f"All downloaded files have been moved to the final directory.")

# Prints the current settings and links in queue
def show_settings():

    # Clears the terminal
    #print(f"\033c")

    # Print ASCII Art Header
    art = """┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        _                  _ _                                   __    ____    _____  ┃
┃       | |                | | |                                 /_ |  |__  \\  | ____| ┃
┃  _   _| |_   ______    __| | |_ __    ______   ___  ___   __   _| |   __)  | | |__   ┃
┃ | | | | __| |______|  / _` | | '_ \\  |______| / __|/ __|  \\ \\ / | |  |__  <  |__  \\  ┃
┃ | |_| | |_           | (_| | | |_) |          \\__ | (__    \\ V /| |   __)  |  ___) | ┃
┃  \\__, |\\__|           \\__,_|_| .__/           |___/\\___|    \\_/ |_|()|____/()|____/  ┃
┃   __/ |                      | |                                                     ┃
┃  |___/                       |_|                                                     ┃
┃                                                By: DredBaron 🯆                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(art)

    if download_directory == "~" and temp_download_directory == "~":
        write_default_options()
        print(f"  {bcolors.ERROR}Note:{bcolors.ENDC} Looks like the options file had to be generated. Please re-run the last command.\n")
        return
    else:
        print(f"  {bcolors.BOLD}{bcolors.OKGREEN}Current settings:\n{bcolors.ENDC}")
        print(f"  {bcolors.UNDERLINE}Download directory is:{bcolors.ENDC}")
        print(f"  {bcolors.OKBLUE}{download_directory}\n{bcolors.ENDC}")
        print(f"  {bcolors.UNDERLINE}Temporary download folder is:{bcolors.ENDC}")
        if use_temp_folder:
            print(f"  {bcolors.OKBLUE}{temp_download_directory}\n{bcolors.ENDC}")
        elif not use_temp_folder:
            print(f"  {bcolors.ERROR}Disabled\n{bcolors.ENDC}")
        else:
            print(f"  {bcolors.ERROR}Temporary download folder is not set.\n{bcolors.ENDC}")
        print(f"  {bcolors.UNDERLINE}yt-dlp options are:{bcolors.ENDC}")
        print(f"  {bcolors.OKBLUE}{yt_dlp_options}\n{bcolors.ENDC}")
        print(f"  {bcolors.OKBLUE}{bcolors.BOLD}{bcolors.OKGREEN}Current download queue:{bcolors.ENDC}")
        if not is_file_blank(queue_file_path):
            for index, link in enumerate(queue):
                print(f"  {bcolors.OKCYAN}{index} - {link}{bcolors.ENDC}")
            print(f"")
        else:
            print(f"  Nothing in queue\n")

# Main loop, handles command options
def main():
    load_queue()

    if len(sys.argv) < 2:
        show_settings()
        return
    command = sys.argv[1]
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_queue()
        return
    elif command == 'add':
        if len(sys.argv) < 3:
            print(f"Please provide a link to add.")
            return
        add_to_queue(sys.argv[2])
    elif command == 'show':
        show_settings()
    elif command == 'remove':
        if len(sys.argv) < 3:
            print(f"Please provide the index to remove.")
            return
        try:
            index = int(sys.argv[2])
            remove_from_queue(index)
        except ValueError:
            print(f"Invalid index")
    elif command == 'setdir':
        if len(sys.argv) < 3:
            print(f"Please provide a directory.")
            return
        set_download_directory(sys.argv[2])
    elif command == 'settemp':
        if len(sys.argv) < 3:
            print(f"Please provide a directory.")
            return
        set_temp_directory(sys.argv[2])
    elif command == 'supp':
        if len(sys.argv) > 1 and sys.argv[1] == "supp":
            if len(sys.argv) == 3:
                set_suppress_option(sys.argv[2])
            else:
                print(f"Usage: supp <y|n>")
    elif command == 'setdelay':
        if len(sys.argv) < 3:
            print(f"{bcolors.ERROR}This option is currently a W.I.P. Will not do anything.{bcolors.ENDC}")
            return
    elif command == 'options':
        if len(sys.argv) < 3:
            print(f"Please provide yt-dlp compatable options.")
            return
        set_yt_dlp_options(" ".join(sys.argv[2:]))
    elif command == 'start':
        if not queue:
            print(f"The queue is empty. Please add links before starting the download.")
            return
        download_queue()
    elif command == 'temp':
        if len(sys.argv) > 1 and sys.argv[1] == "temp":
            if len(sys.argv) == 3:
                set_temp_directory_option(sys.argv[2])
            else:
                print(f"Usage: temp <y|n>")
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()
