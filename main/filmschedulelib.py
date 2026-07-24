import qrcode
from PIL import Image, ImageDraw, ImageFilter

class FilmSchedule:
	def __init__(self,file_name,path):
		self.playlist = {"files":{},"playing":""}
		self.path = path
		self.file_name = file_name

	def create_html(self,playlist):
		pass

	def write_html(self,html):
		pass

	def update_html(self,playlist):
		if playlist == self.playlist:
			return True
		self.playlist = playlist
		html = self.create_html(playlist)
		return self.write_html(html)

	def generate_QR_code(self,url,path,name="the.show.will.begin.shortly_qr.jpg"):
		try:
			bg = Image.open('{}the.show.will.begin.shortly.jpg'.format(path))
		except:
			return False
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=14,
			border=1,
		)
		qr.add_data(url)
		qr.make(fit=True)

		img = qr.make_image(fill_color="black", back_color="white")
		img.save(path+"qr_code.jpg")
		img2 = Image.open(path+"qr_code.jpg")
		bg.paste(img2,(1522,682,1900,1060))
		bg.save(path + name)

		return True
