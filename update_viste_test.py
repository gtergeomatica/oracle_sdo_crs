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
    filename='{}/log/update_viste_test.log'.format(spath),
    level=logging.DEBUG)


#da toglere commento e modificare su QGIS
sys.path.insert(0, r'C:\Users\assis\Documents\GitHub\oracle_sdo_crs')
from credenziali import *


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PARTE UTILE PER LANCIARE LO SCRIPT DA QGIS o da python (es. VisualCode)
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_6")

# decommentare e modificare la seguente riga per lanciare lo script da QGIS
#cx_Oracle.init_oracle_client()

#cartella dove è installato QGIS
qgis_path="C:\OSGeo4W64"
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(user,pwd,host,service)
con_test = cx_Oracle.connect(parametri_con)

parametri_con='{}/{}@//{}/{}'.format(user,pwd,host_produzione,service_produzione)
con_prod = cx_Oracle.connect(parametri_con)

logging.info("Versione ORACLE Test: {}".format(con_test.version))

logging.info("Versione ORACLE Produzione: {}".format(con_prod.version))


curp = con_prod.cursor()
# Cerco le viste con CRS Roma40 - GB F. Ovest dell'utente in questione
query='''select VIEW_NAME,TEXT_VC FROM USER_VIEWS'''
logging.debug(query)
curp.execute(query)

vistep=[]
vistept=[]
vistepp= []

i=0
for vistap in curp:
    i+=1
    vistep.append(vistap[0])
    query1=''' SELECT VIEW_NAME,TEXT_VC FROM USER_VIEWS WHERE VIEW_NAME = '{}' '''.format(vistap[0])
    logging.info('{} - {}'.format(i,vistap[0]))
    curt=con_test.cursor()
    curt.execute(query1)
    check=0
    for vistat in curt:
        check=1
        logging.info('Vista trovata in test')
        if vistat[1]==vistap[1]:
            logging.info('Vista ok in test')
        else:
            logging.info('Le due viste sono differenti')
    if check==1:
        vistept.append(vistap[1])
        query_metadati='''SELECT * FROM mdsys.USER_SDO_GEOM_METADATA 
        WHERE TABLE_NAME='{}' '''.format(vistap[0])
        logging.debug(query_metadati)
        curp1=con_prod.cursor()
        curp1.execute(query_metadati)
        for mp in curp1:
            # cerco diminfo
            query_diminfo='''SELECT DISTINCT a.TABLE_NAME, b.* FROM mdsys.USER_SDO_GEOM_METADATA a,
            TABLE(a.DIMINFO) b, USER_VIEWS c 
            WHERE  a.TABLE_NAME= '{}' '''.format(vistap[0])
            logging.debug(query_diminfo)
            curp2=con_prod.cursor(query_diminfo)
            curp2.execute(query_diminfo)
            diminfo='sdo_dim_array('
            k=1
            for result in curp2:
                if result[1]!=None:
                    if k==1:
                        diminfo='''{}sdo_dim_element('{}',{},{},{})'''.format(diminfo,result[1],result[2],result[3],result[4])
                    else:
                        diminfo='''{} , sdo_dim_element('{}',{},{},{})'''.format(diminfo,result[1],result[2],result[3],result[4])
                    k+=1
            curp2.close()
            diminfo='''{})'''.format(diminfo)
            #logging.debug(diminfo)
            query_metadati1=''' INSERT INTO mdsys.USER_SDO_GEOM_METADATA
            (TABLE_NAME, COLUMN_NAME, DIMINFO, SRID) 
            VALUES ('{0}','{1}',{2}, {3})'''.format(mp[0],mp[1],diminfo,mp[3])
            logging.debug(query_metadati1)
            curt1=con_test.cursor()
            try:
                curt1.execute(query_metadati1)
                logging.info('Metadati inseriti')
                con_test.commit()
            except Exception as e:
                logging.error(e)
            curt1.close()
    else:
        logging.warning('Vista non trovata in test')
        vistepp.append(vistap[1])
    curt.close()
    curp1.close()
    