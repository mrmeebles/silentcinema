from VLClib import VLC
from mercurelib import MERCURE
from filmschedulelib import FilmSchedule
from playlistlib import PLAYLIST
import time
import os
import sys
from pprint import pprint
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# use debug mode to get a lot of output in the console for debugging
if len(sys.argv) > 1 and sys.argv[1] == "-debug":
	debug = True
else:
	debug = False

# check for existing instances of this script and exit if already running
raw = os.popen("ps ax|grep control.py").read().split('\n')
check = False
pid = str(os.getpid())
for line in raw:
	if pid in line:
		continue
	if debug:
		print(line)
	if "python3" in line and "control.py" in line:
		check = True
if check:
	print("control.py already running. Exiting second instance...")
	quit()

# wait to make sure the other services are live
time.sleep(6)

# define a bunch of global variables
last_check = 0
playing = ""
playing_fullscreen = ""
next_file = False
next_playlist = False
VLC_is_running = 0
VLC_is_starting = 0
end_time_current_file = 0
mercure_is_running = 0
mercure_is_starting = 0
mercure_update = 0
is_online = 0
local_ip = ""


# If you develop on mac, update the paths under "darwin" to whatever you're using
if sys.platform == "darwin":
	playlist_root_path = "/Users/silentcinema/files/"
	vlc_path = "/Applications/VLC.app/Contents/MacOS/VLC"
	vlc_string = "VLC.app"
	h = FilmSchedule("schedule.html","html/")
	v = VLC(os.getenv('VLC_AUTH'),playlist_path=playlist_root_path,debug=debug)
else:
	playlist_root_path = '/home/silentcinema/files/'
	vlc_path = "/usr/bin/vlc"
	vlc_string = "/usr/bin/vlc"
	h = FilmSchedule("schedule.html","/var/www/html/")
	v = VLC(os.getenv('VLC_AUTH'), playlist_path=playlist_root_path,debug=debug)
m = False
p = PLAYLIST(playlist_root_path)


# On startup, load waiting image into vlc, pause and enter fullscreen.
ip = os.popen("ifconfig|grep -E -o 'inet (192.168|10.10).[0-9]{1,3}.[0-9]{1,3}'|grep -E -o '(192.168|10.10).[0-9]{1,3}.[0-9]{1,3}'").read().strip()
if ip == "" or len(ip) < 8:
	if debug:
		print("No IP found")
	is_online = False
	local_ip = "127.0.0.1"
else:
	if debug:
		print("IP: {}".format(ip))
	is_online = True
	local_ip = ip
	m = MERCURE(os.getenv('MERCURE_TOKEN'),"http://{}:8009/.well-known/mercure".format(ip),"http://{}:8009/status".format(ip),debug=debug)
	# Update the QR code with the local network
	h.generate_QR_code("http://{}:8008".format(ip),playlist_root_path)

# Check if Mercure is running
def is_mercure_running():
	raw = os.popen("ps ax|grep docker").read().split('\n')
	for line in raw:
		if "docker" in line and "MERCURE_PUBLISHER_JWT" in line:
			return True
	return False
mercure_is_running = is_mercure_running()


control = True
while control:
	### Every 1 second
	# Check if VLC is running
	raw = os.popen("ps ax|grep {}".format(vlc_string)).read().split('\n')
	if len(raw) > 3:
		VLC_is_running = True
	else:
		VLC_is_running = False

	# If VLC is running, get a status update
	if VLC_is_running:
		#  if last check >= 10 seconds ago OR +- 5 second of expected end
		if time.time() > (last_check + 10) or abs(end_time_current_file - time.time()) <= 5:
			# check if mercure is running
			if not mercure_is_running:
				mercure_is_running = is_mercure_running()
			#  get playlist and current file from VLC, note time when call returned as reference
			prestatus_time = time.time()
			file_status,file_info = v.get_status()
			status_time = time.time()
			playlist_status,playlist_info = v.get_playlist()
			post_playlist_time = time.time()
			# Find which file is playing
			if ('information' in file_info and
				 'category' in file_info['information'] and
				 'meta' in file_info['information']['category'] and
				 'filename' in file_info['information']['category']['meta']):
				playing = file_info['information']['category']['meta']['filename']
				if playing not in ['', 'start_soon.jpg','start_soon_qr.jpg','the.show.will.begin.shortly.jpg','the.show.will.begin.shortly_qr.jpg']:
					# If a file is playing, check for the next file in the playlist
					next_file = p.get_next_file(playing,playlist_info)
					if debug:
						pprint(file_info)
						pprint(playlist_info)
						# print(f"Next: {next_file}")
				elif next_playlist != False:
					next_file = p.get_first_file_in_playlist(next_playlist)
				else:
					next_file = False
				if debug:
					print("Next_file:")
					pprint(next_file)
			else:
				playing = ""

			if debug:
				print("Playing: {}".format(playing))

			# get end time
			if ('length' in file_info and 'position' in file_info):
				end_time_current_file = status_time + float(file_info['length']) * (1 - file_info['position'])

			# if no playlist is loaded, check if it's time to start, otherwise load wait screen
			if (not playlist_status and
				file_status and
				file_info["state"] == "stopped") or (playlist_status and
				 file_status and playing in ['start_soon.jpg','start_soon_qr.jpg','the.show.will.begin.shortly.jpg','the.show.will.begin.shortly_qr.jpg']):
				next_playlist = p.find_next_playlist()
				if next_playlist:
					if debug:
						print("adding playlist {}".format(next_playlist["file"]))
					v.add_playlist(next_playlist['file'])
				elif playing not in ['start_soon.jpg','start_soon_qr.jpg','the.show.will.begin.shortly.jpg','the.show.will.begin.shortly_qr.jpg']:
					future_playlist = p.find_next_playlist(2)
					# if debug:
						# print("adding waiting image")
						# pprint(future_playlist)
					if (future_playlist and
							"location" in future_playlist and
							future_playlist["location"] in ["outdoor.m3u","pool.m3u"] and
							playing != "the.show.will.begin.shortly_qr.jpg"
					):
						if debug:
							print("Found future playlist {}".format(future_playlist["file"]))
						h.generate_QR_code("http://{}:8008".format(ip),playlist_root_path)
						v.add_playlist("the.show.will.begin.shortly_qr.jpg")
						time.sleep(1)
						v.pause()
					elif playing != "the.show.will.begin.shortly.jpg":
						if debug:
							print("loading start screen")
						v.add_playlist("the.show.will.begin.shortly.jpg")
						time.sleep(1)
						v.pause()
				time.sleep(1)
			# Check for fullscreen
			if file_status and "fullscreen" in file_info and file_info["fullscreen"] == False and playing_fullscreen != playing:
				v.fullscreen()
				playing_fullscreen = playing

			#  if we think mercure is running send update to players
			if m and mercure_is_running and file_status and playing != "":
				if debug:
					print("Send mercure update for {}".format(playing))
				#  player update: link to audio file, start time and current playtime
				audioURI = "http://{}:8008/audio/{}.m4a".format(ip,urllib.parse.quote(playing[:-4]))
				if playing[-4:] in ['.jpg','avif','webp','jpeg']:
					loop = True
				else:
					loop = False
				mercure_update += 1
				premercure_time = time.time()
				data = {"playing":audioURI,
						"duration":file_info['length'],
						"position":file_info['position'],
						"ref_time":status_time,
						"now_time":premercure_time,
						"state":file_info['state'],
						"est_eof":end_time_current_file,
						"loop":loop}
				m.send_update(data,mercure_update)
				postmercure_time = time.time()
				if debug:
					print("{},+{},+{} | mercure +{},+{}".format(
					(prestatus_time),
					(status_time - prestatus_time),
					(post_playlist_time - prestatus_time),
					(premercure_time - prestatus_time),
					(postmercure_time - prestatus_time),
					))
				#  if current file within 10 minutes of end, send message to prequeue next file
				if debug:
					print("End time: {}, current time: {}, diff: {}".format(end_time_current_file, time.time(), (end_time_current_file - time.time())))
				if end_time_current_file - time.time() < 600 and next_file:
					next_file_name = next_file["@uri"].split("/")[-1]
					if debug:
						print("Found next file {}".format(next_file_name))
					audioURI = "http://{}:8008/audio/{}.m4a".format(ip, urllib.parse.unquote(urllib.parse.unquote(next_file_name[:-4])))
					data = {"next":audioURI,"duration":next_file['@duration']}
					if debug:
						pprint(data)
					mercure_update += 1
					m.send_update(data, mercure_update)
			# control = False
			last_check = time.time()

	# wait for  one second before the next update to save resources
	time.sleep(1)