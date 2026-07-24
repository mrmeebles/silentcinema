# silentcinema
## Description
A solution for a silent open air cinema. silentcinema was created in oder to 
show movies open air without speakers. Each viewer loads an audio player
in the browser of their mobile device and can listen in using their own
headphones.

The heart of the project is a small server, written in python, which sends 
Server Side Events (SSE) to keep the audio player and the video in sync. Also 
included are a schedule and tools for generating QR codes to connect to the 
audio player.

## Prerequisites
To make the silent cinema work, there's a few other things you're going to need:
- A Linux computer - this doesn't need to be very powerful, something like a raspberry pi 5 should work, or any mini PC, like a NUC. The rest of the steps assume the computer is running some flavor of linux. We used Fedora.
- VLC, including optional codecs (see below)
- Mercure - this is used to send SSE. You could use some other solution to send SSE, in which case you'd just need to make changes to mercurelib.py See below for configuration.
- A webserver - we used apache as included with Fedora. The server assumes the use of port 8008. See below. 

### VLC
To access the VLC API, you need to set a password for VLC. Go to VLC > Settings > HTTP Web Interface and check "Enable HTTP Web Interface". For the password enter "password1" minus the quotes. Feel free to select a different password, but if so, you will need to change the VLC_AUTH in the .env file.

You will need to set VLC to autostart when the Linux server starts. One way is to create the file in the default user's path under .config/autostart/vlc.desktop You will find an example vlc.desktop file in this repo under /system

### Mercure
Mercure must be installed on the server. Please read https://mercure.rocks/docs/getting-started

Mercure will be started with the script movie_server_start.sh

### Apache
Apache must be installed on the Linux computer and must run on port 8008. To do this, open the httpd.conf
```
$ sudo nano /etc/httpd/conf/httpd.conf
```
And add the line "Listen 8008", e.g.
```
#Listen 12.34.56.78:80
Listen 80
Listen 8008
```
To start apache at startup type
```
$ sudo systemctl enable httpd
```

### Python
The audio server requires a few python libraries. Run:

```
$ python3 -m pip install pillow qrcode requests xmltodict
```

### Folders
Copy the contents of /html to your html directory. The files details.json, schedule.json and schedule.css are included as examples. 

Copy the contents of /files to the directory where your media files will be stored.

Copy the contents of /tools where ever you like. These scripts are called manually for various functions.

Copy the contents of /main where ever you like. These are the main python files which make everything work.

## Setup
### Copy media files
Create a subfolder in the /files directory and copy your media files there. Once you have created a playlist of your media files, store it to the root of the /files directory. The filename of the playlist has a special format:

[YEAR][MONTH][DAY]-[STARTTIME]-[indoor|outdoor].m3u

So, for example, an open air screening which should start at 1:30pm local time on June first 2027 would be:

20270601-1330-outdoor.m3u

This format tells the server when to start playing the playlist. In addition, for outdoor (open air) screenings, while waiting for the screening to start, a qrcode will be shown on screen of the audio server.

### Generate audio files
After copying your media files, you will need to generate a corresponding audio files for each. To do this, run the file tools/create_audio.py as root with the source and target directories. E.g.:

```
$ sudo python3 tools/create_audio.py files/my_playlist/ /var/www/html/
```

### Run startup script
The script movie_server_start.sh needs to be run as root on startup. You'll find this script in the system directory

### Run control.py
If everything else is set up, try running control.py

```
$ python3 control.py -debug
```
The debug option will give you A LOT of debug information in the console. If it is running and not giving any errors, try opening the audio player in your browser. The address is the IP of your Linux server at port 8008. So for example, if your server's IP is 192.168.0.10, you would open the following URL in your browser: http:192.168.0.10:8008 If everything is set up correctly, when the start time of the playlist is reached, the playlist should be automatically loaded, the first file will play and audio will play from the audio server loaded in your browser. 

### Debugging
Open your browser's developer tools, and click on "console". You should see regular updates telling you the average_eof and New position. If you don't see these updates, the player is not receiving server side events. Here's what you should check:
- Make sure Mercure is running. Open your server's IP with port 8009 in a new browser tab, e.g.: http:192.168.0.10:8008. If it doesn't open, Mercure is probably not running or not accessible.
- If Mercure is running, but no SSE is getting through, it's possible the control script couldn't find it. Go through the debug output to see if mercure was detected on start up.
- If Mercure is running and control.py can see it, it's possible they can't communicate for some reason. The Mercure auth written in .env assumes the default JWT is unchanged. You may need to update this. It's also possible the SSE event is not being recognized. In the Mercure UI page you can test all of this. 
- If Mercure is running, updates are being received, but no audio is playing from the audio server, check the updates and make sure it's receiving the name of the currently playing file. In the console output, you should see "Playing: " followed by the name of the file. If updates are being received, but still no audio is being received, check the network tab and make sure the audio is being loaded. The player looks for an audio file with the same name as the media file, but ending with ".m4a". If the file doesn't exist, or is named even slightly differently, it can't be found.
- If audio is playing, but it stops when the device is put in standby or if audio sync isn't correct, try index2.html instead of index.html

## Other tools
You'll find a couple more useful scripts in the /tools directory:
- create_schedule.py - generates the schedule.json file from the playlists for use by the digital schedule
- generate_qr_codes.py - generated QR codes for connecting to the audio player
- generate_qr_wifi.py - generated QR codes for connecting to wifi

## Credits
For audio playback, howler.js is used: https://github.com/goldfire/howler.js

The example index.html uses the font Creepster: https://fonts.google.com/specimen/Creepster?preview.script=Latn
