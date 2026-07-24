import qrcode
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

if len(sys.argv) < 2:
	print("Usage: python generate_qr_codes.py ip")
	quit()


# Generate QRcodes of film schedule and audio player
def generate_QR_code(url, text, name, path="./"):
	# Create empty image
	img = Image.new("RGB", (1920, 1080), (255, 255, 255))
	timg = Image.new("RGB", (1080, 1080), (255, 255, 255))
	# Call draw Method to add 2D graphics in an image
	I1 = ImageDraw.Draw(timg)
	# Add Text to an image
	myFont = ImageFont.truetype('/Users/silentcinema/Library/Fonts/DrCaligari.ttf', 180)
	I1.text((20, 280), text, font=myFont, fill=(0, 0, 0))
	# I1.text((20, 100), text, font=myFont, fill=(0, 0, 0))
	# timg.show()
	timg2 = timg.rotate(90)
	img.paste(timg2, (0, 0,1080,1080))

	# Display edited image
	# img = Image.new("L", (1920, 1080))
	# except:
	# 	return False
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=30,
		border=1,
	)
	qr.add_data(url)
	qr.make(fit=True)
	img2 = qr.make_image(fill_color="black", back_color="white")
	img2.save(f"{path}{name}-raw.png")
	img3 = Image.open(f"{path}{name}-raw.png")
	width, height = img3.size
	x = int((1920-width)/2) + 50
	y = int((1080-height)/2)
	#
	# img.paste(qr,(0,692))
	# img2.save(path + "qr_code.jpg")
	# img2 = Image.open(path + "qr_code.jpg")
	img.paste(img3, (x,y,x+width,y+height))
	# bg.save(path + name)
	#
	# return True
	img.save(f"{name}-.png", "PNG")

def generate_QR_codes(url, path="./"):
	generate_QR_code(url,"Screening WiFi","qr_screening_wifi")

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: python generate_qr_wifi.py SSID password")
		quit()
	ssid = sys.argv[1]
	pw = sys.argv[2]
	t = "WPA"
	h = "false"
	if len(sys.argv) > 3 and sys.argv[3] in ["WPA","WEP"]:
		t = sys.argv[3]
	if len(sys.argv) > 4 and sys.argv[4] in ["true","false"]:
		h = sys.argv[4]
	generate_QR_codes(f"WIFI:T:{t};S:{ssid};P:{pw};H:{h};;")
