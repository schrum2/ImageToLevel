import sys
import image_slicer

# run with
# python TilesFromImage.py <image.png> <total number of tiles>
# python TilesFromImage.py dalle1.png 256
# (the 256 is because they typically have 16 by 16 tiles)

image = sys.argv[1]
image_slicer.slice(image, int(sys.argv[2]))
