  yt-dlp-sc is a Python script thrown together to help with [yt-dlp](https://github.com/yt-dlp/yt-dlp) automation.

>[!WARNING]
>This is mostly meant to be a personal script for my own use, but I figure I may as well put this out there.

INSTALLATION:
  
  I manually put this script in ```/usr/bin/yt-dlp-sc/``` and added the alias to my terminal as ```alias yt='python /usr/bin/yt-dlp-sc/yt_queue.py'```

CONFIGURATION:
  
  There are two files which are created for use with the program. The files are created in ```~/.config/yt-dlp-sc``` and are ```options.conf``` and ```queue.txt```. The options.conf file is where custom
  configuration is stored, and queue.txt is where the download queue is stored.

USAGE:
  
  The program has a few different options, running it with no options or with help shows the help page.
```
    Commands:
    - add <link>      : Add a link to the download queue.
    - show            : Show the current download queue and settings.
    - remove <index>  : Remove a link from the queue by index.
    - setdir <path>   : Set the download directory.
    - setdelay <min>  : Set the retry delay in minutes. **!!Implemented, but untested!!**
    - options "opts"  : Set yt-dlp options.
    - start           : Start the download session.
    - clear           : Clears the download queue manually.
    - temp <y|n>      : Enables or disables the temporary download folder option.
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
  
  ```clear``` - Clears the download queue manually.

  ```temp``` - Enables or disables the temporary download folder. The default is ```n``` This folder is located at ```~/yt-ddlp-sc/``` and houses the video, audio, and parts until the full
  video is downloaded and combined. The final video is moved to the proper folder, and a record of the download is kept using  yt-dlp's built-in ```--download-archive``` function. This way,
  videos are not downloaded in duplicate. The file is moved before the next download starts. The intent behind this is to use the (probably) faster read/write speed of the home drive to do
  all the I/O work, then moving the file to whatever drive is specified for storage. In my experience, this is best set to ```y``` when the final directory is either a NAS or a HDD. Or both.
  
  ```help``` - Shows the help menu.

FUTURE PLANS:

  Add an auto-clear of the queue after all files have been downloaded, so users don't have to do it manually.

  Set a temporary directory option, as combining all the fragments and audio takes a lot longer on HDD's. Setting a temporary folder in ~ could allow the files to be downloaded and merged faster, then moved to the proper download folder.

>[!NOTE]
>This program uses the [yt-dlp](https://github.com/yt-dlp/yt-dlp) github repository, and is vulnerable to any and all issues present within. Any issues with yt-dlp will **MOST LIKLEY** carry over to this program, thus performance
>cannot be guarenteed. For best results, use known-working options. Any issues which result from not following this recommendation are not my fault/problem, and will **NOT** be addressed.
