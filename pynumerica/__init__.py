# -*- coding: utf-8 -*-
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

from collections import OrderedDict
from datetime import datetime
import logging
import os

from osgeo import gdal, ogr, osr
from six import StringIO

import click

__version__ = '0.1.0'

LOGGER = logging.getLogger(__name__)


class Numerica(object):
    """MSC URP Numerica object model"""

    def __init__(self, ioobj=None, filename=None):
        """
        Initialize a Numerica object

        :param iooobj: file or StringIO object
        :param filename: filename (optional)

        :returns: pynumerica.Numerica instance
        """

        self.filename = filename
        """filename (optional)"""

        self.metadata = OrderedDict()
        """metadata fields"""

        self.data = []
        """data fields"""

        if filename is not None:
            self.filename = os.path.basename(filename)

        filelines = ioobj.readlines()

        LOGGER.debug('Detecting if file is a Numerica file')
        is_numerica = [s for s in filelines if 'MajorProductType RADAR' in s]
        if not is_numerica:
            raise InvalidDataError('Unable to detect Numerica format')

        LOGGER.debug('Parsing lines')
        for line in filelines:
            try:
                key, value = [s.strip() for s in line.split(' ', 1)]
            except ValueError:
                LOGGER.error('Malformed line: {}'.format(line))
            if key in ['Width', 'Height', 'HornHeight', 'GroundHeight']:
                LOGGER.debug('Casting {} as int'.format(value))
                self.metadata[key] = int(value)
            elif key in ['LatCentre', 'LonCentre', 'LatitudeIncrement',
                         'LongitudeIncrement']:
                LOGGER.debug('Casting {} as float'.format(value))
                self.metadata[key] = float(value)
            elif key == 'ValidTime':
                LOGGER.debug('Casting {} as datetime'.format(value))
                self.metadata[key] = datetime.strptime(value, '%Y%m%d%H%M')
            elif key == 'Data':  # split into list of tuples (lat, long, value)
                LOGGER.debug('Parsing data values')
                n = 3
                v = value.split(',')
                data = [','.join(v[i:i+n]) for i in range(0, len(v), n)]

                for d in data:
                    self.data.append([float(i) for i in d.split(',')])
            else:
                LOGGER.debug('Casting {} as string'.format(value))
                self.metadata[key] = value

    def get_data_spatial_extent(self):
        """returns tuple of minx, miny, maxx, maxy"""

        latitudes = sorted([i[0] for i in self.data])
        longitudes = sorted([i[1] for i in self.data])

        return (longitudes[0], latitudes[0], longitudes[-1], latitudes[-1])

    def get_data_range(self):
        """returns tuple min/max of data values"""

        data_values = sorted([i[2] for i in self.data])

        return (data_values[0], data_values[-1])

    def to_grid(self, filename='out.tif', fmt='GTiff'):
        """
        transform numerica data into raster grid

        :param filename: filename of output file
        :param fmt: file format.  Supported are any of the supported GDAL
                    Raster Format Codes (http://www.gdal.org/formats_list.html)

        :returns: boolean (file saved on disk)
        """

        LOGGER.debug('Creating OGR vector layer in memory')
        vsource = ogr.GetDriverByName('MEMORY').CreateDataSource('memory')

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        vlayer = vsource.CreateLayer('memory', srs, ogr.wkbPoint)

        vlayer.CreateField(ogr.FieldDefn('value', ogr.OFTReal))

        for d in self.data:
            vfeature = ogr.Feature(vlayer.GetLayerDefn())
            vfeature.SetField('value', d[2])

            # create the WKT for the feature using Python string formatting
            wkt = 'POINT(%f %f)' % (d[1], d[0])

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            vfeature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            vlayer.CreateFeature(vfeature)
            # Dereference the feature
            vfeature = None

        LOGGER.debug('Creating GDAL raster layer')
        width = self.metadata['Width']
        height = self.metadata['Height']
        resx = self.metadata['LongitudeIncrement']
        resy = self.metadata['LatitudeIncrement']

        minx = ((self.metadata['LonCentre'] - resx * (width / 2)) - (resx / 2))

        maxy = ((self.metadata['LatCentre'] + resy * (height / 2)) -
                (resy / 2))

        dsource = gdal.GetDriverByName(fmt).Create(filename, width, height,
                                                   1, gdal.GDT_Float64)

        dsource.SetProjection(srs.ExportToWkt())

        dsource.SetGeoTransform((minx, resx, 0.0, maxy, 0.0, -resy))
        dband = dsource.GetRasterBand(1)
        dband.SetNoDataValue(-9999)

        LOGGER.debug('Rastering virtual vector data')
        gdal.RasterizeLayer(dsource, [1], vlayer, options=['ATTRIBUTE=value'])
        LOGGER.info('Filename {} saved to disk'.format(filename))

        LOGGER.debug('Freeing data sources')
        vsource = None
        dsource = None

        return True


class InvalidDataError(Exception):
    """Exception stub for format reading errors"""
    pass


def load(filename):
    """
    Parse Numerica data from from file
    :param filename: filename
    :returns: pynumerica.Numerica object
    """

    with open(filename) as ff:
        return Numerica(ff, filename=filename)


def loads(strbuf):
    """
    Parse Numerica data from string
    :param strbuf: string representation of Numerica data
    :returns: pynumerica.Numerica object
    """

    s = StringIO(strbuf)
    return Numerica(s)


@click.command()
@click.version_option(version=__version__)
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to Numerica data file')
@click.option('--verbosity', type=click.Choice(['ERROR', 'WARNING',
              'INFO', 'DEBUG']), help='Verbosity')
def numerica_info(file_, verbosity):
    """parse Numerica data files"""

    if verbosity is not None:
        logging.basicConfig(level=getattr(logging, verbosity))

    if file_ is None:
        raise click.ClickException('Missing --file argument')

    with open(file_) as fh:
        try:
            n = Numerica(fh, filename=file_)
            click.echo('Numerica file: {}\n'.format(n.filename))
            click.echo('Metadata:')
            for key, value in n.metadata.items():
                click.echo(' {}: {}'.format(key, value))
            click.echo('\nData:')
            click.echo(' Number of records: {}'.format(len(n.data)))
            click.echo(' Spatial Extent: {}'.format(
                n.get_data_spatial_extent()))
            data_range = n.get_data_range()
            click.echo(' Range of Values: min={} - max={}'.format(
                data_range[0], data_range[1]))
        except Exception as err:
            raise click.ClickException(str(err))
