import os
import json
import glob
import pickle
import cv2
import shutil
import csv
from PIL import Image

import Inputs
import RepairMC
import RepairAE
import EvaluateMC
import EvaluatePixel
import EvaluateLevel
import Visualize
import PixelGen
import CNNGen

import sys

# Adding simple handling of command line parameters

print(sys.argv)
if len(sys.argv) < 3:
    print("Should be following:\npython Main_Custom.py <input.png> <out_dir>")
    quit()
# A PNG or other image file
input_file = sys.argv[1]
base_output_dir = sys.argv[2]

# Locations and Methods:
dataLocation = "./data/games/"
gameOptions = sorted(os.listdir(dataLocation))
print(gameOptions)
selectedGame = sys.argv[3] if len(sys.argv) == 4 else gameOptions[1]

generateMethods = ['Pixel']
#repairMethods = ['AutoEncoder', 'MarkovChain', 'Multi1']
pixelMethods = ['img', 'histogram', 'avrg']
#MCMethods = ["NSEW", "NS", "EW", "SW", "NE", "NW"]
pixelSize = 8 if selectedGame == "lode-runner-simplified" else 16

asciiLevels, sprites, spriteAsciiMap = Inputs.Get_All_Inputs(dataLocation, selectedGame)

imageFile = input_file
imageName = os.path.splitext(os.path.basename(imageFile))[0]
inputImage_pil = Image.open(imageFile)
inputImage_cv = cv2.imread(imageFile)

# for now it streches or contracts image but maybe cropping would be better or should have an option for either
w, h = inputImage_pil.size
# Hard coding this to match the output size of DALL-E images
outputLevelWidth = 32 if selectedGame == "lode-runner-simplified" else 16 
outputLevelHeight = 32 if selectedGame == "lode-runner-simplified" else 16

# Strech:
dsize = (pixelSize * outputLevelWidth, pixelSize * outputLevelHeight)
inputImage_pil = inputImage_pil.resize(dsize)
inputImage_cv = cv2.resize(inputImage_cv, dsize)

outputFolder = "./" + base_output_dir + "/" + imageName + "_to_" + selectedGame + "/"
if os.path.exists(outputFolder):
    shutil.rmtree(outputFolder)
os.makedirs(outputFolder)

for selectedGenMethod in generateMethods:
    if(selectedGenMethod == 'Pixel'):
        pixelMethodsList = pixelMethods
    else:
        pixelMethodsList = ['img']

    for selectedPixelMethod in pixelMethodsList:
        generatedLevel = []
        if(selectedGenMethod == 'Pixel'):
            generatedLevel = PixelGen.generate(inputImage_cv, sprites, spriteAsciiMap, pixelSize, selectedPixelMethod)

        methodInfoString = "Gen-" + selectedGenMethod + selectedPixelMethod
        processString = (outputFolder + methodInfoString)
        if not os.path.exists(processString):
            os.makedirs(processString)
        inputImage_pil.save(processString + "/" + "a_Original_Resized.png", "PNG")

        tileFileLocation = processString + "/" + "before_repair.txt"
        with open(tileFileLocation, 'w') as f:
            f.write("\n".join(map(lambda x : "".join(x), generatedLevel)))
        print(f"Save to {tileFileLocation}")

        # Evaluation 1 ===========================================================================
        # generatedLevel => (values)
        generatedImage = Visualize.visualize(generatedLevel, sprites, spriteAsciiMap, pixelSize)
        saveLocation = processString + "/" + "b_Generated.png"
        generatedImage.save(saveLocation, "PNG")
        print(f"Saved to {saveLocation}")
            
            