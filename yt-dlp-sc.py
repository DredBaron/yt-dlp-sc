#!/usr/bin/env python3

from rich.live import Live
from rich.panel import Panel
import os
import sys
import subprocess
import configparser
import shutil
import requests
import re

# Text colors
class bcolors:
    COMPLETED = '\033[92m'
    OKBLUE = '\033[94m'
    OKRED = '\033[91m'
    OKSTATUS = '\033[96m'
    ERROR = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

# Define the path to the configuration and queue files
config_file_path = os.path.expanduser("~/.config/yt-dlp-sc/options.conf")
queue_file_path = os.path.expanduser("~/.config/yt-dlp-sc/queue.txt")
config = configparser.ConfigParser()

# Initialize global variables
yt_dlp_sc_version = "2.1.0"
download_directory = "~"
temp_download_directory = "~"
use_temp_folder = ""
yt_dlp_options = ""
suppress_output = ""
debug = "True"
pretty = ""
queue = []
default_options = """[yt-dlp]
download_directory=~/Downloads
temp_download_directory=~/Downloads/yt-dlp-sc
yt_dlp_options=-f bv*[height<=1080][ext=mp4]+ba*[ext=m4a] -N 2
use_temp_folder=False
suppress_output=True
debug=False
pretty=True"""

def create_yt_dlp_sc_folder():
    if os.access(os.path.expanduser("~/.config"), os.W_OK) and not os.path.isdir(os.path.expanduser("~/.config/yt-dlp-sc/")):
        os.makedirs(os.path.expanduser("~/.config/yt-dlp-sc/"))
        print(f"Created ~/.config/yt-dlp-sc/")
        return
    elif os.path.isdir(os.path.expanduser("~/.config/yt-dlp-sc/")):
        print(f"~/.config/yt-dlp-sc already exists, skipping.")
        return
    elif os.path.exists(os.path.expanduser("~/.config")) and not os.access(os.path.expanduser("~/.config"), os.W_OK):
        print(f"Directory ~/.config/ is not writable, please allow write permissions, then try running this program again.")
        return

def create_config():
    global default_options
    print(f"Creating configuration file with default settings.")
    with open(config_file_path, 'w') as f:
        f.writelines(default_options)
    return

# Returns whether the file is the same as the default settings
def is_same_as_default(compare):
    compare_content = open(compare, 'r')

    file1_lines = compare_content.readlines()
    file2_lines = default_options

    for i in range(len(file1_lines)):
        if file1_lines[i] != file2_lines[i]:
            compare_content.close()
            return False
        
        elif file1_lines[i] == file2_lines[i]:
            compare_content.close()
            return True
        else:
            print(f"{bcolors.ERROR}DEBUG Error 30:{bcolors.ENDC} Option file and internal default settings could not be compared.")

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

# Writes the default settings to the options file if the file is either blank or does not exist
def write_default_options():
    global config_file_path

    # Config file exists. Throw 'Already Exists' error
    if os.path.exists(config_file_path) and not is_same_as_default(config_file_path):
        if debug:
            print(f"{bcolors.ERROR}DEBUG Error 01:{bcolors.ENDC} config file exists, contents don't seem to be right.")
        print(f"Populating existing configuration file with default settings. Returning")
        create_config()

    # ~/.config/yt-dlp-sc/ exists, but there is no config file. Throwing 'Does Not Exist' error and creatign default config file
    elif not os.path.exists(config_file_path) and os.access(os.path.expanduser("~/.config/yt-dlp-sc/"), os.W_OK):
        if debug:
            print(f"{bcolors.ERROR}DEBUG Error 02:{bcolors.ENDC} config file does not exist.")
        print(f"{bcolors.ERROR}Configuration file not found:{bcolors.ENDC} {config_file_path}")
        create_config()

    # ~/.config/yt-dlp-sc does not exist. Throwing 'Does Not Exist' error and creating directory and config folder inside.
    elif not os.path.exists(os.path.expanduser("~/.config/yt-dlp-sc/")):
        if debug:
            print(f"{bcolors.ERROR}DEBUG Error 03:{bcolors.ENDC} ~/.config/yt-dlp-sc does not exist. Attempting to create and populate.")        
        create_yt_dlp_sc_folder()
        create_config()

    # ~/.config is either unwritable or does not exist. Throwing 'Does Not Exist' error and advising the user.
    elif not os.access(os.path.expanduser("~/.config/"), os.W_OK):
        print(f"{bcolors.ERROR}Error:{bcolors.ENDC} ~/.config either does not exist, or cannot be written to.")
        return
    
    # Load options into memory
    load_options()

# Reads and loads the options from the options file into memory
def load_options():
    global download_directory
    global temp_download_directory
    global yt_dlp_options
    global use_temp_folder
    global suppress_output
    global debug
    global pretty

    # Checks if the config_file_path exists, and if it is not empty
    if os.path.exists(config_file_path) and not os.stat(config_file_path).st_size == 0:
        if not check_header(config_file_path):
            prepend_line_to_file(config_file_path, "[yt-dlp]")
        else:
            config.read(config_file_path)
            download_directory = os.path.expanduser(config.get('yt-dlp', 'download_directory'))
            temp_download_directory = os.path.expanduser(config.get('yt-dlp', 'temp_download_directory'))
            yt_dlp_options = config.get('yt-dlp', 'yt_dlp_options')
            use_temp_folder = config.getboolean('yt-dlp', 'use_temp_folder')
            suppress_output = config.getboolean('yt-dlp', 'suppress_output')
            debug = config.getboolean('yt-dlp', 'debug')
            pretty = config.getboolean('yt-dlp', 'pretty')

    # Check if the options file is already loaded with defaults.
    if is_same_as_default(config_file_path):
        print(is_same_as_default(config_file_path))
        config.read(config_file_path)
        download_directory = os.path.expanduser(config.get('yt-dlp', 'download_directory'))
        temp_download_directory = os.path.expanduser(config.get('yt-dlp', 'temp_download_directory'))
        yt_dlp_options = config.get('yt-dlp', 'yt_dlp_options')
        use_temp_folder = config.getboolean('yt-dlp', 'use_temp_folder')
        suppress_output = config.getboolean('yt-dlp', 'suppress_output')
        debug = config.getboolean('yt-dlp', 'debug')
        pretty = config.getboolean('yt-dlp', 'pretty')

    # Check if the configuration file exists but is only blank/whitespace. Writes defaults if it is.
    elif is_file_blank(config_file_path):
        write_default_options()

# Reads and loads the queue from the queue file into active queue memory
def load_queue():
    global queue
    if os.path.exists(queue_file_path):
        with open(queue_file_path, 'r') as f:
            queue = [line.strip() for line in f if line.strip()]
    elif not os.path.exists(queue_file_path):
        print(f"{bcolors.ERROR}Queue file not found,{bcolors.ENDC} generating empty queue.")
        with open(queue_file_path, 'w') as f:
            pass
    else:
        if debug:
            print(f"{bcolors.ERROR}DEBUG Error 10:{bcolors.ENDC} Error determining queue file status.")

# Saves the updated set_temp_folder to the options file
def set_temp_directory_option(temp_folder_option):
    global use_temp_folder
    if temp_folder_option.lower() == "y" or temp_folder_option.lower() == "yes":
        use_temp_folder = True
        save_config()
        print(f"Temporary folder option is now {bcolors.COMPLETED}enabled{bcolors.ENDC}.")
        return True
    elif temp_folder_option.lower() == "n" or temp_folder_option.lower() == "no":
        use_temp_folder = False
        save_config()
        print(f"Temporary folder option is now {bcolors.OKRED}disabled{bcolors.ENDC}.")
        return False
    else:
        print(f"Usage: -t/--temp <directory>")

# Saves the debug option to the options file
def set_debug(debug_option):
    global debug
    if debug_option.lower() == "y" or debug_option.lower() == "yes":
        debug = True
        save_config()
        print(f"Debug option is now {bcolors.COMPLETED}enabled{bcolors.ENDC}.")
    elif debug_option.lower() == "n" or debug_option.lower() == "no":
        debug = False
        save_config()
        print(f"Debug option is now {bcolors.OKRED}disabled{bcolors.ENDC}.")
    else:
        print(f"Usage: -D/--debug <y|n>")

# Saves the pretty option to the options file
def set_pretty(pretty_option):
    global pretty
    if pretty_option.lower() == "y" or pretty_option.lower() == "yes":
        pretty = True
        save_config()
        print(f"Pretty option is now {bcolors.COMPLETED}enabled{bcolors.ENDC}.")
    elif pretty_option.lower() == "n" or pretty_option.lower() == "no":
        pretty = False
        save_config()
        print(f"Pretty option is now {bcolors.OKRED}disabled{bcolors.ENDC}.")
    else:
        print(f"Usage: -p/--pretty <y|n>")

# Saves the suppress_output option to the options file
def set_suppress_option(suppress_option):
    global suppress_output
    if suppress_option.lower() == "y" or suppress_option.lower() == "yes":
        suppress_output = True
        save_config()
        print(f"Suppress option is now {bcolors.COMPLETED}enabled{bcolors.ENDC}.")
        return True
    elif suppress_option.lower() == "n" or suppress_option.lower() == "no":
        suppress_output = False
        save_config()
        print(f"Suppress option is now {bcolors.OKRED}disabled{bcolors.ENDC}.")
        return False
    else:
        print(f"Usage: -s/-suppress <y|n>")

# Saves the updated temp_directory_option to the options file
def set_temp_directory(directory):
    global temp_download_directory
    global download_directory
    if os.path.expanduser(directory) == os.path.expanduser(download_directory):
        print(f"{bcolors.ERROR}Error: {bcolors.ENDC}Temporary download folder and destination download folder are the same. It is better to disable the temporary folder.")
        return
    if is_writable(directory):
        temp_download_directory = os.path.expanduser(directory)
        save_config()
        print(f"Directory set to: {os.path.expanduser(temp_download_directory)}")
    elif not is_writable(os.path.expanduser(directory)) and os.path.isdir(os.path.expanduser(directory)):
        print(f"Specified directory does not have write permission.")
    else:
        print(f"Invalid directory. Please provide a valid path.")
        return

# Saves the updated download_directory to the options file
def set_download_directory(directory):
    global temp_download_directory
    global download_directory
    if os.path.expanduser(directory) == os.path.expanduser(temp_download_directory):
        print(f"{bcolors.ERROR}Error: {bcolors.ENDC}Temporary download folder and destination download folder are the same.")
        print(f"It is better to disable the temporary folder.")
        return
    if is_writable(directory):
        download_directory = os.path.expanduser(directory)
        save_config()
        print(f"Download directory set to: {os.path.expanduser(download_directory)}")
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
        f.write(f"download_directory={os.path.expanduser(download_directory)}\n")
        f.write(f"temp_download_directory={os.path.expanduser(temp_download_directory)}\n")
        f.write(f"yt_dlp_options={yt_dlp_options}\n")
        f.write(f"use_temp_folder={use_temp_folder}\n")
        f.write(f"suppress_output={suppress_output}\n")
        f.write(f"debug={debug}\n")
        f.write(f"pretty={pretty}\n")

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
    open(queue_file_path, 'w').close()
    if not suppress_output:
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
        if not suppress_output:
            print(f"All contents in {yt_dlp_folder} cleared.")
    else:
        print(f"{yt_dlp_folder} does not exist.")
    
    # Delete the archive file
    if os.path.exists(archive_file):
        os.remove(archive_file)
        print(f"Archive file {archive_file} deleted.")

# Prints the help menu
def show_help():
    help_text = r"""  Commands:

    - show          : Show the current download queue and settings.
    - start         : Start the download session.
    - clear         : Clear the download queue manually.

    -a, --add
                    Add a link to the download queue.

    -r, --remove
                    Remove a link from the queue by index.

    -d, --setdir
                    Set the download directory.

    -o, --options
                    Set yt-dlp options.

    -t, --temp
                    Enables or disables the temporary download folder option.

    -T, --tempdir
                    Set the temporary download directory.

    -s, -suppress
                    Enables or disables the yt-dlp output suppression, showing only the progress bar.

    -p, --pretty
                    Enables or disables the 'pretty' menu.

    -D, --debug
                    Enables or disables debug output.

    -v, --version
                    Prints the program version.
                    
    -h, --help
                    Show this help message.
"""
    # Clears the terminal
    print(f"\033c")
    print(help_text)

def print_version():
    print(f"yt-dlp-sc version: {yt_dlp_sc_version}")

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
        return False
    except Exception as e:
        print(f"Error with {url}: {e}.")
        return False

def contains_substring(main_string, substring):
    
    return substring in main_string

item_number = "?"
total_items = "?"

def extract_download_details(line):
    global item_number
    global total_items
    # Extract the fragment number, total fragments, ETA, download speed, total size, and playlist progress.
    fragment_match = re.search(r"\(frag (\d+)/(\d+)\)", line)
    eta_match = re.search(r"ETA (\d{2}:\d{2})", line)
    speed_match = re.search(r"at\s+([~\d.]+[A-Za-z]+/s)", line)
    size_match = re.search(r"of ~\s+([~\d.]+[A-Za-z]+)", line)
    download_count = re.search(r"Downloading item (\d+) of (\d+)", line)

    # Extract fragments, ETA, download speed, and total size if available
    current_fragment = fragment_match.group(1) if fragment_match else "?"
    total_fragment = fragment_match.group(2) if fragment_match else "?"
    eta = eta_match.group(1) if eta_match else "N/A"
    speed = speed_match.group(1) if speed_match else "N/A"
    total_size = size_match.group(1) if size_match else "N/A"
    pulled_item_number = download_count.group(1) if download_count else "?"
    pulled_total_items = download_count.group(2) if download_count else "?"

    if str.isdigit(pulled_item_number):
        item_number = pulled_item_number
    if str.isdigit(pulled_total_items):
        total_items = pulled_total_items

    return current_fragment, total_fragment, eta, speed, total_size, item_number, total_items

def format_download_status(line):
    # Extract the relevant information from the line
    current_fragment, total_fragment, eta, speed, total_size, item_number, total_items = extract_download_details(line)

    if str.isdigit(f"{item_number}") and str.isdigit(f"{total_items}"):
        formatted_line = f"Downloading fragment {current_fragment}/{total_fragment} | ETA: {eta} at ~ {speed} | Video {item_number} of {total_items} size ~ {total_size}"
        return formatted_line
    else:
        formatted_line = f"Downloading fragment {current_fragment}/{total_fragment} | ETA: {eta} at ~ {speed} | Video size ~ {total_size}"
        return formatted_line

def format_merging_status(line):
    # Extract the relevant information from the line
    current_fragment, total_fragment, eta, speed, total_size, item_number, total_items = extract_download_details(line)

    if str.isdigit(f"{item_number}") and str.isdigit(f"{total_items}"):
        formatted_line = f"Merging Video and Audio files for video {item_number} of {total_items}."
        return formatted_line
    else:
        formatted_line = f"Merging Video and Audio files"
        return formatted_line

# Starts the downloading of each link in queue, sequentially.
def download_queue():
    global download_archive
    global download_directory
    global temp_download_directory
    global suppress_output
    global queue

    # CLears the terminal
    print(f"\033c")
    
    # Check if the suppress option is enabled
    if suppress_output:
        print(f"Suppression is {bcolors.COMPLETED}enabled{bcolors.ENDC}.\n")
    else:
        print(f"Suppression is {bcolors.OKRED}disabled{bcolors.ENDC}.\n")

    # Check if temporary folder option is enabled
    if use_temp_folder:
        current_download_directory = os.path.expanduser(temp_download_directory)
        print(f"Temporary folder is {bcolors.COMPLETED}enabled{bcolors.ENDC}.")
        print(f"{bcolors.OKSTATUS}Downloading to temporary folder:{bcolors.ENDC} {os.path.expanduser(current_download_directory)}")
        print(f"{bcolors.OKSTATUS}Final download folder is:{bcolors.ENDC} {os.path.expanduser(download_directory)}\n")

        # Check if the temporary download folder is the current target, and if it extsts
        if os.path.expanduser("~/Downloads/yt-dlp-sc") in os.path.expanduser(current_download_directory) and not os.path.isdir(os.path.expanduser(current_download_directory)):
            # If the default temporary download folder does not exist, try to create it
            if debug:
                print(f"Default temporary folder does not exist. Creating {os.path.expanduser(current_download_directory)}")
            if os.access(os.path.expanduser("~/Downloads"), os.W_OK):
                os.makedirs(os.path.expanduser("~/Downloads/yt-dlp-sc/"))
            # If the ~/Downloads folder is not writable, throw an error.
            elif not os.access(os.path.expanduser("~/Downloads"), os.W_OK):
                if debug:
                    print(f"DEBUG Error 40: Unable to write to ~/Downloads")
                    return
        # If the status of the ~/Downloads folder cannot be accessed.
        else:
            if debug:
                print(f"DEBUG Error 41: Unable to access ~/Downloads")
                return

    else:
        # Use final directory if temp folder is not enabled
        current_download_directory = os.path.expanduser(download_directory)
        print(f"Temporary folder is {bcolors.OKRED}disabled{bcolors.ENDC}.")
        print(f"{bcolors.OKSTATUS}Downloading directly to final directory:{bcolors.ENDC} {os.path.expanduser(current_download_directory)}\n")

    while queue:
        # Get the first link from the queue
        link = queue[0]
              
        print(f"{bcolors.OKSTATUS}Checking Queue URL:{bcolors.ENDC} {link}")
        if "www.youtube.com/" in link:
            print(f"{bcolors.COMPLETED}URL looks like it belongs to Youtube.{bcolors.ENDC}\n")
            print(f"{bcolors.OKSTATUS}Checking responsiveness{bcolors.ENDC}")
            link_valid = True
            if check_ping(link):
                print(f"{bcolors.COMPLETED}URL is responsive. Proceeding with download.{bcolors.ENDC}\n")

                link_responsive = True
            elif not check_ping(link):
                print(f"{bcolors.ERROR}Removing URL:{bcolors.ENDC} {link}\n")
                link_responsive = False
                queue.pop(0)
                save_queue()
        elif "www.youtube.com/" not in link:
            print(f"{bcolors.ERROR}Removing URL:{bcolors.ENDC} {link}\n")
            link_valid = False
            queue.pop(0)
            save_queue()

        if link_valid and link_responsive:
            if use_temp_folder:
                download_archive = f"{os.path.expanduser(current_download_directory)}/downloaded_videos.txt"
                command = ["yt-dlp", "--download-archive", download_archive] + yt_dlp_options.split() + [link]
                if debug:
                    print(f"{bcolors.OKSTATUS}Command (pretty):{bcolors.ENDC} {' '.join(command)}\n")
                    print(f"{bcolors.OKSTATUS}Command (raw):{bcolors.ENDC} {command}\n")

            elif not use_temp_folder:
                command = ["yt-dlp"] + yt_dlp_options.split() + [link]
                if debug:
                    print(f"{bcolors.OKSTATUS}Command (pretty):{bcolors.ENDC} {' '.join(command)}\n")
                    print(f"{bcolors.OKSTATUS}Command (raw):{bcolors.ENDC} {command}\n")

            if suppress_output:
                initial_panel = Panel("Fetching download information", border_style="green")
                with Live(initial_panel, refresh_per_second = 5) as live:
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
                            if ("[download]" in line and "%" in line and "ETA" in line) or ("Downloading item" in line):
                                formatted_line = format_download_status(line)
                                panel = Panel(formatted_line, title = "Download Progress", border_style = "cyan")
                                live.update(panel)
                            if "[Merger]" in line and "Merging" in line:
                                formatted_line = format_merging_status(line)
                                panel = Panel(formatted_line, title = "Download Progress", border_style = "blue")
                                live.update(panel)

                        print(f"{bcolors.COMPLETED}Finished downloading:{bcolors.ENDC} {link}\n")
                        queue.pop(0)
                        save_queue()

                    except subprocess.CalledProcessError as e:
                        stderr_output = e.stderr.decode().strip()
                        print(f"{bcolors.ERROR}Error occurred while downloading: {stderr_output}{bcolors.ENDC}")
                        break

            elif not suppress_output:
                try:
                    subprocess.run(command, check=True, cwd=os.path.expanduser(current_download_directory), stderr=subprocess.PIPE)
                    print(f"{bcolors.COMPLETED}Finished downloading:{bcolors.ENDC} {link}\n")
                    queue.pop(0)
                    save_queue()
                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode().strip()
                    print(f"{bcolors.ERROR}Error occurred while downloading: {stderr_output}{bcolors.ENDC}")
                    break        

            # Move files from temp folder to final directory if temp folder was used
            if use_temp_folder:
                move_files_to_final_directory(os.path.expanduser(temp_download_directory))

# Moves all files in the temporary download directory to the proper download folder.
def move_files_to_final_directory(temp_dir):
    temporary_directory = os.listdir(os.path.expanduser(temp_dir))
    if not temporary_directory:
        print(f"No files found in {os.path.expanduser(temp_dir)} after download.")
        return
    if debug:
        print(f"Removing archive file at {os.path.expanduser(temp_dir)}downloaded_videos.txt")
    # Move each file to the proper download directory
    for filename in temporary_directory:
        if "downloaded_videos.txt" in filename:
            os.remove(os.path.join(os.path.expanduser(temp_dir), filename))
        else:
            temp_file_path = os.path.join(os.path.expanduser(temp_dir), filename)
            global download_directory
            final_file_path = os.path.join(os.path.expanduser(download_directory), filename)
            if not suppress_output:
                print(f"Moving {temp_file_path} to {final_file_path}")
            shutil.move(temp_file_path, final_file_path)
    clear_queue()
    if os.path.expanduser("~/Downloads/yt-dlp-sc") in os.path.expanduser(temp_dir):
        os.rmdir(temp_dir)
        if debug:
            print(f"Removed empty directory at {os.path.expanduser(temp_dir)}")

    if not suppress_output:
        print(f"All downloaded files have been moved to the final directory.")

# Prints the current settings and links in queue
def show_settings():

    # Clears the terminal
    if not debug:
        print(f"\033c")

    if download_directory == "~" and yt_dlp_options == "":
        write_default_options()
        if download_directory == "~" and yt_dlp_options == "":
            if not suppress_output:
                print(f"  {bcolors.ERROR}DEBUG Error 20:{bcolors.ENDC} Program is not seeing default options file, generation seemingly failed.\n")

    # ASCII Art
    art = r"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        _                  _ _                                   ___    ___    ___    ┃
┃       | |                | | |                                 |__ \  |__ \  / _ \   ┃
┃  _   _| |_   ______    __| | |_ __    ______   ___  ___   __   __ ) |    ) || | | |  ┃
┃ | | | | __| |______|  / _` | | '_ \  |______| / __|/ __|  \ \ / // /    / / | | | |  ┃
┃ | |_| | |_           | (_| | | |_) |          \__ | (__    \ V // /_   / /_ | |_| |  ┃
┃  \__, |\__|           \__,_|_| .__/           |___/\___|    \_/|____()|____()\___/   ┃
┃   __/ |                      | |                                                     ┃
┃  |___/                       |_|                                                     ┃
┃                                                By: DredBaron 🯆                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """

    # Print art
    if pretty:
        print(art)

    # Current Settings output
    print(f"  {bcolors.BOLD}{bcolors.COMPLETED}Current settings:{bcolors.ENDC}\n")

    # Download directory
    print(f"  {bcolors.UNDERLINE}Download directory is:{bcolors.ENDC}")
    print(f"  {bcolors.OKBLUE}{os.path.expanduser(download_directory)}{bcolors.ENDC}\n")
    
    # Temporary directory
    print(f"  {bcolors.UNDERLINE}Temporary download folder is:{bcolors.ENDC}")
    if use_temp_folder:
        print(f"  {bcolors.OKBLUE}{os.path.expanduser(temp_download_directory)}{bcolors.ENDC}\n")
    elif not use_temp_folder:
        print(f"  {bcolors.OKRED}Disabled\n{bcolors.ENDC}")
    else:
        print(f"  {bcolors.ERROR}Temporary download folder is not set.{bcolors.ENDC}\n")
    
    # yt-dlp options
    print(f"  {bcolors.UNDERLINE}yt-dlp options are:{bcolors.ENDC}")
    print(f"  {bcolors.OKBLUE}{yt_dlp_options}{bcolors.ENDC}\n")

    # Output suppression
    print(f"  {bcolors.UNDERLINE}Output suppresion is:{bcolors.ENDC}")
    if suppress_output:
        print(f"  {bcolors.OKBLUE}Enabled{bcolors.ENDC}\n")
    elif not suppress_output:
        print(f"  {bcolors.OKRED}Disabled{bcolors.ENDC}\n")

    # Debug
    print(f"  {bcolors.UNDERLINE}Debug is:{bcolors.ENDC}")
    if debug:
        print(f"  {bcolors.OKBLUE}Enabled{bcolors.ENDC}\n")
    elif not debug:
        print(f"  {bcolors.OKRED}Disabled{bcolors.ENDC}\n")



    # Download queue
    print(f"  {bcolors.OKBLUE}{bcolors.BOLD}{bcolors.COMPLETED}Current download queue:{bcolors.ENDC}")
    if not is_file_blank(queue_file_path):
        for index, link in enumerate(queue):
            print(f"  {bcolors.OKSTATUS}{index} - {link}{bcolors.ENDC}")
        print(f"")
    else:
        print(f"  Nothing in queue\n")

# Main loop, handles command options
def main():
    load_queue()
    load_options()

    # Blank command, defaults to show
    if len(sys.argv) < 2:
        show_settings()
        return
    
    # Clear command
    command = sys.argv[1]
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_queue()
        return
    
    # Add command
    elif command == '-a' or command == '--add':
        if len(sys.argv) < 3:
            print(f"Usage: -a/--add <link>")
            return
        add_to_queue(sys.argv[2])

    # Show command
    elif command == 'show':
        show_settings()

    # Remove command
    elif command == '-r' or command == '--remove':
        if len(sys.argv) < 3:
            print(f"Usage: -r/--remove <index>")
            return
        try:
            index = int(sys.argv[2])
            remove_from_queue(index)
        except ValueError:
            print(f"Invalid index")

    # Setdir command
    elif command == '-d' or command == '--dir':
        if len(sys.argv) < 3:
            print(f"Usage: -d/--dir <directory path>")
            return
        set_download_directory(os.path.expanduser(sys.argv[2]))

    # Tempdir command
    elif command == '-T' or command == '--tempdir':
        if len(sys.argv) < 3:
            print(f"Usage: -T/--tempdir <directory>")
            return
        set_temp_directory(os.path.expanduser(sys.argv[2]))

    # Supp command
    elif command == '-s' or command == '--suppress':
        if len(sys.argv) > 1 and (sys.argv[1] == '-s' or sys.argv[1] == '--suppress'):
            if len(sys.argv) == 3:
                set_suppress_option(sys.argv[2])
            else:
                print(f"Usage: -s/--suppress <y|n>")
        
    # Options command    
    elif command == '-o' or command == '--options':
        if len(sys.argv) < 3:
            print(f"Usage: -o/--options <yt-dlp options>")
            return
        set_yt_dlp_options(' '.join(sys.argv[2:]))
    
    # Start command
    elif command == 'start':
        if not queue:
            print(f"The queue is empty. Please add links before starting the download.")
            return
        download_queue()

    # Temp command
    elif command == '-t' or command == '--temp':
        if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--temp"):
            if len(sys.argv) == 3:
                set_temp_directory_option(sys.argv[2])
            else:
                print(f"Usage: -t/--temp <y|n>")

    # Debug command
    elif command == '-D' or command == '--debug':
        if len(sys.argv) > 1 and (sys.argv[1] == '-D' or sys.argv[1] == '--debug'):
            if len(sys.argv) == 3:
                set_debug(sys.argv[2])
            else:
                print(f"Usage: -D/--debug <y|n>")

    # Pretty command
    elif command == '-p' or command == '--pretty':
        if len(sys.argv) > 1 and sys.argv[1] == 'pretty':
            if len(sys.argv) > 1 and (sys.argv[1] == '-dp' or sys.argv[1] == '--pretty'):
                set_pretty(sys.argv[2])
            else:
                print(f"Usage: -p/--pretty <y|n>")

    # Help command
    elif command == '-h' or command == '--help':
        show_help()

    # Version command
    elif command == '--version':
        if len(sys.argv) < 3:
            print_version()
        else:
            print(f"This option does not take arguments")
    # Unknown command
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
