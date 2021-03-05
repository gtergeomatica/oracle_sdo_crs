#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt
import subprocess
from subprocess import *

#import osr

import cx_Oracle

#libreria per gestione log
import logging

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
spath=os.path.dirname(os.path.realpath(__file__))
#exit()
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode ='w',
    filename='{}/log/conversione_oracle_viste_19.log'.format(spath),
    level=logging.DEBUG)


#da toglere commento e modificare su QGIS
sys.path.insert(0, r'C:\Users\assis\Documents\GitHub\oracle_sdo_crs')
from credenziali import *


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_9")

# decommentare e modificare la seguente riga per lanciare lo script da QGIS
#cx_Oracle.init_oracle_client()

#cartella dove è installato QGIS
qgis_path="C:\OSGeo4W64"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(user,pwd,host,service)
con = cx_Oracle.connect(parametri_con)
logging.info("Versione ORACLE: {}".format(con.version))

cur = con.cursor()
# Cerco le viste con CRS Roma40 - GB F. Ovest dell'utente in questione
query='''SELECT a.TABLE_NAME, b.* FROM mdsys.USER_SDO_GEOM_METADATA a,
TABLE(a.DIMINFO) b, USER_VIEWS c 
WHERE  a.TABLE_NAME=c.VIEW_NAME
AND (srid = 3003 OR srid=82087) order by TABLE_NAME'''
logging.debug(query)
cur.execute(query)

# per le viste materializzate dice Cristina di stare attenti perchè forse è necessario 
# come primo step rimuovere l'indice spaziale per poi ricrearlo


lb=[]



# DA MODIFICARE PER IL CASO 3D (ripensare il ciclo) !!!! che in produzione ci sono anche i null (forse basta toglierli nel select precedente)


i=1
for result in cur:
    if result[1]=='X':
        view_x=result[0]
        geom_name=result[1]
        minx=result[2]
        maxx=result[3]
    elif result[1]=='Y':
        view_y=result[0]
        miny=result[2]
        maxy=result[3]
    elif result[1]=='Z':
        view_z=result[0]
        minz=result[2]
        maxz=result[3]

    if (view_x==view_y) OR ()):
        query_srid='''SELECT (SDO_GEOM.SDO_MBR(GEOMETRY).SDO_SRID) AS SRID 
        FROM {0}.{1}
        GROUP BY SDO_GEOM.SDO_MBR(GEOMETRY).SDO_SRID'''.format(user,result[0])
        cur1 = con.cursor()
        cur1.execute(query_srid)
        for result1 in cur1:
            check_srid=result1[0]
        cur1.close()
        logging.info('Il SRID stimato della vista è {}'.format(check_srid))
        if check_srid ==7791:
            newspatialRef = osr.SpatialReference()
            newspatialRef.ImportFromEPSG(7791)
            oldspatialRef = osr.SpatialReference()
            #oldspatialRef.ImportFromEPSG(3003)
            oldspatialRef.ImportFromProj4("+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs".format(qgis_path))
            ct_3003_to_7791 = osr.CoordinateTransformation(oldspatialRef, newspatialRef)
            print('ok')
            new_minx, new_miny , z= ct_3003_to_7791.TransformPoint(minx, miny)
            new_maxx, new_maxy , z= ct_3003_to_7791.TransformPoint(maxx, maxy)
            
            # rimozione DB vecchi metadati
            query_delete='''DELETE FROM user_sdo_geom_metadata
            WHERE table_name='{}';'''.format(view_x)
            cur1 = con.cursor()
            try: 
                cur1.execute(query_srid)
            except Exception as e:
                logging.error(e)
            cur1.close()
            # insert su DB nuovi metadati
            query_insert=''' insert into user_sdo_geom_metadata 
            (table_name,column_name,diminfo,srid) values
            ('{0}','{1}', 
            sdo_dim_array(sdo_dim_element('X',{2},{3},0.005),
            sdo_dim_element('Y',{4},{5},0.005)),
            7791)'''.format(view_x, geom_name, minx, maxx, miny, maxy)
            cur1 = con.cursor()
            try: 
                cur1.execute(query_insert)
                con.commit()
            except Exception as e:
                logging.error(e)
            cur1.close()
                
                
                
        else : 
            logging.info('Vista {} da non convertire'.format(result[0]))

    i+=1
