import subprocess
import os,sys

def escape_for_bash(text):
	text = text.replace(" ", "\ ")
	text = text.replace("~", "\~")
	text = text.replace("`", "\`")
	text = text.replace("#", "\#")
	text = text.replace("$", "\$")
	text = text.replace("&", "\&")
	text = text.replace("*", "\*")
	text = text.replace("(", "\(")
	text = text.replace(")", "\)")
	text = text.replace("|", "\|")
	text = text.replace("[", "\[")
	text = text.replace("]", "\]")
	text = text.replace("{", "\{")
	text = text.replace("}", "\}")
	text = text.replace(";", "\;")
	text = text.replace("'", "\'")
	text = text.replace("<", "\<")
	text = text.replace(">", "\>")
	text = text.replace("/", "\/")
	text = text.replace("?", "\?")
	text = text.replace("!", "\!")
	return text

	
def generate_audio(source,target):
	files = os.listdir(source)
	for f in files:
		if f[0:1] == "." or f in ["audio"] or f[-3:] in ["srt","m3u","jpg"]:
			continue
		file = escape_for_bash(f)
		source_path = "{}{}".format(source, file)
		target_path = "{}audio/{}.m4a".format(target, file[:-4])
		print("ffmpeg -i {} -vn -strict experimental -c:a aac -b:a 128k {}".format(source_path, target_path))
		# subprocess.run("ffmpeg -i {}{} {}audio/{}.mp3".format(root,file,root,file[:-4]).replace(" ","\ "))
		subprocess.run("ffmpeg -i {} -vn -strict experimental -c:a aac -b:a 128k -movflags +faststart -ac 2 {}".format(source_path, target_path),shell=True)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: python create_audio.py <source> <target>")
	else:
		generate_audio(sys.argv[1],sys.argv[2])