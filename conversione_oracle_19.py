#!/usr/bin/env python
# coding=utf-8
# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt
import cx_Oracle


#libreria per gestione log
import logging

from impostazione_base import *

from credenziali import *

# inserire riferimento a data e schema

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    filemode ='w',
    filename='{}\log\{}_{}_conversione_oracle_19.log'.format(spath, date_file, user),
    level=logging.DEBUG)





# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(user,pwd,host,service)
con = cx_Oracle.connect(parametri_con)
logging.info("Versione ORACLE: {}".format(con.version))


# DEBUG VISTE (if debug_viste=0 non fa nulla sulle viste (PER ORA TEST))
debug_viste=0




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
query='''SELECT a.owner, a.srid, count(a.table_name) FROM mdsys.ALL_SDO_GEOM_METADATA a
LEFT JOIN SYS.all_mviews c ON  a.TABLE_NAME=c.MVIEW_NAME
WHERE c.MVIEW_NAME IS NULL 
group by a.srid, a.owner 
ORDER BY a.owner'''
logging.debug(query)
cur.execute(query)
#cur.execute('select * from all_tables')
i=0
logging.info('*****************************************************')
logging.info('CENSIMENTO TABELLE PER SCHEMA \nschema,  srid, count table')
for result in cur:
    logging.info('{}, {}, {}'.format(result[0],result[1], result[2]))
    i+=1
logging.info('*****************************************************')
cur.close()

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
logging.debug('''Cerco le tabelle con CRS Roma40 - GB F. Ovest dell'utente in questione''')
query='''SELECT a.* FROM mdsys.USER_SDO_GEOM_METADATA a 
JOIN USER_TABLES b ON  a.TABLE_NAME=b.TABLE_NAME 
LEFT JOIN SYS.all_mviews c ON  a.TABLE_NAME=c.MVIEW_NAME
WHERE (srid = 3003 OR srid=82087) 
AND c.MVIEW_NAME IS NULL AND a.TABLE_NAME NOT LIKE '%_CSG' '''
logging.debug(query)
cur = con.cursor()
cur.execute(query)
#cur.execute('select * from all_tables')
i=0


for result in cur:
    logging.info('*******************************************\nPasso {}'.format(i))
    cc=0 #questo lo uso come check
    table_name=result[0]
    column_name=result[1]
    logging.debug("{}, {}, {}, {}".format(result[0], result[1], result[2], result[3]))
    #cerco dimensione (2D, 3D o 4D) e tipologia di tabella geometrica
    subquery='''SELECT a.{1}.Get_Dims(), a.{1}.Get_GType() FROM {0} a 
    where a.{1}.Get_Dims() is not null and a.{1}.Get_Dims() is not null 
    GROUP BY a.{1}.Get_Dims(), a.{1}.Get_GType()'''.format(table_name,column_name)
    #logging.debug(subquery)
    check_table=0
    cur2 = con.cursor()
    try:
        cur2.execute(subquery)
        logging.debug(subquery)
        for result2 in cur2:
            dim=result2[0]
            logging.debug('Dimensione = {}'.format(dim))
            ntipo=result2[1]
            tipo=type[ntipo]
            si_tipo=si_type[ntipo]
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
                '-nlt {3} -lco SRID=7791 -dim {5} -unsetFieldWidth '\
                'oci:{4}:AAAAABBBB '\
                'oci:{4}:{1}'.format(qgis_path,table_name,column_name,tipo,parametri_con,dim)
            logging.debug(comando)
            ret=os.system(comando)
            #rinomino la tabella con il nome giusto (problema con ogr2ogr nln per nomi maggiori di 30 char)          
            cur_a = con.cursor()
            rename=''' ALTER TABLE {}."AAAAABBBB" RENAME TO "{}_7791" '''.format(user,table_name)
            logging.debug(rename)
            try:
                cur_a.execute(rename)
                cur_a.close()
            except Exception as m:
                logging.error(m)
                continue
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
                '-nlt {3} -lco SRID=7791 -dim {5} -unsetFieldWidth '\
                'oci:{4}:{1}_7791 '\
                'oci:{4}:{1}'.format(qgis_path,table_name,column_name,tipo,parametri_con,dim)
            logging.debug(comando)
            ret=os.system(comando)
        if ret!=0:
            logging.error('return= {} - Problem with ogr2ogr for table {}'.format(ret,table_name))
            logging.warning('Taella {} non convertita correttamente'.format(ret,table_name))
            continue
        else:
            logging.debug(ret)
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Rimuovo indice spaziale per evitare che ci sia un qualche problema che dia fastidio nei passi seguenti
        cur_a = con.cursor()
        spatial_index='''DROP INDEX {0}_SDX'''.format(table_name)
        logging.debug(spatial_index)
        try:
            cur_a.execute(spatial_index)
            logging.debug('Rimosso indice spaziale per tabella originale {}'.format(table_name))
        except Exception as e:
            logging.warning(e)
        cur_a.close()
        
        
        
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
            continue
        cur3.close()
        query2='ALTER TABLE {0}.{1}_7791 RENAME TO "{1}"'.format (user,table_name)
        logging.debug(query2)
        cur3 = con.cursor()
        try:
            cur3.execute(query2)
            logging.debug('Rinominata tabella {}_7791'.format(table_name))
        except Exception as e:
            logging.error(e)
            continue
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
            con.commit()
            logging.debug('Step 1 - impostati metadati per la tabella {}_CSG'.format(table_name))
        except Exception as m:
            logging.error('Metadati della tabella {}_CSG non creati. \n Errore: {}'.format(table_name, m))
        cur_m.close()
        
        
        #step 2 - rimuovo i metadati per la tabella originale
        metadati= ''' DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            con.commit()
            logging.debug('Step 2 - Metadati tabella originale {} rimossi'.format(table_name))
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
            con.commit()
            logging.debug('Step 3 - Impostati i metadati della tabella {}'.format(table_name))
        except Exception as m:
            logging.error('Metadati della tabella {} non ricreati. \n Errore: {}'.format(table_name, m))
        cur_m.close()
         
        
        #step 4 - rimuovo i metadati per la tabella _7791
        metadati= ''' DELETE FROM USER_SDO_GEOM_METADATA WHERE table_name = '{}_7791' '''.format(table_name)
        cur_m=con.cursor()
        try:
            cur_m.execute(metadati)
            con.commit()
            logging.debug('Step 4 - Metadati tabella {}_7791 rimossi'.format(table_name))
        except Exception as m:
            logging.warning('Metadati della tabella {}_7791 non rimossi. \n Errore: {}'.format(table_name, m))
        cur_m.close()
        
        
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Creazione indice spaziale 
        cur_a = con.cursor()
        #spatial_index='''CREATE INDEX {0}_SDX
        #    ON {0} ( GEOMETRY )  
        #    INDEXTYPE IS MDSYS.SPATIAL_INDEX;
        #'''.format(table_name, dim, tipo)
        spatial_index='''CREATE INDEX {0}_SDX 
        ON {0} ({3}) INDEXTYPE IS MDSYS.SPATIAL_INDEX 
        PARAMETERS ('sdo_indx_dims={1}, layer_gtype={2}')
        '''.format(table_name, dim, si_tipo, column_name)
        #######################################################################
        # specificate il tipo di geometria e se è 2D o 3D  !!!!!!! TODO !!!!!!
        # PARAMETERS con GTYPOE
        # #######################################################################
        logging.debug(spatial_index)
        try:
            cur_a.execute(spatial_index)
            con.commit()
            logging.debug('Creato indice spaziale per tabella {}'.format(table_name))
        except Exception as e:
            logging.warning(e)
        cur_a.close()

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Ripristino permessi

        #da qua li verifico (GRANTEE, PRIVILEGE e GRANTABLE che decide se usare o meno il WITH...)
        queryp0='''SELECT PRIVILEGE, GRANTEE, GRANTABLE FROM USER_TAB_PRIVS 
        WHERE TABLE_NAME like '{}_CSG' '''.format(table_name)
        cur_p0 = con.cursor()
        logging.debug(queryp0)
        cur_p0.execute(queryp0)
        for priv in cur_p0:
            queryp1 = '''GRANT {0} ON {1} TO {2} '''.format(priv[0],table_name, priv[1])
            if priv[2] == 'YES':
                queryp1 = '{} WITH GRANT OPTION'.format(queryp1)
            cur_p1 = con.cursor()
            logging.debug(queryp1)
            try:
                cur_p1.execute(queryp1)
                con.commit()
            except Exception as e:
                logging.warning(e)
            cur_p1.close()
        cur_p0.close()

        # qua li assegno
        #GRANT SELECT ON RIS_ELEZIONI_EU_2019 TO GTER_USER WITH GRANT OPTION;


        ##################################################################################
        # questa parte non e' da fare qua
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
                    logging.debug('Metadati della vista {} rimossi.'.format(view_name))
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
                    con.commit()
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

logging.info("Finito ciclo su tabelle da convertire. Chiusura connessione al DB in corso") 
con.close()