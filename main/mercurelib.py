from pprint import pprint
import json
import requests

class MERCURE:
	def __init__(self,token,url,topic,debug=False):
		self.token = token
		self.event = 0
		self.topic = topic
		self.url = url
		self.debug = debug

	def send_update(self,data="blah",id=False,type="",topic=False):
		if not topic:
			topic = self.topic
		if not id:
			self.event += 1
			id = self.event
		obj = {"data": json.dumps(data),
			   "id": id,
			   "type": type,
			   "retry": "",
			   "topic": topic}
		if self.debug:
			pprint(obj)

		headers = {"Authorization": self.token}
		r = requests.post(self.url, data=obj, headers=headers)
		if self.debug:
			print(r.status_code)
			print(r.headers)
			print(r.text)
		if r.status_code == 200:
			return True
		else:
			return False


