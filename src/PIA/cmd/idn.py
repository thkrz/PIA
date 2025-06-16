#!/usr/bin/python3
import numpy as np
import rasterio
import sys


def main():
    assert len(sys.argv) > 1
    bounds = []
    for f in sys.argv[1:]:
        with rasterio.open(f) as src:
            bounds.append(src.bounds)
    bounds = np.array(bounds)
    l, b = bounds[:, :2].max(axis=0)
    r, t = bounds[:, 2:].min(axis=0)
    print(l, b, r, t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
