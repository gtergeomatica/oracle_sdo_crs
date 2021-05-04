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
ogr2ogr -f "OCI" -overwrite  -nln TEST_IMPORT_SONDAGGI -lco GEOMETRY_NAME=GEOMETRY -nlt POINT -lco SRID=7791 -unsetFieldWidth oci:XXXXXX/XXXXX@//vm-oraprod-linux2/georef11.dominio:TEST_IMPORT_SONDAGGI C:\Users\assis\Downloads\per_roberto\SondaggiGEO_U00-32.shp
```

dove
- `-f "OCI"`: formato di importazione Oracle
- `-lco OVERWRITE=YES`: per forzare la sovrascrittura del dato importato
- `-nln NOME_TABELLA_ORACLE`: per definire il nome della tabella oracle
- `-lco GEOMETRY_NAME=NOME_COLONNA_GEMETRIA`: specifico il nome del campo geometria
- `-lco SRID=7791` : precisa il SRID che deve avere la tabella in Oracle (il SRID deve essere presente sul DB)
- `-lco PRECISION=NO` o in alternativa `-unsetFieldWidth`: molto comodo per prevenire eventuali errori dovuto alle precisioni dei campi numerici
- `-nlt GEOMETRY_TYPE` : **opzione fondamentale** gestisce il corretto import dei dati di partenza a livello geometrico (ad esempio `-nlt POINT`)
- `-unsetFieldWidth`: molto comodo per prevenire eventuali errori dovuto alle precisioni dei campi numerici
- `oci:USER/PWD$@//INDIRIZZO_ISTANZA _ORACLE:NOME_TABELLA_ORACLE`: utente:password@indirizzo_istanza:nome_tabella
- percorso allo shapefile

A questo link l'elenco completo delle Layer Creation Option disponibili per Oracle https://gdal.org/drivers/vector/oci.html per esempio altre istruzioni comode potrebbero essere: 
- `-lco TRUNCATE=YES` per mantenere eventuali indici o vincoli già esistenti o anche modifiche al tipo di campo (es. conversioni di float/integer o altro)
- `-lco SPATIAL_INDEX=NO` per evitare che venga creato uno spatial index di default

**NOTA BENE 1 - Password con $**

Nel caso in cui si usino delle password con il carattere `$` la powershell di windows (non serve questa nota nel caso in cui si usi la OsGeo4W Shell) interpreta quel campo come una variabile per cui non riconosce il comando correttamente. A quel punto è suffiente:

1) definire una variabile 

```
$pwd='password_con_$'
```

2) richiamare la variabile nella stringa 

es. `oci:USER/$pwd$@//INDIRIZZO_ISTANZA _ORACLE:NOME_TABELLA_ORACLE`: 


**NOTA BENE 2 - Errori al primo import**

Qualora la tabella non sia già presente in oracle alla prima importazione vengono fuori i seguenti messaggi di errore che però **non sono preoccupanti**. Semplicemente segnalano che non la tabella che si sta importando non esiste nei metadati di Oracle `OCIDescribeAny`

```
ERROR 1: ORA-04043: object NOME_TABELLA_ORACLE does not exist
 in OCIDescribeAny
ERROR 1: ORA-04043: object NOME_TABELLA_ORACLE does not exist
 in OCIDescribeAny
ERROR 1: ORA-04043: object "NOME_TABELLA_ORACLE" does not exist
 in OCIDescribeAny
ERROR 1: ORA-04043: object "NOME_TABELLA_ORACLE" does not exist
 in OCIDescribeAny
 ```


# Script python

## Introduzione

Gli script python realizzati hanno lo scopo di convertire, servendosi di ogr2ogr le tabelle di oracle nel sistema di riferimento Roma40 Monte Mario - Gauss Boaga Fuso Ovest (EPSG 3003) nel nuovo sistema di coordinate ufficiale italiano RDN2008 - UTM32N (EPSG 7791) servendosi dei grigliati IGM in formato NTv2


Complessivamente gli script sono i seguenti: 
- **conversione_oracle_19.py** : gestisce la conversione delle tabelle 

![wp](/img/schema_tabelle.png)


-----------------------------------------------------------------------


- **viste.py** : gestisce la conversione delle viste

![wp](/img/schema_viste.png)


-----------------------------------------------------------------------


Ci sono poi 2 script accessori usati per i test
- **pulizia_oracle_19.py** : ripristina nomi tabelle e metadati a quelli originali attraverso una ricerca delle tabelle con suffisso **CSG** (*Converted by Script Gter*)
- **update_viste_test.py** : allinea i metadati delle viste nell'ambiente di test a quello di produzione



Tutti gli script usano il file **credenziali.py** che va creato e dove vanno salvati utenti e password degli schemi su cui agire e il file **impostazione_base.py** che va semplicemente modificato.

Per le istruzioni dettagliate vedi le seguenti sezioni

## Fasi di installazione

Per fruire dello script su sistemi Windows si suggerisce di eseguire le seguenti operazioni preliminari:

1) avere QGIS installato da OsGeo4W Installer (si vedano queste istruzioni nel caso https://install-qgis-windows-dummies.readthedocs.io/it/latest/)

2) copiare il file con i grigliatiin formato NTv2 XXXX_**R40_F00.gsb** ed eventualmente gli altri file .gsb nella cartella C:\\OSGeo4W64\\share\\proj

3) aprire la OSGeo4W shell 

4) digitare `py3_env` che dovrebbe stampare i percorsi dell'installazione python con QGIS e abilitare python sulla shell OsGeo

4) digitare `python -m pip install --upgrade pip` per aggiornare pip

5) digitare `python -m pip install cx_Oracle` (da testare ma forse occorre avere i privilegi di installare qualcosa nella cartella C:\OSGeo4W64)

6) scaricare instant client oracle https://www.oracle.com/it/database/technologies/instant-client/downloads.html

![wp](/img/oic0.png)

scompattare la cartella e salvarla da qualche parte sul PC (es. C:\oracle\instantclient_**19_9**)



A quel punto lo script dovrebbe funzionare direttamente dalla console python di QGIS, ma c'è un problema con la libreria per i log (logging) per cui si consiglia di usare piuttosto la **powershell di Windows**



## Lanciare gli scritp  


### Operazioni da fare la prima volta o in caso di aggiornamenti
1) scaricare la presente cartella con il tasto in alto a destra 

![wp](/img/download.PNG)

(oppure clonare il repository GitHub per restare sempre aggiornati - Si suggerisce l'installazione di GitHub desktop)

2) scompattare la cartella e aggiungere file *credenziali.py* con le credenziali di accesso al DB oracle:

```
# credenziali di accesso al DB
user='XXXXXX'
pwd='XXXXXXX'


host='XXXXX'
service='XXXXX.dominio.it'

# usati solo dallo script update_viste_test.py
host_produzione='XXXXX'
service_produzione='XXXXX.dominio.it'

```

3) aprire il file **impostazioni_base.py** e modificare la seguente riga specificando il percorso e la versione (es. instantclient_**19_9** ) del client oracle precedentemente scaricato

```
cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_9")
```

controllare (e se necessario cambiare) la riga in cui si specifica il percorso radice di QGIS

```
#cartella dove è installato QGIS
qgis_path="C:\OSGeo4W64"
```



### Operazioni da fare ogni volta e per lanciare i singoli script
4) aprire la **powershell** di windows

![wp](/img/powershell0.PNG)


e andare alla cartella scaricata, a titolo di esempio 

```
cd .\Documents\GitHub\oracle_sdo_crs\ 
```
![wp](/img/powershell1.PNG)



5) Lanciare uno script python. 

Quello di test per verificare che tutto funzioni è **test_python_qgis.py** che dovrebbe creare uno script di log con specificato l'utente che viene usato e l'ambiente (host e service di test o di esercizio)

```
 C:\OSGeo4W64\apps\Python37\python.exe .\test_python_qgis.py
```

### Gestione dei log:
I log vengono salvati nella cartella log:

- YYYYMMDDHHmm_UTENTE_nomescript.py il livello di log è impostato su DEBUG che è il massimo (ossia stampo tutto) è possibile ridurre (o semplificare il log) usando i seguenti livelli

- **DEBUG** stampa tutto (es. script SQL lanciati dagli script)
- **INFO** stampa le informazioni sugli step in cui si trova lo script
- **WARNING** stampa solo warning ed errori
- **ERROR** stampa solo gli errori






<!-- 
3) nel file principale denominato **conversione_oracle19.py** controllare le seguenti righe:

```
#da toglere commento e modificare su QGIS
#sys.path.insert(0, r'C:\Users\assis\Documents\GitHub\oracle_sdo_crs')
from credenziali import *
print('test')
# decommentare e modificare la seguente riga per lanciare lo script fuori da QGIS
#cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_6")
# decommentare e modificare la seguente riga per lanciare lo script da QGIS
cx_Oracle.init_oracle_client()
```

4) per le fasi di debug abbiamo anche creato un file denominato **pulizia_oracle19.py** che riporta tutto allo stato iniziale -->