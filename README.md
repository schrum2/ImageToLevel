# levels
Turning images into 2-D video game levels

## Jacob's instructions

Go to the `Main` directory and run:
```
python Main_Single.py <input.png> <out_dir>
```

For example,
```
python Main_Single.py dalle1.png dalle1_test
```

## HTML Server
Quick manual setup of server (Not necessary to run the code. Skip ahead to run from command line)

```
npm run build

tmux new -s python-server
<goto /server>
python3 flask-server.py
<press ctrl-b-d>

tmux new -s http-server
<goto /dist>
http-server -c-1 -p 80
<press ctrl-b-d>
```

## Installation

(These are the original instructions. See my additional notes below)

```
git clone git@github.com:mattgallivan/levels.git
cd levels
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

From Jacob: I specifically used Python 3.7.11 (I made an Anaconda environment). The original requirements file tries to use a version of Pytorch that is no longer availble. Therefore, after the standard pip-install, you will need to install the old version of Pytorch using this command:

```
pip install torch==1.7.0+cpu torchvision==0.8.1+cpu torchaudio===0.7.0 -f https://download.pytorch.org/whl/torch_stable.html
```

This is specifically the CPU version (not CUDA).

## Basic Example

Basic example that creates a level based on a poor drawing. However, if does not apply any kind of repair, and thus seems to not produce a great output.

```
python levels/levels.py eugene-bad-drawing.png super-mario-bros-simplified/gameMetadata.json random nothing 16 11
```

## Usage Details
```
usage: levels.py [-h] [-og OUTPUT_GEN] [-or OUTPUT_REP] image game generator repair width height

positional arguments:
  image                 Filename of the input RGB image in 'data/imgs/'
  game                  Filename of the game JSON found in 'data/games/'
  generator             The name of the generator function
  repair                The name of the repair function
  width                 Width of the output level
  height                Height of the output level

optional arguments:
  -h, --help            show this help message and exit
  -og OUTPUT_GEN, --output_gen OUTPUT_GEN
                        Filename for generator .txt output
  -or OUTPUT_REP, --output_rep OUTPUT_REP
                        Filename for generator + repair .txt output
```

## How do I write a generator?

Add a function inside generators.py with the following format:

```
def generator_name_here(image, game, width, height):
    ...
```

where image is a PIL image of the input, game is the game's JSON file, and width and height
are the desired width and height of the output level.

## How do I write a repair?

Add a function inside repair.py with the following format:

```
def repair_name_here(level, game, width, height):
    # ...
```

where level is a 2D matrix of the input level and game is the game's JSON file.

## How do I install a library?

```
pip install library_name
pip freeze > requirements.txt
```
