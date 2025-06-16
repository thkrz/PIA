#!/usr/bin/python3
import numpy as np
import sys
from PIL import Image

from imreflib import color


def main():
    with Image.open("class.pgm") as image:
        b = np.array(image)
    colors = color.loadtxt("colors.txt")
    palette = np.vstack(([255, 255, 255], colors))
    arr = palette[b].astype(np.uint8)
    im = Image.fromarray(arr, mode="RGB")
    im.save("class.ppm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
