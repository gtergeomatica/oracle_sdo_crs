# oracle_sdo_crs

Istruzioni repository
-----------------------------------------------------------------------

Analisi e script sul DB Oracle

- **analisi_CRS_3003**: cartella contente alcune analisi al file 

- **oracleSpatialCoord_rdn2008_it.sql**: script per aggiornare il DB Oracle con il CRS RDN2008 (EPSG 6706) e i sistemi con proiezione UTM32, UTM33 e UTM34 
(mancano proiezione con Fuso Italia e Fuso 12) per cui sarebbero da aggiungere i riferimenti alle proiezioni utilizzate



Manuale d'uso ogr2ogr per Oracle
-----------------------------------------------------------------------

Il comando ogr2ogr viene installato con la libreria GDAL ed è comunemente disponibile sia su distribuzioni linux che windows

Su linux si installa tramite il comando 
    
```   
sudo apt install gdal-bin
```
o (distro RH o Centos) 
```
sudo yum install gdal
```

Su windows la strada più semplice è tramite l'OsGeo4W Installer di QGIS che consente anche di installare e aggiornare le varie versioni di QGIS (si veda a tal proposito la nostra guida https://install-qgis-windows-dummies.readthedocs.io/en/latest/)


A quel punto il comando ogr2ogr è contenuto nella cartella `C:\OSGeo4W64\bin`



