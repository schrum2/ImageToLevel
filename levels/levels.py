from PIL import Image

import argparse
import json
import os
import pprint

import generators
import formats
import repair

# Added
import Visualize
import Inputs

# Read the arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument("image", help="Filename of the input RGB image in 'data/imgs/'")
parser.add_argument("game", help="Filename of the game JSON found in 'data/games/'")
parser.add_argument("generator", help="The name of the generator function")
parser.add_argument("repair", help="The name of the repair function")
parser.add_argument("width", help="Width of the output level")
parser.add_argument("height", help="Height of the output level")

parser.add_argument("-og", "--output_gen", help="Filename for generator .txt output")
parser.add_argument("-or", "--output_rep", help="Filename for generator + repair .txt output")
args = parser.parse_args()

# Load the input image
image_dir = "data/imgs/"
image_name = args.image
image_path = image_dir + image_name
if not os.path.isfile(image_path):
    raise IOError(f"{image_name} does not exist -- check the '{image_dir}' directory?")
image = Image.open(image_path)

# Load the game JSON
game_dir = "data/games/"
game_name = args.game
game_path = game_dir + game_name
if not os.path.isfile(game_path):
    raise IOError(f"{game_name} does not exist -- check the '{game_dir}' directory?")
with open(game_path) as json_file:
    game = json.load(json_file)

# Generate the level using the image and game data
generator = getattr(generators, args.generator)
pre_level = generator(image, game, int(args.width), int(args.height))

# Repair the level using the image and game data
repair = getattr(repair, args.repair)
post_level = repair(pre_level, game, int(args.width), int(args.height))

# Write the generator level to an output .txt file if necessary
if args.output_gen:
    formats.write_level(args.output_gen, pre_level)

# Write the generator + repair level to an output .txt file if necessary
if args.output_rep:
    formats.write_level(args.output_rep, post_level)

# Write to STDOUT if no output file found
if not args.output_gen and not args.output_rep:
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(post_level)

# Added code to output image
# Locations and Methods:
dataLocation = "./data/games/"
gameOptions = sorted(os.listdir(dataLocation))
print(gameOptions)
selectedGame = gameOptions[1]

pixelSize = 16

#asciiLevels, sprites, spriteAsciiMap = Inputs.Get_All_Inputs(dataLocation, selectedGame)
asciiLevelsSMB2, spritesSMB2, spriteAsciiMapSMB2 = Inputs.Get_All_Inputs(dataLocation, "super-mario-bros-simplified")


generatedImage = Visualize.visualize(post_level, spritesSMB2, spriteAsciiMapSMB2, pixelSize)
generatedImage.save("b_Generated.png", "PNG")