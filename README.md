  yt-dlp-sc is a Python script thrown together to help with [yt-dlp](https://github.com/yt-dlp/yt-dlp) automation.

>[!WARNING]
>This is mostly meant to be a personal script for my own use, but I figure I may as well put this out there.

INSTALLATION:
  
  I manually put ```yt-dlp-sc.py``` in ```/usr/bin/yt-dlp-sc/``` and added the alias to my terminal as ```alias yt='python /usr/bin/yt-dlp-sc/yt-dlp-sc.py'```

CONFIGURATION:
  
  There are two files which are created for use with the program. The files are created in ```~/.config/yt-dlp-sc``` and are ```options.conf``` and ```queue.txt```. The ```options.conf``` file is where custom
  configuration is stored, and ```queue.txt``` is where the download queue is stored. The script may throw a couple errors on first execution, but it will generate a default ```options.conf``` and a blank ```queue.txt``` file.

USAGE:
  
  The program has a few different options, running it with no options or with help shows the help page.
```
    Commands:
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
```
OPTIONS:

  ```add``` - Adds the following link to the queue file.

  ```show``` - Shows all options, and the links in queue.
  
  ```remove``` - Removes the link in queue at the specified index. This queue can be seen with show.
  
  ```setdir``` - Sets the download directory. I have not tested this with relative filepaths, so I would recommend absolute.
  
  ```setdelay``` - If the program detects the "Please log in to prove you are not a bot" error, the delay can be set for how long the program will wait in minutes to auto-resume.
  
  ```options``` - Lets you set custom yt-dlp options. The default is 
  ```-f bv*[height<=1080][ext=mp4]+ba*[ext=m4a] -N 2```
  
  ```start``` - Starts the download with whatever is in the download queue
  
  ```clear``` - Clears the download queue manually. This also clears the temporary download folder and download archive file. Best not to use until all downloads are complete.

  ```temp``` - Enables or disables the temporary download folder. The default is ```n``` This folder is located at ```~/yt-ddlp-sc/``` and houses the video, audio, and parts until the full
  video is downloaded and combined. The final video is moved to the proper folder, and a record of the download is kept using  yt-dlp's built-in ```--download-archive``` function. This way,
  videos are not downloaded in duplicate. The file(s) are moved after all files in the download queue have completed. The intent behind this is to use the (probably) faster read/write speed
  of the home drive to do all the I/O work, then moving the file to whatever drive is specified for storage. In my experience, this is best set to ```y``` when the final directory is either
  a NAS or a HDD. Or both.

  ```settemp``` - Sets the temporary download directory location. This and ```setdir``` have collision detection, as there is no reason to waste time moving files to the same directory. This
  directory will house a file called ```downloaded_videos.txt```, this is the yt-dlp archive file. Once the download is complete and all files are moved to the destination directory, this
  file is deleted.

  ```supp <y|n>``` - Enables or disables the yt-dlp output suppression. WHen disabled, there is no change to the standard yt-dlp output. When enabled, the output is rolled into a little box
  at the bottom of the terminal, displaying, for example:
  
```
╭──────────────────────────────────────────────── Download Progress ────────────────────────────────────────────────╮
│ Downloading fragment 96/1018 | ETA: 00:36 at ~ 47.10MiB/s | Total size ~ 1.68GiB                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

```
╭──────────────────────────────────────────────── Merging Progress ─────────────────────────────────────────────────╮
│ Merging files into final file                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
  
  ```help``` - Shows the help menu.

FUTURE PLANS:

  Nothing specific on the docket as of now, but this is subject to change on a whim.

>[!NOTE]
>This program uses the [yt-dlp](https://github.com/yt-dlp/yt-dlp) github repository, and is vulnerable to any and all issues present within. Any issues with yt-dlp will **MOST LIKLEY** carry over to this program, thus performance
>cannot be guarenteed. For best results, use known-working options. Any issues which result from not following this recommendation are not my fault/problem, and will **NOT** be addressed.
