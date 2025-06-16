import argparse
import numpy as np
from PIL import Image
from pathlib import Path

from imreflib import color, read_info

parser = argparse.ArgumentParser(description="Classify image.")
parser.add_argument("--eps", type=float, help="maximum color distance", default=0)
parser.add_argument(
    "--no-fill", action="store_true", help="disable interpolation of missing values"
)
args = parser.parse_args()


def clip():
    with Image.open("mask.pbm") as mask:
        dst = Image.new("RGB", mask.size, (255, 255, 255))
        with Image.open("ref.ppm") as src:
            comp = Image.composite(src, dst, mask)
            comp.save("clean.ppm")


def main():
    p = Path("clean.ppm")
    if not p.exists():
        clip()
    with Image.open(p) as image:
        im = np.array(image)
    colors = color.loadtxt("colors.txt")
    info = read_info()
    eps = args.eps if args.eps > 0.01 else float(info["COLOR_EPS"])
    IM, _ = color.quantize(im, colors, threshold=eps)
    if not args.no_fill:
        with Image.open("mask.pbm") as image:
            mask = np.array(image).astype(bool)
        IM = color.fill(IM, mask=mask)
        IM[~mask] = 0
    Image.fromarray(IM, mode="L").save("class.pgm")
    return 0
