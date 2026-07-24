import requests
from urllib import parse
import os
import xmltodict


class VLC:
	def __init__(self,auth,base="http://localhost:8080/requests/",playlist_path="",debug=False):
		self.auth = auth
		self.base = base
		self.playlist_path = playlist_path
		self.debug = debug

	def api_foo(self,word,command=False):
		try:
			if command:
				url = self.base + word + ".json?command="+command
			elif word == "playlist_jstree":
				url = self.base + word + ".xml"
			else:
				url = self.base + word + ".json"
			if self.debug:
				print(url)
			headers = {"Authorization": self.auth}
			r = requests.get(url, headers=headers)
			if r.status_code == 200:
				if url[-3:] == "xml":
					return (True, r.text)
				else:
					return (True, r.json())
			else:
				if self.debug:
					print(r.status_code)
					print(r.headers)
					print(r.text)
				return (False, "")
		except:
			if self.debug:
				print("Exception")
			return (False, "")

	def format_playlist_data(self,xml):
		try:
			data_dict = xmltodict.parse(xml)
			return data_dict['root']['item']['item'][0]['item']
		except:
			return False

	def get_status(self):
		return self.api_foo("status")

	def pause(self):
		return self.api_foo("status","pl_pause")

	def play(self,id=False):
		if id:
			command = "pl_play&id={}".format(id)
		else:
			command = "pl_play"
		return self.api_foo("status",command=command)

	def get_playlist(self):
		r, data = self.api_foo("playlist_jstree")
		if not r:
			return (False, "")
		obj = self.format_playlist_data(data)
		if obj:
			return (True, obj)
		return (False, "")

	def fullscreen(self):
		return self.api_foo("status","fullscreen")

	def empty_playlist(self):
		return self.api_foo("status", "pl_empty")

	def add_playlist(self,name):
		# check if playlist exists
		if self.debug:
			print(self.playlist_path + name)
		if not os.path.isfile(self.playlist_path + name):
			return (False,"Playlist doesn't exist")

		# empty playlist
		r, s = self.empty_playlist()
		if not r:
			return (False,"")

		# Add new playlist
		path = parse.quote_plus("file://"+self.playlist_path + name).replace("+","%2520")
		return self.api_foo("status",command="in_play&input={}".format(path))

	def set_volume(self,volume):
		val = int(float(volume) * 2.56)
		return self.api_foo("status","volume&val={}".format(val))

	def seek(self,percent):
		return self.api_foo("status", "seek&val={}%25".format(percent))
