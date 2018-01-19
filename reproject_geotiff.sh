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

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input file (GeoTIFF)> <outputdir-GeoTIFF-Reprojected>"
    exit 1
fi

SRS=epsg:4326
# # Values for all radars except Guam
EXTENT="-170.3238550 16.9346100 -50.0028550 67.1906100"
WIDTH=6525
HEIGHT=5584
## Values for Canadian radars only
# EXTENT="-126.6009205 41.2104430 -50.0066585 57.8493430"
# WIDTH=5938
# HEIGHT=1850
# # Values for Canadian radars + US border radars
#EXTENT="-126.6009205 37.2573430 -49.9977505 57.8493430"
#WIDTH=6027
#HEIGHT=2288

mkdir -p $2

bn=`basename $1`
file_="$1/$bn.tif"
fileout_="$2/$bn.tif_reprojected.tif"
gdalwarp -t_srs $SRS -te $EXTENT -ts $WIDTH $HEIGHT -srcnodata None $1 $fileout_