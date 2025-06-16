#!/usr/bin/python3
import numpy as np
import rasterio
import sys
from pathlib import Path


def _norm(arr):
    if arr.max() == 4:
        return arr
    arr[arr == 1] = 2
    arr[arr == 0] = 1
    arr -= 1
    return arr


def main():
    assert len(sys.argv) > 1
    mask = None
    for a in sys.argv[1:]:
        p = Path(a)
        t = p.name
        with rasterio.open(p) as src:
            arr = _norm(src.read(1))
            if mask is None:
                mask = arr > 0
            else:
                mask &= arr > 0
            with rasterio.open(t, "w", **src.profile) as dst:
                dst.write(arr, 1)
    np.save("point_mask.npy", mask.astype(bool))
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/python3
import rasterio
from rasterio.windows import get_data_window
import sys


def main():
    assert len(sys.argv) > 2
    a, b = sys.argv[1], sys.argv[2]
    with rasterio.open(a) as src:
        window = get_data_window(src.read(1, masked=True))
        kwargs = src.meta.copy()
        kwargs.update(
            {
                "height": window.height,
                "width": window.width,
                "transform": rasterio.windows.transform(window, src.transform),
            }
        )

        with rasterio.open(b, "w", **kwargs) as dst:
            dst.write(src.read(window=window))
    print(b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
