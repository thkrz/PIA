#!/bin/bash -e
findres() {
	python3 - <<EOF
import numpy as np

epsg = "$epsg"
ref_size = 5
arr = np.loadtxt("gcp.txt")
dpx = arr[-1, 0] - arr[0, 0]
x_max = arr[:, 2].max()
x_min = arr[:, 2].min()

if epsg.endswith("4326"):
  from pyproj import Geod
  geod = Geod(ellps="WGS84")
  y = arr[0, 3]
  _, _, dx = geod.inv(x_min, y, x_max, y)
else:
  dx = x_max - x_min
cx = dx / dpx
cx = max(ref_size, round(cx / ref_size) * ref_size)
print(cx, end="")
EOF
}

usage() {
	echo "usage: imwrap [-r epsg] [-n nodata] [-t target_epsg] [-s cell_size] [file]" >&2
	exit 1
}

t_epsg="EPSG:32639"
if [ -f info.txt ]; then
	epsg="EPSG:$(awk '/^EPSG/{printf "%d", $2}' info.txt)"
else
	epsg="EPSG:4326"
fi
tr=0
nodata=0
while getopts ":r:n:t:s:" arg; do
	case $arg in
	r)
		epsg="EPSG:${OPTARG}"
		;;
	n)
		nodata=$OPTARG
		;;
	s)
		tr=$OPTARG
		;;
	t)
		t_epsg=$OPTARG
		;;
	*)
		usage
		;;
	esac
done
shift $((OPTIND - 1))
if [ $tr -eq 0 ]; then
  tr=$(findres)
fi

cls=class.pgm
if [ -n "$1" ]; then
  cls=$1
fi

nam=$(basename "$PWD")
dst=${nam}.tif
gcp=$(sed ':a; N; $!ba; s/\n/ -gcp /g' gcp.txt)
gdal_translate \
	-a_srs $epsg \
	-a_nodata $nodata \
	-gcp $gcp \
	-of GTiff \
	$cls \
	temp.tif
gdalwarp -overwrite -of GTiff -tap -tr $tr $tr -t_srs $t_epsg \
  -r max \
  temp.tif temp2.tif && rm temp.tif
imtrim.py temp2.tif $dst && rm temp2.tif
# imtrim.py temp2.tif out.tif && rm temp2.tif

echo "CELL_SIZE: $tr, EPSG: $epsg"
