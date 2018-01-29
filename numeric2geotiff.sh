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
elif [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input file> <outputdir>"
    exit 1
fi

mkdir -p $2
bn=`basename $1`
pynumeric export -f "$1" -o "$2/$bn.tif" -of GTiff