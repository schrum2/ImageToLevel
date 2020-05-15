import os
import json
import glob
import pickle
import cv2
from PIL import Image

import Inputs
import RepairMC
import RepairAE
import EvaluateMC
import EvaluatePixel
import Visualize
import PixelGen
import CNNGen


# Inputs ================================================================================
# Actual image(s):
imageName = "TestImg"
imageFile = imageName+".jpeg"
inputImage_pil = Image.open(imageFile)
inputImage_cv = cv2.imread(imageFile)

w,h = inputImage_pil.size

pixelSize = 16

# for now it streches or contracts image but maybe cropping would be better or should have an option for either
outputLevelWidth = w//pixelSize
outputLevelHeight = h//pixelSize
outputLevelWidth = 202
outputLevelHeight = 14

dsize = (pixelSize*outputLevelWidth, pixelSize*outputLevelHeight)
inputImage_pil = inputImage_pil.resize(dsize)
inputImage_cv = cv2.resize(inputImage_cv, dsize)
inputImage_pil.save("./output_images_and_levels/a-originalImage.jpeg", "JPEG")

# Locations and Methods:
dataLocation = "./data/games/"
gameOptions = sorted(os.listdir(dataLocation))
generateMethods = ['CNN', 'Pixel']
repairMethods = ['AutoEncoder', 'MarkovChain']
pixelMethods = ['img', 'histogram']
MCMethods = ["NSEW", "NS", "EW"]
# TODO: May be some other hyperparameters we want to set here

#user Input
selectedGame = gameOptions[1]
selectedGenMethod = generateMethods[1]
selectedRepairMethod = repairMethods[1]

selectedPixelMethods = pixelMethods[1]
selectedMCMethod = MCMethods[0]

# Game data and game pretrained models (should be files):
trainModels = False
asciiLevels, sprites, spriteAsciiMap = Inputs.Get_All_Inputs(dataLocation, selectedGame)
trainedModelLocations = dataLocation + selectedGame + "/trainedModels/"
trainedMarkovChain = trainedModelLocations + "smbprobabilities"
trainedCNN = trainedModelLocations + "cnn_model"
patch_width = 20
patch_height = 14 # Anything other than 14 will need a new stiching method for the CNN
CNN_epochs = 20
CNN_batch = 16
trainedAutoEncoder = []
tempFileLocation = "./Temp_for_AE/"

if(trainModels):
    for m in MCMethods:
        RepairMC.train_MC(asciiLevels, m, trainedMarkovChain)
    CNNGen.train_model(asciiLevels, pixelSize, sprites, spriteAsciiMap, trainedCNN, CNN_epochs, CNN_batch, patch_width, patch_height)

# The MC for eval, not for the repair
markovProbabilitiesNSEW = pickle.load(open(trainedMarkovChain + MCMethods[0] + ".pickle", "rb"))

# Generate the level from the images======================================================
# inputImage => generatedLevel
generatedLevel = []
if(selectedGenMethod == 'CNN'):
    generatedLevel = CNNGen.generate(inputImage_cv, pixelSize, spriteAsciiMap, trainedCNN, patch_width, patch_height)

if(selectedGenMethod == 'Pixel'):
    generatedLevel = PixelGen.generate(inputImage_cv, sprites, spriteAsciiMap, pixelSize, selectedPixelMethods)
    
# Evaluation 1 ===========================================================================
# generatedLevel => (values)
generatedImage = Visualize.visualize(generatedLevel, sprites, spriteAsciiMap)
generatedImage.save("./output_images_and_levels/b-generatedLevel.jpeg", "JPEG")
consistencyGen = EvaluateMC.evaluate(generatedLevel, markovProbabilitiesNSEW, MCMethods[0])
closenessGen = EvaluatePixel.evaluate(inputImage_pil, generatedImage)

# Repair the levels ======================================================================
# generatedLevel => repairedLevel
repairedLevel = []
if(selectedRepairMethod == 'AutoEncoder'):
    repairedLevel = RepairAE.Repair(generatedLevel, tempFileLocation, imageName, spriteAsciiMap)

if(selectedRepairMethod == 'MarkovChain'):
    repairedLevel = RepairMC.Repair(generatedLevel, trainedMarkovChain, selectedMCMethod)

# Evaluation 2 ===========================================================================
# repairedLevel => (values)
repairedImage = Visualize.visualize(repairedLevel, sprites, spriteAsciiMap)
repairedImage.save("./output_images_and_levels/c-repairedImage.jpeg", "JPEG")
consistencyRepair = EvaluateMC.evaluate(repairedLevel, markovProbabilitiesNSEW, MCMethods[0])
closenessRepair = EvaluatePixel.evaluate(inputImage_pil, repairedImage)

# Plotting ===============================================================================
print("Conisitency After Gen: " + str(consistencyGen))
print("Conisitency After Repair: " + str(consistencyRepair))
print("Closeness After Gen: " + str(closenessGen))
print("Closeness After Repair: " + str(closenessRepair))