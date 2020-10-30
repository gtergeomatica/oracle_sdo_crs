#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt
import cx_Oracle

#libreria per gestione log
import logging


spath=os.path.dirname(os.path.realpath(__file__))
#exit()
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode ='w',
    #filename='{}/log/conversione_oracle_19.log'.format(spath),
    level=logging.DEBUG)


#da toglere commento e modificare su QGIS
#sys.path.insert(0, r'C:\Users\assis\Documents\GitHub\oracle_sdo_crs')
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
con = cx_Oracle.connect(parametri_con)
logging.info("Versione ORACLE: {}".format(con.version))


# DEBUG VISTE (if debug_viste=0 non fa nulla sulle viste (PER ORA TEST))
debug_viste=1

# DEBUG - solo nella fase di debug dello script
# ricreo la condizione iniziale sulle tabelle convertite 
debug=1
if debug==1: 
    query_debug='''SELECT TABLE_NAME FROM ALL_ALL_TABLES 
        WHERE OWNER LIKE upper('{}') 
        AND TABLE_NAME LIKE '%_CSG' ORDER BY TABLE_NAME'''.format(user)
    cur0 = con.cursor()
    logging.debug(query_debug)
    cur0.execute(query_debug)
    for result in cur0:
        logging.debug('Altero tabella {}'.format(result[0]))   
        table_original_name=result[0].replace('_CSG','')
        query1='ALTER TABLE {0}.{1} RENAME TO "{1}_7791"'.format (user,table_original_name)
        #query1='DELETE TABLE {0}.{1};'.format (user,table_original_name)
        logging.debug(query1)
        cur1 = con.cursor()
        try:
            cur1.execute(query1)
            logging.debug('Rinominata tabella {}'.format(table_original_name))
        except Exception as e:
            logging.error(e)
        cur1.close()
        query2='ALTER TABLE {0}.{1}_CSG RENAME TO "{1}"'.format (user,table_original_name)
        logging.debug(query2)
        cur1 = con.cursor()
        try:
            cur1.execute(query2)
            logging.debug('Rinominata tabella {}_CSG'.format(table_original_name))
        except Exception as e:
            logging.error(e)
        cur1.close()
        query3='DELETE TABLE {0}.{1}_7791'.format (user,table_original_name)
        logging.debug(query3)
        cur1 = con.cursor()
        try:
            cur1.execute(query3)
            logging.debug('Rimossa la tabella {}_7791'.format(table_original_name))
        except Exception as e:
            logging.error(e)
        cur1.close()
    cur0.close()
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Aggiorno i metadati spaziali
    
    #step 1 - rimuovo i metadati per la tabella originale
    metadati= ''' DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}' '''.format(table_name)
    cur_m=con.cursor()
    try:
        cur_m.execute(metadati)
        logging.debug('Step 1 metadati OK: Metadati tabella originale rimossi')
    except Exception as m:
        logging.warning('Metadati della tabella {} non rimossi. \n Errore: {}'.format(table_name, m))
    cur_m.close()
    
    
    
    # step 2 creo metadati per tabella originale con quelli della tabella _CSG
    metadati= ''' INSERT INTO user_sdo_geom_metadata 
                using SELECT '{0}', column_name, diminfo, srid 
                FROM user_sdo_geom_metadata WHERE table_name LIKE '{0}_CSG' '''.format(table_name)
    cur_m=con.cursor()
    try:
        cur_m.execute(metadati)
        logging.debug('Step 2 metadati OK')
    except Exception as m:
        logging.error('Metadati della tabella {}_CSG non creati. \n Errore: {}'.format(table_name, m))
    cur_m.close()
    
    
    