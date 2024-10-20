  yt-dlp-sc is a Python script thrown together to help with [yt-dlp](https://github.com/yt-dlp/yt-dlp) automation.

>[!WARNING]
>This is mostly meant to be a personal script for my own use, but I figure I may as well put this out there.

INSTALLATION:
  
  ```git clone https://github.com/dredbaron/yt-dlp-sc```

  ```cd yt-dlp-sc```

  ```make install```

This project also requires that yt-dlp is installed.

CONFIGURATION:
  
  There are two files which are created for use with the program. The files are created in ```~/.config/yt-dlp-sc``` and are ```options.conf``` and ```queue.txt```. The ```options.conf``` file is where custom
  configuration is stored, and ```queue.txt``` is where the download queue is stored. The script may throw a couple errors on first execution, but it will generate a default ```options.conf``` and a blank ```queue.txt``` file.

USAGE:
  
  The program has a few different options, running it with no options or with help shows the help page.
```
  Commands:

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

    
                    Enables or disables the temporary download folder option.

    -T, --tempdir
                    Set the temporary download directory.

    -s, -suppress
                    Enables or disables the yt-dlp output suppression.

    -p, --pretty
                    Enables or disables the 'pretty' menu.

    -D, --debug
                    Enables or disables debug output.

    -v, --version
                    Prints the program version.
                    
    -h, --help
                    Show this help message.
```
OPTIONS:

  ```show``` - Shows all options, and the links in queue.
  
  ```start``` - Starts the download with whatever is in the download queue
  
  ```clear``` - Clears the download queue manually. This also clears the temporary download folder and download archive file. Best not to use until all downloads are complete.

  ```-a, --add``` - Adds the following link to the queue file.
  
  ```-r, --remove``` - Removes the link in queue at the specified index. This queue can be seen with show.
  
  ```-d, --setdir``` - Sets the download directory. I have not tested this with relative filepaths, so I would recommend absolute.
  
  ```-o, --options``` - Lets you set custom yt-dlp options. The default is 
  ```-f bv*[height<=1080][ext=mp4]+ba*[ext=m4a] -N 2```

  ```-t, --temp``` - Enables or disables the temporary download folder. The default is ```n``` This folder is located at ```~/yt-ddlp-sc/``` and houses the video, audio, and parts until the full
  video is downloaded and combined. The final video is moved to the proper folder, and a record of the download is kept using  yt-dlp's built-in ```--download-archive``` function. This way,
  videos are not downloaded in duplicate. The file(s) are moved after all files in the download queue have completed. The intent behind this is to use the (probably) faster read/write speed
  of the home drive to do all the I/O work, then moving the file to whatever drive is specified for storage. In my experience, this is best set to ```y``` when the final directory is either
  a NAS or a HDD. Or both.

  ```-T, --tempdir``` - Sets the temporary download directory location. This and ```setdir``` have collision detection, as there is no reason to waste time moving files to the same directory. This
  directory will house a file called ```downloaded_videos.txt```, this is the yt-dlp archive file. Once the download is complete and all files are moved to the destination directory, this
  file is deleted.

  ```-s, -suppress``` - Enables or disables the yt-dlp output suppression. When disabled, there is no change to the standard yt-dlp output. When enabled, the output is rolled into a little box
  at the bottom of the terminal, displaying, for example:
  
```
╭──────────────────────────────────────────── Download Progress ────────────────────────────────────────────╮
│ Downloading fragment 96/1018 | ETA: 00:36 at ~ 47.10MiB/s | Total size ~ 1.68GiB | Video 3 of 7 ~ 2.23GiB │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

```
╭──────────────────────────────────────────── Merging Progress ─────────────────────────────────────────────╮
│ Merging files into final file                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

  ```-p, --pretty``` - Enables or disabled the pretty version of the UI. Currently, this is just the ASCII art.

  ```-D, --debug``` - Enables or disables debug error output, and whether the screen clears on UI refresh.

  ```--version``` - Displays the program version. Not in the help menu yet, but it is a vailid command option as of 2.1.0
  
  ```-h, --help``` - Shows the help menu.

FUTURE RELEASE PLANS:

* Add ability to parse multiple command optins in one command.

* Show video title somewhere during downloading

* Create a more <b>responsive</b> UI. Not sure what that exactly means, but that'll get figured out.

>[!NOTE]
>This program uses the [yt-dlp](https://github.com/yt-dlp/yt-dlp) github repository, and is vulnerable to any and all issues present within. Any issues with yt-dlp will **MOST LIKLEY** carry over to this program, thus performance
>cannot be guarenteed. For best results, use known-working options. Any issues which result from not following this recommendation are not my fault/problem, and will **NOT** be addressed.
