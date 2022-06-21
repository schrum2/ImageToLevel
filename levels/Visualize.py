import glob
from PIL import Image

def visualize(level, sprites, spriteAsciiMap, pixelSize):
	maxY = len(level)
	maxX = len(level[0].rstrip("\n")) # remove the "\n"
	image = Image.new("RGB", (maxX*pixelSize, maxY*pixelSize), color=(91, 153, 254))
	pixels = image.load()

	for y in range(0, maxY):
		for x in range(0, maxX):
			imageToUse = None
			if level[y][x] in spriteAsciiMap.keys():
				if(level[y][x] != "-"):
					asciiVal = spriteAsciiMap[level[y][x]][0]
					imageToUse = sprites[asciiVal][0]
			if level[y][x]=="X":
				if y>maxY-2:
					imageToUse = sprites["ground"][0]
				else:
					imageToUse = sprites["stair"][0]
			if not imageToUse == None:
				pixelsToUse = imageToUse.load()
				for x2 in range(0, pixelSize):
					for y2 in range(0, pixelSize):
						qqq = pixelsToUse[x2,y2]
						qq = pixels[x*pixelSize+x2,y*pixelSize+y2]
						pixels[x*pixelSize+x2,y*pixelSize+y2] = pixelsToUse[x2,y2]
			else:
				#This part is for adding holes in the level
				if(level[y][x] == " "):
					for x2 in range(0, pixelSize):
						for y2 in range(0, pixelSize):
							pixels[x*pixelSize+x2,y*pixelSize+y2] = (0,0,0)
	
	return image