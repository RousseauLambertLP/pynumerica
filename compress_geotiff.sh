#!/bin/bash
# =================================================================
#
# Copyright (c) 2017 Government of Canada
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =================================================================


if [[ $1 == --version ]] || [[ $1 == -V ]]; then
    echo "Version 0.1"
    exit 1
elif [ "$#" -lt 3 ]; then
    echo "Usage: $0 <compression method (PACKBITS/DEFLATE/LZW)> <input file/folder> <outputdir>"
    exit 1
fi

mkdir -p $3

if [[ "$2" == *".tif" ]]; then
bn=`basename $2`
gdal_translate -of GTiff -co "COMPRESS=$1" -co "TILED=YES" $2 "$3/$bn-compress.tif"

else
TIFFFILES=$(find $2 -name "*.tif")
for files in $TIFFFILES
do
    bn=`basename $files`
    gdal_translate -of GTiff -co "COMPRESS=$1" -co "TILED=YES"  $files "$3/$bn-compress.tif"
done
fi