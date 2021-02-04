from PIL import Image
import numpy as np
import sys

# ceci est un exemple pour convertir une image 24 bit
# en image 16bits (656) pour utiliser avec ole1331
#
#
#  ex:
#
#  python3 ToRGB565  imagefile  className
#
#  ceci va créer un fichier className.py 
#  contenant la classe python avec un framebuf
#  directement accessible une fois l'objet créer



if len(sys.argv) != 3:
   print("usage:   img_rgb565 imagefile classname")
   quit()
   
img = Image.open(sys.argv[1])
imgarray = np.array(img)
 
H, W , depth = imgarray.shape

if depth != 3:
   print("image need to be 24 bit RGB")
   quit()
 

# lambda function to convert 24bit RGB to 16 BIT RGB565
RGB565 = lambda r, g , b : [(r & 0xf8) | g >> 5 , (g & 0x1c) <<3  | b >> 3]


# create a new array with 2 bytes for RGB565
imgRGB565 = np.array([[RGB565(i[0],i[1],i[2]) for i in j] for j in imgarray])

# ok we need bytearray
byteRGB565 = imgRGB565.astype(np.ubyte).tobytes()

# all done now lets create image buffer

imgLength = len(byteRGB565)

file=open(sys.argv[2]+".py","wt")

file.write("import framebuf\n\n")
file.write("class {}:\n".format(sys.argv[2]))
file.write("    width = {}\n".format(imgRGB565.shape[1]))
file.write("    height = {}\n".format(imgRGB565.shape[0]))
file.write("    img = bytearray(b\"")
startLine = False
for i in range(imgLength):
    if startLine:
        file.write("\"\\\n             b\"")
        startLine = False
    file.write("\\x{:02X}".format(byteRGB565[i]))
    if i % 16 == 15:
        startLine = True
file.write("\")\n")
file.write("    Fb = framebuf.FrameBuffer(img, width, height,framebuf.RGB565)\n")
file.close()

