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
    print("Should be following:\npython Main_Single.py <input.png> <out_dir>")
    quit()
# A PNG or other image file
input_file = sys.argv[1]
base_output_dir = sys.argv[2]

# Locations and Methods:
dataLocation = "./data/games/"
gameOptions = sorted(os.listdir(dataLocation))
print(gameOptions)
selectedGame = gameOptions[1]

generateMethods = ['CNN', 'Pixel']
repairMethods = ['AutoEncoder', 'MarkovChain', 'Multi1']
pixelMethods = ['img', 'histogram', 'avrg']
MCMethods = ["NSEW", "NS", "EW", "SW", "NE", "NW"]
pixelSize = 16

# Training Models=========================================================================
# Training Info:
trainModels = False
asciiLevels, sprites, spriteAsciiMap = Inputs.Get_All_Inputs(dataLocation, selectedGame)
trainedModelLocations = dataLocation + selectedGame + "/trainedModels/"

# Hyperparameters
patch_width = 2
patch_height = 2  # Anything other than 2, 7, or 14 will need a new stiching method for the CNN
CNN_epochs = 50
CNN_batch = 16

# Trained Model Locations
trainedCNN = trainedModelLocations + "cnn_model" + "_" + str(patch_width) + "_" + str(patch_height) + ".pth"
trainedMarkovChain = trainedModelLocations + "smbprobabilities"
trainedEval = trainedModelLocations + "evalDictionary"
trainedAutoEncoder = trainedModelLocations + "ae_model" + ".pth"
tempFileLocation = "./Temp_for_AE/"
if os.path.exists(tempFileLocation):
    shutil.rmtree(tempFileLocation)
os.makedirs(tempFileLocation)

# Training Methods if required:
if(trainModels):
    CNNGen.train_model(asciiLevels, pixelSize, sprites, spriteAsciiMap, trainedCNN, CNN_epochs, CNN_batch, patch_width, patch_height)

for m in MCMethods:
    RepairMC.train_MC(asciiLevels, m, trainedMarkovChain)
EvaluateMC.trainEval(asciiLevels, trainedEval)

# Actual System=============================================================================
# Actual image(s):

#imageFile = "./green-hills-landscape.png"
#imageFile = "./dalle1.png"
imageFile = input_file
imageName = os.path.splitext(os.path.basename(imageFile))[0]
inputImage_pil = Image.open(imageFile)
inputImage_cv = cv2.imread(imageFile)

# for now it streches or contracts image but maybe cropping would be better or should have an option for either
w, h = inputImage_pil.size
#outputLevelWidth = w // pixelSize
#outputLevelHeight = h // pixelSize
# Hard coding this to match the output size of DALL-E images
outputLevelWidth = 16 #40
outputLevelHeight = 16 #14

# Strech:
dsize = (pixelSize * outputLevelWidth, pixelSize * outputLevelHeight)
inputImage_pil = inputImage_pil.resize(dsize)
inputImage_cv = cv2.resize(inputImage_cv, dsize)

# Crop:
#level_start = 50
#left, top, right, bottom = level_start, 0, level_start + outputLevelWidth, outputLevelHeight
#inputImage_pil = inputImage_pil.crop((pixelSize * left, pixelSize * top, pixelSize * right, pixelSize * bottom))
#inputImage_cv = inputImage_cv[0:0 + outputLevelHeight * pixelSize, level_start * pixelSize:level_start * pixelSize + outputLevelWidth * pixelSize]

outputFolder = "./" + base_output_dir + "/" + imageName + "_to_" + selectedGame + "/"
if os.path.exists(outputFolder):
    shutil.rmtree(outputFolder)
os.makedirs(outputFolder)
#EvalFile = open(outputFolder + "Evaluations.txt", "a+")
# user Input
# selectedGenMethod = generateMethods[1]
# selectedRepairMethod = repairMethods[1]
# selectedPixelMethod = pixelMethods[2]
selectedMCMethod = MCMethods[3]
for selectedGenMethod in generateMethods:
    if(selectedGenMethod == 'Pixel'):
        pixelMethodsList = pixelMethods
    else:
        pixelMethodsList = ['img']

    for selectedPixelMethod in pixelMethodsList:
        for selectedRepairMethod in repairMethods:
            methodInfoString = "Gen-" + selectedGenMethod + selectedPixelMethod + "_Rep-" + selectedRepairMethod
            processString = (outputFolder + methodInfoString)
            if not os.path.exists(processString):
                os.makedirs(processString)
            inputImage_pil.save(processString + "/" + "a_Original_Resized.png", "PNG")

            # Generate the level from the images======================================================
            # inputImage => generatedLevel
            generatedLevel = []
            if(selectedGenMethod == 'CNN'):
                generatedLevel = CNNGen.generate(inputImage_cv, pixelSize, spriteAsciiMap, trainedCNN, patch_width, patch_height)

            if(selectedGenMethod == 'Pixel'):
                generatedLevel = PixelGen.generate(inputImage_cv, sprites, spriteAsciiMap, pixelSize, selectedPixelMethod)

            # Evaluation 1 ===========================================================================
            # generatedLevel => (values)
            generatedImage = Visualize.visualize(generatedLevel, sprites, spriteAsciiMap, pixelSize)
            saveLocation = processString + "/" + "b_Generated.png"
            generatedImage.save(saveLocation, "PNG")
            print(f"Saved to {saveLocation}")
            consistencyGen = EvaluateMC.evaluate(generatedLevel, trainedEval)
            closenessGen = EvaluatePixel.evaluate(inputImage_pil, generatedImage)
            #levelCompareGen = EvaluateLevel.evaluate(testLevel, generatedLevel)

            # Repair the levels ======================================================================
            # generatedLevel => repairedLevel
            repairedLevel = generatedLevel
            if(selectedRepairMethod == 'AutoEncoder'):
                repairedLevel = RepairAE.Repair(repairedLevel, tempFileLocation, imageName, spriteAsciiMap)

            if(selectedRepairMethod == 'MarkovChain'):
                repairedLevel = RepairMC.Repair(repairedLevel, trainedMarkovChain, spriteAsciiMap, selectedMCMethod)

            if(selectedRepairMethod == 'Multi1'):
                repairedLevel = RepairAE.Repair(repairedLevel, tempFileLocation, imageName, spriteAsciiMap)
                repairedLevel = RepairMC.Repair(repairedLevel, trainedMarkovChain, spriteAsciiMap, selectedMCMethod)

            # Evaluation 2 ===========================================================================
            # repairedLevel => (values)
            repairedImage = Visualize.visualize(repairedLevel, sprites, spriteAsciiMap, pixelSize)
            repairedImage.save(processString + "/" + "c_Repaired.png", "PNG")
            consistencyRepair = EvaluateMC.evaluate(repairedLevel, trainedEval)
            closenessRepair = EvaluatePixel.evaluate(inputImage_pil, repairedImage)
            #levelCompareRepair = EvaluateLevel.evaluate(testLevel, repairedLevel)

            # Plotting ===============================================================================
            # print("Closeness After Gen: " + str(closenessGen))
            # print("Closeness After Repair: " + str(closenessRepair))
            # print("Conisitency After Gen: " + str(consistencyGen))
            # print("Conisitency After Repair: " + str(consistencyRepair))

            # EvalFile.write(methodInfoString + " Closeness After Gen: " + str(closenessGen) + "\n")
            # EvalFile.write(methodInfoString + " Closeness After Repair: " + str(closenessRepair) + "\n")
            # EvalFile.write(methodInfoString + " Conisitency After Gen: " + str(consistencyGen) + "\n")
            # EvalFile.write(methodInfoString + " Conisitency After Repair: " + str(consistencyRepair) + "\n")
            #EvalFile.write(methodInfoString + " LevelCheck After Gen: " + str(levelCompareGen) + "\n")
            #EvalFile.write(methodInfoString + " LevelCheck After Repair: " + str(levelCompareRepair) + "\n")
            #EvalFile.write("\n")

            # if not ("Closeness_" + methodInfoString) in stats.keys():
                # stats["Closeness_" + methodInfoString] = []
            # stats["Closeness_" + methodInfoString] += [closenessRepair]

            # if not ("Conisitency_" + methodInfoString) in stats.keys():
                # stats["Conisitency_" + methodInfoString] = []
            # stats["Conisitency_" + methodInfoString] += [consistencyRepair]

            #if not ("LevelCompare_" + methodInfoString) in stats.keys():
                #stats["LevelCompare_" + methodInfoString] = []
            #stats["LevelCompare_" + methodInfoString] += [levelCompareRepair]

#EvalFile.close()