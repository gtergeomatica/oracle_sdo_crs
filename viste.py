#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt
import subprocess
from subprocess import *

#import osr
#from osgeo import osr

from pyproj import CRS
from pyproj import Transformer

import cx_Oracle

#libreria per gestione log
import logging

from impostazione_base import *

from credenziali import *

#exit()
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode ='w',
    filename='{}/log/{}_{}_conversione_oracle_viste_19.log'.format(spath, date_file, user),
    level=logging.DEBUG)


# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(user,pwd,host,service)
con = cx_Oracle.connect(parametri_con)
logging.info("Versione ORACLE: {}".format(con.version))

# cur = con.cursor()
# # Cerco le viste con CRS Roma40 - GB F. Ovest dell'utente in questione
# query='''SELECT a.TABLE_NAME, b.* FROM mdsys.USER_SDO_GEOM_METADATA a,
# TABLE(a.DIMINFO) b, USER_VIEWS c 
# WHERE  a.TABLE_NAME=c.VIEW_NAME
# AND (srid = 3003 OR srid=82087) AND SDO_DIMNAME IS NOT null 
# order by TABLE_NAME, SDO_DIMNAME'''
# logging.debug(query)
# cur.execute(query)

# per le viste materializzate dice Cristina di stare attenti perchè forse è necessario 
# come primo step rimuovere l'indice spaziale per poi ricrearlo

cur0 = con.cursor()
query='''SELECT a.TABLE_NAME, count(b.SDO_DIMNAME) , 'v' AS tipo
FROM mdsys.USER_SDO_GEOM_METADATA a,
TABLE(a.DIMINFO) b, USER_VIEWS c 
WHERE  a.TABLE_NAME=c.VIEW_NAME
AND (srid = 3003 OR srid=82087) AND SDO_DIMNAME IS NOT null  
GROUP BY TABLE_NAME
UNION
SELECT a.TABLE_NAME, count(b.SDO_DIMNAME) , 'mv' AS tipo
FROM mdsys.USER_SDO_GEOM_METADATA a,
TABLE(a.DIMINFO) b, USER_MVIEWS c 
WHERE  a.TABLE_NAME=c.MVIEW_NAME
AND (srid = 3003 OR srid=82087) AND SDO_DIMNAME IS NOT null  
GROUP BY TABLE_NAME'''

logging.debug(query)
cur0.execute(query)

for vv in cur0: 
    if vv[2] =='v':
        logging.debug('Sto analizzando la vista {}'.format(vv[0]))
        query1='''SELECT a.TABLE_NAME, b.*, a.COLUMN_NAME
            FROM mdsys.USER_SDO_GEOM_METADATA a,
            TABLE(a.DIMINFO) b, USER_VIEWS c 
            WHERE  a.TABLE_NAME=c.VIEW_NAME
            AND SDO_DIMNAME IS NOT null 
            AND a.TABLE_NAME='{}' '''.format(vv[0])
    elif vv[2]=='mv':
        logging.debug('Sto analizzando la vista materializzata {}'.format(vv[0]))
        # DROP INDEX
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Rimuovo indice spaziale per evitare che ci sia un qualche problema che dia fastidio nei passi seguenti
        cur_a = con.cursor()
        spatial_index='''DROP INDEX {0}_SDX'''.format(vv[0])
        logging.debug(spatial_index)
        try:
            cur_a.execute(spatial_index)
            logging.debug('Rimosso indice spaziale per vista materializzata {}'.format(vv[0]))
        except Exception as e:
            logging.warning(e)
        cur_a.close()

        # refresh vista materializzata 
        query_r='''BEGIN DBMS_SNAPSHOT.REFRESH( '"{}"."{}"','C'); end;'''.format(user,vv[0])
        cur_r = con.cursor()
        logging.debug(query_r)
        try:
            cur_r.execute(query_r)
        except Exception as e:
            logging.error('''Problema con il refresh della vista materializzata {}. Errore {}'''.format(vv[0],e))
            continue
        cur_r.close()    
        
        query1='''SELECT a.TABLE_NAME, b.*, a.COLUMN_NAME
            FROM mdsys.USER_SDO_GEOM_METADATA a,
            TABLE(a.DIMINFO) b, USER_MVIEWS c 
            WHERE  a.TABLE_NAME=c.MVIEW_NAME
            AND SDO_DIMNAME IS NOT null 
            AND a.TABLE_NAME='{}' '''.format(vv[0])
    cur = con.cursor()
    logging.debug(query1)
    try:
        cur.execute(query1)
    except Exception as e:
        logging.error('''Problema con la vista {}. Errore {}'''.format(vv[0],e))
        continue
    #print(vv[0])
    #lb=[]
    for result in cur:
        #check_z=0
        if result[1]=='X':
            #view_x=result[0]
            #geom_name=result[]
            minx=result[2]
            maxx=result[3]
            column_name=result[5]
        elif result[1]=='Y':
            #view_y=result[0]
            miny=result[2]
            maxy=result[3]
        elif result[1]=='Z':
            #view_z=result[0]
            minz=result[2]
            maxz=result[3]
    cur.close()
    
    # questa query non va bene perchè non è detto che tutte 
    # le viste abbiano la colonna
    # GEOMETRY 
    # prima di lanciarla bisognerebbe cercare di recuperare il nome della 
    # colonna geometry
    
    
    query_srid = '''SELECT (SDO_GEOM.SDO_MBR({2}).SDO_SRID) AS SRID 
        FROM {0}.{1}
        GROUP BY SDO_GEOM.SDO_MBR({2}).SDO_SRID'''.format(user,vv[0],column_name)
    #print(query_srid)
    logging.debug(query_srid)
    cur1 = con.cursor()
    try:
        cur1.execute(query_srid)
    except Exception as e:
        logging.error('''Problema con la vista {}. Errore {}'''.format(vv[0],e))
        continue
    for result1 in cur1:
        check_srid=result1[0]
    cur1.close()
    logging.info('Il SRID stimato della vista e {}'.format(check_srid))
    if check_srid ==7791:
        logging.info('Faccio la riproiezione')
        # questa parte commentata usava la libreria GDAL ma in maniera erronea 
        # sia perchè l'installazione è più complessa
        # sia perchè la libreria deputata alla gestione delle trasformazioni fra CRS è proj --> pyproj
        #newspatialRef = osr.SpatialReference()
        #newspatialRef.ImportFromEPSG(7791)
        #oldspatialRef = osr.SpatialReference()
        #oldspatialRef.ImportFromEPSG(3003)
        #oldspatialRef.ImportFromProj4("+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs".format(qgis_path))
        #ct_3003_to_7791 = osr.CoordinateTransformation(oldspatialRef, newspatialRef)
        #print(vv[0])
        #new_minx, new_miny , z= ct_3003_to_7791.TransformPoint(minx, miny)
        #new_maxx, new_maxy , z= ct_3003_to_7791.TransformPoint(maxx, maxy)
        
        # uso della libreria pyproj
        new_crs = CRS.from_epsg(7791)
        old_crs = CRS.from_proj4("+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs".format(qgis_path))

        transformer = Transformer.from_crs(old_crs, new_crs, always_xy=True)

        new_minx, new_miny = transformer.transform(minx, miny)
        new_maxx, new_maxy = transformer.transform(maxx, maxy)
        
        # rimozione DB vecchi metadati
        query_delete='''DELETE FROM user_sdo_geom_metadata
        WHERE table_name='{}' '''.format(vv[0])
        logging.debug(query_delete)
        cur1 = con.cursor()
        try: 
            cur1.execute(query_delete)
            con.commit()
        except Exception as e:
            logging.error(e)
        cur1.close()
        # insert su DB nuovi metadati
        if vv[1]==2:
            query_insert=''' insert into user_sdo_geom_metadata 
            (table_name,column_name,diminfo,srid) values
            ('{0}','{1}', 
            sdo_dim_array(sdo_dim_element('X',{2},{3},0.005),
            sdo_dim_element('Y',{4},{5},0.005)),
            7791)'''.format(vv[0], column_name, new_minx, new_maxx, new_miny, new_maxy)
        elif vv[1]==3:
            query_insert=''' insert into user_sdo_geom_metadata 
            (table_name,column_name,diminfo,srid) values
            ('{0}','{1}', 
            sdo_dim_array(sdo_dim_element('X',{2},{3},0.005),
            sdo_dim_element('Y',{4},{5},0.005),sdo_dim_element('Z',{6},{7},0.005) ),
            7791)'''.format(vv[0], column_name, new_minx, new_maxx, new_miny, new_maxy, minz, maxz)
        else:
            logging.error('Problema nei metadati')
            continue
        cur1 = con.cursor()
        try: 
            cur1.execute(query_insert)
            con.commit()
        except Exception as e:
            logging.error(e)
        cur1.close()
        # ricreare metadati spaziali


        
    else:
        logging.info('Non faccio nulla')           



logging.info("Finito ciclo su viste e/o viste materializzate da convertire. Chiusura connessione al DB in corso")
cur0.close()
con.close()