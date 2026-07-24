import os
import time, datetime
from urllib import parse

class PLAYLIST():
	def __init__(self,path,debug=False):
		self.path = path
		self.playlist = {"playing_id":0,"playing_filename":"","data":[],"duration":0}
		self.playlists = self.get_playlists()
		self.debug = debug

	def get_playlist(self):
		return self.playlist

	def get_playlists(self):
		self.playlists = []
		ps = os.listdir(self.path)
		ps.sort()
		for p in ps:
			if ".m3u" in p and "-" in p:
				parts = p.split("-")
				if len(parts) < 3:
					continue
				self.playlists.append({"date":parts[0],"time":parts[1],"location":parts[2],"file":p})
		return self.playlists

	def find_next_playlist(self,useDelta=False):
		# look to see if we're in the window of a playlist
		for playlist in self.playlists:
			duration=self.get_playlist_duration(playlist)
			if self.debug:
				print(f"The duration is: {duration}")
			time_string = playlist["date"]+playlist["time"]
			t = time.mktime(datetime.datetime.strptime(time_string, "%Y%m%d%H%M").timetuple())
			now = time.time()
			if not useDelta and (t - 5) <= now and now <= (t + duration):
				return playlist
			# If not, look for a playlist starting within X hours
			elif useDelta != False and (t - useDelta*60*60) <= now and now <= (t + duration):
				return playlist
		return False

	def set_playlist(self,playlist):
		self.playlist['data'] = playlist

	def set_playing(self,playing_filename):
		self.playlist['playing_filename'] = playing_filename
		# for item in self.playlist['data']:
		# 	if item["@name"] == playing_filename:
		# 		self.playlist["playing_id"] = item["@id"][5:]

	def get_playlist_duration(self,playlist=False):
		duration = 0
		# pprint(playlist)
		with open(self.path+playlist["file"]) as file:
			lines = [line.rstrip() for line in file]
		lines.pop(0)
		for line in lines:
			if "#EXTINF:" in line:
				# print(line)
				d = int(line[8:].split(",")[0])
				duration += d
		return duration

	def get_next_file(self,file,playlist):
		# print("Get next. File {}".format(file))
		if type(playlist) == dict:
			playlist = [playlist]
		i = 1
		# pprint(playlist)
		for i in range( len(playlist)):
			if ((playlist[i]["@name"] == file or
				parse.unquote(playlist[i]["@uri"].split("/")[-1]) == file) and
					len(playlist) > (i+1)):
				return playlist[i + 1]
		return False

	def get_first_file_in_playlist(self,playlist):
		with open(self.path+playlist["file"]) as file:
			lines = [line.rstrip() for line in file]
		return {"@uri":lines[2]}
