#!/usr/bin/env python
import os,sys
import cx_Oracle
import datetime

date_file = datetime.datetime.now().strftime("%Y%m%d%H%M")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
#VISUALSTUDIO
spath=os.path.dirname(os.path.realpath(__file__))
print('Ok 1')#
#print(spath)

#QGIS 
#spath=r'C:\Users\roberto.marzocchi\OneDrive\Documenti\GitHub\oracle_sdo_crs'
#spath='C:/Users/roberto.marzocchi/Documents/GitHub/oracle_sdo_crs/'


#da toglere commento e modificare su QGIS
#sys.path.insert(0, r'C:\Users\assis\OneDrive\Documenti\GitHub\oracle_sdo_crs')

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS

#VISUALSTUDIO
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_9")

# QGIS
#cx_Oracle.init_oracle_client()

#cartella dove è installato QGIS
qgis_path="C:\OSGeo4W64"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#specifico i tipi geometrici supportati da ogr2ogr
n_type=[0,1,2,3,4,5,6,7]
type=['UNKNOWN','POINT', 'LINESTRING', 'POLYGON', 'GEOMETRYCOLLECTION', 'MULTIPOINT', 'MULTILINESTRING','MULTIPOLYGON']
# differenziare type per spatial index LINESTRING --> LINE (uguale per il multiline)
si_type=['UNKNOWN','POINT', 'LINE', 'POLYGON', 'GEOMETRYCOLLECTION', 'MULTIPOINT', 'MULTILINE','MULTIPOLYGON']
