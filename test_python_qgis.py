#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis

'''
Script utile per testare lancio di script python da QGIS
'''
import os,sys,shutil,re,glob, getopt
import cx_Oracle


#libreria per gestione log
import logging

#QGIS
#sys.path.append('C:\\Users\\roberto.marzocchi\\OneDrive\\Documenti\\GitHub\\oracle_sdo_crs')
sys.path.append('C:/Users/roberto.marzocchi/Documents/GitHub/oracle_sdo_crs/')

print('Ok partiti!')


from impostazione_base import *

from credenziali import *

# inserire riferimento a data e schema
print('Ok 3')

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode ='w',
    filename='{}\log\{}_{}_test_QGIS.log'.format(spath, date_file, user),
    level=logging.DEBUG)





# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(user,pwd,host,service)
con = cx_Oracle.connect(parametri_con)
logging.info("Versione ORACLE: {}".format(con.version))


# DEBUG VISTE (if debug_viste=0 non fa nulla sulle viste (PER ORA TEST))
debug_viste=0




# STEP 0 - Pulizia USER_SDO_GEOM_METADATA
logging.info('Sto usando l\'utente {} sul DB cui si accede all\'host {} con il service {}'.format(user,host,service))