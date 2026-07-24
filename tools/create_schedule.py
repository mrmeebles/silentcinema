import os
import math
import time, datetime
import json
from urllib import parse

def parse_playlist(lines):
	films = []
	for i in range(math.floor(len(lines) / 2)):
		# try:
		print(lines[i*2])
		print(lines[i*2 +1])
		infos = lines[i * 2][8:].split(",")

		if lines[i*2 +1][-4:] in [".mp4",".mov",".mkv"]:
				title = parse.unquote(lines[i*2 +1].split('/')[-1][:-4].replace("."," "))
		else:
				title = parse.unquote(lines[i*2 +1].split('/')[-1].replace("."," "))
		film = {"title":title,"duration":int(infos[0])}
		films.append(film)
		# except:
		# 	return []
	return films

def generate_schedule(root):
	days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
	schedule = {}
	files = os.listdir(root)
	for f in files:
		if f[-3:] != "m3u":
			print("Skipping: {}".format(f))
			continue
		print(f)
		parts = f[:-4].split("-")
		if len(parts) < 3:
			continue
		starttime = time.mktime(datetime.datetime.strptime(parts[0]+parts[1], "%Y%m%d%H%M").timetuple())

		with open(root+f) as file:
			lines = [line.rstrip() for line in file]
		lines.pop(0)

		date = parts[0][0:4]+"-"+parts[0][4:6]+"-"+parts[0][6:8]
		if date not in schedule:
			d = datetime.date(int(parts[0][0:4]), int(parts[0][4:6]), int(parts[0][6:8]))
			label = days[d.weekday()] + " " + parts[0][6:8]
			schedule[date] = {"date":date,
							  "label": label,
							  "films": []}
		list = parse_playlist(lines)
		for item in list:
			start = datetime.datetime.fromtimestamp(starttime).strftime('%H:%M')
			starttime += int(item["duration"])
			end = datetime.datetime.fromtimestamp(starttime).strftime('%H:%M')
			location = parts[2]
			if len(parts) > 3:
				imdbId = parts[3]
			else:
				imdbId = 0
			film = {"title": item["title"],
					"start": start,
					"end": end,
					"location": location,
					"imdbId": imdbId}
			schedule[date]["films"].append(film)

		final = []
		for date in schedule:
			final.append(schedule[date])
	return final


def save_schedule_json(root, file):
	data = generate_schedule(root)
	with open(file, "w") as f:
		f.write(json.dumps(data))


if __name__ == "__main__":
	save_schedule_json("./", "schedule.json")


