# oracle_sdo_crs

Istruzioni repository
-----------------------------------------------------------------------

Analisi e script sul DB Oracle

- **analisi_CRS_3003**: cartella contente alcune analisi al file 

- **oracleSpatialCoord_rdn2008_it.sql**: script per aggiornare il DB Oracle con il CRS RDN2008 (EPSG 6706) e i sistemi con proiezione UTM32, UTM33 e UTM34 
(mancano proiezione con Fuso Italia e Fuso 12) per cui sarebbero da aggiungere i riferimenti alle proiezioni utilizzate



Manuale d'uso ogr2ogr per Oracle
-----------------------------------------------------------------------

Il comando *ogr2ogr* è una utility da linea di comando che viene installata con la libreria GDAL ed è comunemente disponibile sia su distribuzioni linux che windows. E' molto comoda per gestire cambi di coordinate (anche usando i grigliati IGM in formato NTv2) e/o di formato. Nonchè l'import/export da DB 

Su linux si installa tramite il comando 
    
```   
sudo apt install gdal-bin
```
o (distro RH o Centos) 
```
sudo yum install gdal
```

Qualora su linux si voglia accedere al DB Oracle (in lettura o scrittura in funzione dei propri permessi) occorre installare i client oracle https://www.oracle.com/it/database/technologies/instant-client/linux-x86-64-downloads.html e quindi compilare la libreria GDAL con la configurazione opportuna per Oracle. 


Su windows la strada più semplice è tramite l'OsGeo4W Installer di QGIS che consente anche di installare e aggiornare le varie versioni di QGIS (si veda a tal proposito la nostra guida https://install-qgis-windows-dummies.readthedocs.io/en/latest/)


A quel punto il comando ogr2ogr è contenuto nella cartella `C:\OSGeo4W64\bin`, contiene già i client Oracle, e si può usare:

- dalla powershell di Windows (Windows PowerShell ISE)

![wp](/img/windows_powershell.PNG)

- dalla OsGeo4W Shell 

![wp](/img/osgeo_shell.PNG)


Per importare uno shapefile su Oracle la sintassi base è la seguente:

```
ogr2ogr -f "OCI" -overwrite  -nln NOME_TABELLA_ORACLE -lco GEOMETRY_NAME=GEOMETRY -nlt POINT -lco SRID=7791 -unsetFieldWidth oci:USER/PWD$@//INDIRIZZO_ISTANZA _ORACLE:NOME_TABELLA_ORACLE PERCORSO_SHAPEFILE
```

es (nel caso di istanza oracle ). 

```
ogr2ogr -f "OCI" -overwrite  -nln TEST_IMPORT_SONDAGGI -lco GEOMETRY_NAME=GEOMETRY -nlt POINT -lco SRID=7791 -unsetFieldWidth oci:XXXXXX/XXXXX@//vm-oraprod-linux2/georef11.**dominio**:TEST_IMPORT_SONDAGGI C:\Users\assis\Downloads\per_roberto\SondaggiGEO_U00-32.shp
```
