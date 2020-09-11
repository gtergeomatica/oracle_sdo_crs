# Copyleft Roberto Marzocchi - Gter srl Innovazione in Geomatica Gnss e Gis
import os,sys,shutil,re,glob, getopt

#apro connessione Oracle
import conn
import cx_Oracle
# per girare fuori da QGIS
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_6")
# per girare fuori da QGIS
#cx_Oracle.init_oracle_client()



#installazione di QGIS
qgis_path="C:\OSGeo4W64"

# con = cx_Oracle.connect('GPE/gpeowner@192.168.1.87/xe')
parametri_con='{}/{}@//{}/{}'.format(conn.user,conn.pwd,conn.host,conn.service)
con = cx_Oracle.connect(parametri_con)
#con = cx_Oracle.connect('PC_EMERGENZE/$Allerta45$@TEST')
print(con.version)

cur = con.cursor()
#tutte le tabelle geometriche
cur.execute('SELECT count(table_name), srid FROM mdsys.ALL_SDO_GEOM_METADATA group by srid ')
#cur.execute('select * from all_tables')
i=0
print('i,  srid, count table')
for result in cur:
    print('{}, {}, {}'.format(i,result[1], result[0]))
    i+=1


#quit()   
#tutte le tabelle geometriche
cur.execute('SELECT * FROM mdsys.ALL_SDO_GEOM_METADATA where srid = 32632')
#cur.execute('select * from all_tables')
i=0
for result in cur:
    print(i,len(result))
    #print("{}, {}, {}, {}".format(result[0], result[1], result[2], result[3]))
    print("{}, {}, {}, {},{}".format(result[0], result[1], result[2], result[3],result[4]))
    #print("{}, {}, {}, {},{}, {}".format(result[0], result[1], result[2], result[3],result[4], result[5]))
    i+=1

query='SELECT * FROM mdsys.USER_SDO_GEOM_METADATA WHERE (srid = 3003 OR srid=82087) --AND TABLE_NAME=\'TEST_PUNTI_3003\''
#print(query)
cur.execute(query)
#cur.execute('select * from all_tables')
i=0

#specifico i tipi geometrici supportati da ogr2ogr
n_type=[0,1,2,3,4,5,6,7]
type=['UNKNOWN','POINT', 'LINESTRING', 'POLYGON', 'GEOMETRYCOLLECTION', 'MULTIPOINT', 'MULTILINESTRING','MULTIPOLYGON']

for result in cur:
    print(i,len(result))
    table_name=result[0]
    column_name=result[1]
    print("{}, {}, {}, {}".format(result[0], result[1], result[2], result[3]))
    subquery='SELECT a.{1}.Get_Dims(), a.{1}.Get_GType() FROM {0} a GROUP BY a.{1}.Get_Dims(), a.{1}.Get_GType()'.format(table_name,column_name)
    check_table=0
    cur2 = con.cursor()
    try:
        cur2.execute(subquery)
        print(subquery)
        for result2 in cur2:
            print('Dimensione = {}'.format(result2[0]))
            ntipo=result2[1]
            tipo=type[ntipo]
            print('Tipo: {}'.format(tipo))
    except:
        check_table=1
    if check_table==0:
        comando='{0}\\bin\\ogr2ogr.exe -f "OCI" -overwrite '\
            '-s_srs "+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl '\
            '+nadgrids={0}\\share\\proj\\44080835_44400922_R40_F00.gsb +units=m +no_defs" '\
            '-t_srs EPSG:7791 -nln {1}_7791  -lco GEOMETRY_NAME={2} '\
            '-nlt {3} -lco SRID=7791 -unsetFieldWidth '\
            'oci:{4}:{1}_7791 '\
            'oci:{4}:{1}'.format(qgis_path,table_name,column_name,tipo,parametri_con)
        print(comando)
        ret=os.system(comando)
        print(ret)
    i+=1