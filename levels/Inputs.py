import os
import json
import glob
import cv2

from PIL import Image

def Get_All_Inputs(dataLocation, selectedGame):
	levelLocation = dataLocation + selectedGame +"/game-levels-ascii/*.txt"
	spriteLocation = dataLocation + selectedGame + "/sprites/*.png"
	gameJsonFile = dataLocation + selectedGame + "/gameMetadata.json"
	
	asciiLevels = []
	for levelFile in glob.glob(levelLocation):
		with open(levelFile) as fp:
			level = {}
			y = 0
			for line in fp:
				level[y] = line
				y+=1
			asciiLevels.append(level)
	
	gameMetaData = json.load(open(gameJsonFile))
	asciiList = gameMetaData['tiles']
	
	sprites = {}
	for filename in glob.glob(spriteLocation):
		im = Image.open(filename)
		cv_im = cv2.imread(filename)
		splits = os.path.split(filename)
		name = splits[-1][:-4]
		sprites[name] = [im, cv_im]
	
	spriteAsciiMap = {}
	keys = list(asciiList.keys())
	for i in range(0, len(keys)):
		key = keys[i]
		spriteAsciiMap[key] = asciiList[key]['sprites']
		
	return asciiLevels, sprites, spriteAsciiMap