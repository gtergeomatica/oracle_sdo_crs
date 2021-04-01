#!/usr/bin/env python
import os,sys
import cx_Oracle
import datetime

date_file = datetime.datetime.now().strftime("%Y%m%d%H%M")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
spath=os.path.dirname(os.path.realpath(__file__))
#spath=r'C:\Users\assis\OneDrive\Documenti\GitHub\oracle_sdo_crs'


#da toglere commento e modificare su QGIS
#sys.path.insert(0, r'C:\Users\assis\OneDrive\Documenti\GitHub\oracle_sdo_crs')

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_9")

# decommentare e modificare la seguente riga per lanciare lo script da QGIS
#cx_Oracle.init_oracle_client()

#cartella dove è installato QGIS
qgis_path="C:\OSGeo4W64"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++