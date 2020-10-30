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
debug=0
if debug==1: 
    query_debug='''SELECT TABLE_NAME FROM ALL_ALL_TABLES 
        WHERE OWNER LIKE upper('{}') 
        AND TABLE_NAME LIKE '%_CSG' ORDER BY TABLE_NAME'''.format(user)
    cur0 = con.cursor()
    logging.debug(query_debug)
    cur0.execute(query_debug)
    for result in cur0:   
        table_original_name=result[0].replace('_CSG','')
        query1='ALTER TABLE {0}.{1} RENAME TO "{1}_7791";'.format (user,table_original_name)
        #query1='DELETE TABLE {0}.{1};'.format (user,table_original_name)
        cur1 = con.cursor()
        cur1.execute(query1)
        cur1.close()
        query2='ALTER TABLE {0}.{1}_CSG RENAME TO "{1}";'.format (user,table_original_name)
        cur1 = con.cursor()
        cur1.execute(query2)
        cur1.close()
        query3='DELETE TABLE {0}.{1};'.format (user,table_original_name)
        cur1 = con.cursor()
        cur1.execute(query3)
        cur1.close()
    cur0.close()


# STEP 0 - Pulizia USER_SDO_GEOM_METADATA
query_metadata_orfani='''SELECT table_name FROM USER_SDO_GEOM_METADATA
minus
SELECT table_name FROM cat WHERE table_type IN('TABLE','VIEW') ORDER BY table_name'''
cur0 = con.cursor()
logging.debug(query_metadata_orfani)
cur0.execute(query_metadata_orfani)
for result in cur0:
    subquery_delete='''DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}' '''.format(result[0])
    logging.debug(subquery_delete)
    cur0bis = con.cursor()
    try:
        cur0bis.execute(subquery_delete)
        con.commit()
    except Exception as e:
        logging.error(e)
    cur0bis.close()
cur0.close()




# STEP 1 - Verifica di tutte le tabelle spaziali presenti sul DB e conteggio delle tabelle suddivise per diverso CRS 
cur = con.cursor()
#tutte le tabelle geometriche
query='SELECT count(table_name), srid FROM mdsys.ALL_SDO_GEOM_METADATA group by srid '
logging.debug(query)
cur.execute(query)
#cur.execute('select * from all_tables')
i=0
logging.debug('i,  srid, count table')
for result in cur:
    print('{}, {}, {}'.format(i,result[1], result[0]))
    i+=1


#quit()   
#tutte le tabelle geometriche
#cur.execute('SELECT * FROM mdsys.ALL_SDO_GEOM_METADATA where srid = 32632')
#cur.execute('select * from all_tables')
#i=0
#for result in cur:
#    print(i,len(result))
    #print("{}, {}, {}, {}".format(result[0], result[1], result[2], result[3]))
#    print("{}, {}, {}, {},{}".format(result[0], result[1], result[2], result[3],result[4]))
    #print("{}, {}, {}, {},{}, {}".format(result[0], result[1], result[2], result[3],result[4], result[5]))
#    i+=1



# Step 2 - Cerco le tabelle con CRS Roma40 - GB F. Ovest dell'utente in questione
query='SELECT * FROM mdsys.USER_SDO_GEOM_METADATA WHERE (srid = 3003 OR srid=82087)'
logging.debug(query)
cur.execute(query)
#cur.execute('select * from all_tables')
i=0

#specifico i tipi geometrici supportati da ogr2ogr
n_type=[0,1,2,3,4,5,6,7]
type=['UNKNOWN','POINT', 'LINESTRING', 'POLYGON', 'GEOMETRYCOLLECTION', 'MULTIPOINT', 'MULTILINESTRING','MULTIPOLYGON']

for result in cur:
    logging.info('Passo {}'.format(i))
    table_name=result[0]
    column_name=result[1]
    logging.debug("{}, {}, {}, {}".format(result[0], result[1], result[2], result[3]))
    #cerco dimensione (2D, 3D o 4D) e tipologia di tabella geometrica
    subquery='SELECT a.{1}.Get_Dims(), a.{1}.Get_GType() FROM {0} a GROUP BY a.{1}.Get_Dims(), a.{1}.Get_GType()'.format(table_name,column_name)
    logging.debug(subquery)
    check_table=0
    cur2 = con.cursor()
    try:
        cur2.execute(subquery)
        print(subquery)
        for result2 in cur2:
            logging.debug('Dimensione = {}'.format(result2[0]))
            ntipo=result2[1]
            tipo=type[ntipo]
            logging.debug('Tipo: {}'.format(tipo))
    except Exception as e:
        check_table=1
        logging.warning('{}'.format(e))
    cur2.close()
    if check_table==0:
        #crero il comando
        new_table_name = '{}_7791'.format(table_name)
        if len(new_table_name)>30:
            comando='{0}\\bin\\ogr2ogr.exe -f "OCI" -overwrite '\
                '-s_srs "+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl '\
                '+nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs" '\
                '-t_srs EPSG:7791 -nln AAAAABBBB -lco SPATIAL_INDEX=FALSE -lco GEOMETRY_NAME={2} '\
                '-nlt {3} -lco SRID=7791 -unsetFieldWidth '\
                'oci:{4}:AAAAABBBB '\
                'oci:{4}:{1}'.format(qgis_path,table_name,column_name,tipo,parametri_con)
            logging.debug(comando)
            ret=os.system(comando)
            #rinomino la tabella con il nome giusto (problema con ogr2ogr nln per nomi maggiori di 30 char)          
            cur_a = con.cursor()
            rename=''' ALTER TABLE {}."AAAAABBBB" RENAME TO "{}_7791" '''.format(user,table_name)
            logging.debug(rename)
            cur_a.execute(rename)
            cur_a.close()
            
            metadati= ''' INSERT INTO user_sdo_geom_metadata 
                    using SELECT '{0}_7791', column_name, diminfo, srid 
                    FROM user_sdo_geom_metadata WHERE table_name LIKE 'AAAAABBBB' '''.format(table_name)
            cur_m=con.cursor()
            try:
                cur_m.execute(metadati)
                logging.debug('Metadati OK')
            except Exception as m:
                logging.error('Metadati della tabella {}_CSG non creati. \n Errore: {}'.format(table_name, m))
            cur_m.close()
            # cur_a = con.cursor()
            # metadati= ''' INSERT INTO user_sdo_geom_metadata 
            #         using SELECT '{0}_7791', column_name, diminfo, srid 
            #         FROM all_sdo_geom_metadata WHERE owner = '{1}' and table_name = 'AAAAABBBB' '''.format(table_name,user)
            # logging.debug(metadati)
            # cur_a.execute(metadati)
            # cur_a.close()
            # cur_a = con.cursor()
            # drop_metadati='''DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = 'AAAAABBBB' '''
            # logging.debug(drop_metadati)
            # logging.debug(drop_metadati)
            # cur_a.execute(drop_metadati)
            # con.commit()
            # cur_a.close()
        else: 
            comando='{0}\\bin\\ogr2ogr.exe -f "OCI" -overwrite '\
                '-s_srs "+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl '\
                '+nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs" '\
                '-t_srs EPSG:7791 -nln {1}_7791 -lco SPATIAL_INDEX=FALSE -lco GEOMETRY_NAME={2} '\
                '-nlt {3} -lco SRID=7791 -unsetFieldWidth '\
                'oci:{4}:{1}_7791 '\
                'oci:{4}:{1}'.format(qgis_path,table_name,column_name,tipo,parametri_con)
            logging.debug(comando)
            ret=os.system(comando)
        if ret!=0:
            logging.error('return= {} - Problem with ogr2ogr for table {}'.format(ret,table_name))
        else:
            logging.debug(ret)
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Rinomino le tabelle di origine e finale
        # aggiungo _SCG (Converted using Script of Gter)
        query1='ALTER TABLE {0}.{1} RENAME TO "{1}_CSG"'.format (user,table_name)
        logging.debug(query1)
        cur3 = con.cursor()
        try:
            cur3.execute(query1)
            logging.debug('Rinominata tabella {}'.format(table_name))
        except Exception as e:
            logging.error(e)
        cur3.close()
        query2='ALTER TABLE {0}.{1}_7791 RENAME TO "{1}"'.format (user,table_name)
        logging.debug(query2)
        cur3 = con.cursor()
        try:
            cur3.execute(query2)
            logging.debug('Rinominata tabella {}_7791'.format(table_name))
        except Exception as e:
            logging.error(e)
        cur3.close()
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Aggiorno i metadati spaziali
        
        # step 1 creo metadati per tabella _CSG con quelli della tabella originale
        metadati= ''' INSERT INTO user_sdo_geom_metadata 
                    using SELECT '{0}_CSG', column_name, diminfo, srid 
                    FROM user_sdo_geom_metadata WHERE table_name LIKE '{0}' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            logging.debug('Step 1 metadati OK')
        except Exception as m:
            logging.error('Metadati della tabella {}_CSG non creati. \n Errore: {}'.format(table_name, m))
        cur_m.close()
        
        
        #step 2 - rimuovo i metadati per la tabella originale
        metadati= ''' DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            logging.debug('Step 2 metadati OK: Metadati tabella originale rimossi')
        except Exception as m:
            logging.warning('Metadati della tabella {} non rimossi. \n Errore: {}'.format(table_name, m))
        cur_m.close()
        
        
        #step 3 - creo i metadati per la tabella nuova a partire da quelli della _7791
        metadati= ''' INSERT INTO user_sdo_geom_metadata 
                    using SELECT '{0}', column_name, diminfo, srid 
                    FROM user_sdo_geom_metadata WHERE table_name LIKE '{0}_7791' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            logging.debug('Step 3 metadati OK')
        except Exception as m:
            logging.error('Metadati della tabella {} non ricreati. \n Errore: {}'.format(table_name, m))
        cur_m.close()
         
        
        #step 4 - rimuovo i metadati per la tabella originale
        metadati= ''' DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}_7791' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            logging.debug('Step 4 metadati OK: Metadati tabella _7791 rimossi')
        except Exception as m:
            logging.warning('Metadati della tabella {}_7791 non rimossi. \n Errore: {}'.format(table_name, m))
        cur_m.close()
        
        
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Creazione indice spaziale 
        cur_a = con.cursor()
        spatial_index='''DROP INDEX {0}_SDX'''.format(table_name)
        logging.debug(spatial_index)
        try:
            cur_a.execute(spatial_index)
            logging.debug('Rimosso indice spaziale per tabella originale {}'.format(table_name))
        except Exception as e:
            logging.warning(e)
        cur_a.close()
        cur_a = con.cursor()
        spatial_index='''CREATE INDEX {0}_SDX
            ON {0} ( GEOMETRY )  
            INDEXTYPE IS MDSYS.SPATIAL_INDEX'''.format(table_name)
        logging.debug(spatial_index)
        try:
            cur_a.execute(spatial_index)
            logging.debug('Creato indice spaziale per tabella {}'.format(table_name))
        except Exception as e:
            logging.error(e)
        cur_a.close()
        # questo if forse sarà da rimuovere (temporaneo)
        if debug_viste > 0:
            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #cerco le viste
            query_viste='''SELECT a.owner, a.name, b.text FROM all_dependencies a 
                join all_views b on a.owner=b.owner and a.name=b.view_name
                WHERE a.type=\'VIEW\'  and upper(a.referenced_name) like upper(\'%{}%\')
                and a.referenced_type = \'TABLE\''''.format(table_name)
            #select OWNER, VIEW_NAME, TEXT FROM all_VIEWS where contains(TEXT, '{}', 1) > 0'".format(table_name)
            logging.debug(query_viste)
            cur3 = con.cursor()
            cur3.execute(query_viste)
            for result3 in cur3:
                owner=result3[0]
                view_name=result3[1]
                text=result3[2]
                #new_table_name = '{}_7791'.format(table_name)
                logging.debug(table_name)
                logging.debug(new_table_name)
                # questa parte non serve
                #nuova_vista='create or replace view {}.{} as {}'.format(owner,view_name,re.sub(table_name,new_table_name,text,flags=re.I))
                #logging.debug(nuova_vista)
                #cur4=con.cursor()
                #cur4.execute(nuova_vista)
                #cur4.close()
                # elimino vecchi metadati
                cur5=con.cursor()
                delete_metadati='''DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}' '''.format(view_name)
                try:
                    cur5.execute(subquery_delete)
                    con.commit()
                except Exception as e:
                    logging.warning('Problema nel rimuovere i metadati della vista {}. \n{}'.format(view_name, e))
                cur5.close() 
                # ricreo i metadati della vista
                metadati= ''' INSERT INTO user_sdo_geom_metadata 
                    using SELECT '{}', column_name, diminfo, srid 
                    FROM all_sdo_geom_metadata WHERE owner = '{}' and table_name = '{}' '''.format(view_name,user,new_table_name)
                cur6=con.cursor()
                try:
                    cur6.execute(metadati)
                except Exception as m:
                    logging.error('Metadati della vista {} non creati. \n Errore: '.format(view_name, m))
                cur6.close()
            cur3.close()
            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #cerco le viste materializzate
            query_mviste='''SELECT a.owner, a.name, b.* 
                FROM all_dependencies a 
                join all_mviews b on a.owner=b.owner and a.name=b.view_name
                WHERE upper(a.referenced_name) like upper(\'%{}%\')
                and a.referenced_type = \'TABLE\''''.format(table_name)
            logging.debug(query_mviste)
        
        
        
        
    i+=1
con.close()