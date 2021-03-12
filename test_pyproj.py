#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt


from impostazione_base import *


from pyproj import CRS
from pyproj import Transformer




new_crs = CRS.from_epsg(7791)
old_crs = CRS.from_proj4("+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs".format(qgis_path))

transformer = Transformer.from_crs(old_crs, new_crs, always_xy=True)

x, y= transformer.transform(1475552.01, 4914239.88)

print(x)
print(y)
