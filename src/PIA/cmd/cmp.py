import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from imreflib import color


def main():
    with Image.open("ref.ppm") as image:
        a = np.array(image)
    with Image.open("class.pgm") as image:
        b = np.array(image)
    colors = color.loadtxt("colors.txt")
    palette = np.vstack(([255, 255, 255], colors))
    fig, axs = plt.subplots(1, 2, sharex=True, sharey=True, constrained_layout=True)
    axs[0].axis("off")
    axs[0].imshow(a)
    axs[1].axis("off")
    axs[1].imshow(palette[b])
    plt.show()
    return 0
