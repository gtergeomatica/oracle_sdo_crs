-- GTER srl copyleft 2020
-- Author: Roberto Marzocchi roberto.marzocchi@gter.it
-- the SQL script can be used to update CRS in Oracle Spatial DB


-- Inserisco il DATUM 1132 (Rete_Dinamica_Nazionale_2008) 

INSERT INTO MDSYS.SDO_DATUMS ( 
DATUM_ID,
DATUM_NAME,
DATUM_TYPE,
ELLIPSOID_ID,
PRIME_MERIDIAN_ID,
INFORMATION_SOURCE,
DATA_SOURCE,
SHIFT_X,
SHIFT_Y,
SHIFT_Z,
ROTATE_X,
ROTATE_Y,
ROTATE_Z,
SCALE_ADJUST,
IS_LEGACY,
LEGACY_CODE)
VALUES (
1132,
'Rete_Dinamica_Nazionale_2008',
'GEODETIC',
7019,
8901,
NULL,
'EPSG',
NULL,
NULL,
NULL,
NULL,
NULL,
NULL,
NULL,
'FALSE',
NULL);


-- Inserisco EPSG 6706 (sistema 2D)

INSERT INTO MDSYS.SDO_COORD_REF_SYSTEM (
SRID,
COORD_REF_SYS_NAME,
COORD_REF_SYS_KIND,
COORD_SYS_ID,
DATUM_ID,
geog_crs_datum_id,
SOURCE_GEOG_SRID,
PROJECTION_CONV_ID,
CMPD_HORIZ_SRID,
CMPD_VERT_SRID,
INFORMATION_SOURCE,
DATA_SOURCE,
IS_LEGACY,
LEGACY_CODE,
LEGACY_WKTEXT,
LEGACY_CS_BOUNDS,
is_valid,
supports_sdo_geometry)
VALUES (
6706,
'RDN2008',
'GEOGRAPHIC2D',
6422,
1132,
1132,
NULL,
NULL,
NULL,
NULL,
NULL,
'EPSG',
'FALSE',
NULL,
NULL,
NULL,
'TRUE',
'TRUE');


-- Inserisco EPSG 7791 (sistema 2D)

INSERT INTO MDSYS.SDO_COORD_REF_SYSTEM (
SRID,
COORD_REF_SYS_NAME,
COORD_REF_SYS_KIND,
COORD_SYS_ID,
DATUM_ID,
geog_crs_datum_id,
SOURCE_GEOG_SRID,
PROJECTION_CONV_ID,
CMPD_HORIZ_SRID,
CMPD_VERT_SRID,
INFORMATION_SOURCE,
DATA_SOURCE,
IS_LEGACY,
LEGACY_CODE,
LEGACY_WKTEXT,
LEGACY_CS_BOUNDS,
is_valid,
supports_sdo_geometry)
VALUES (
7791,
'RDN2008 / UTM zone 32N',
'PROJECTED',
4499,
NULL,
1132,
6706,
16032,
NULL,
NULL,
'EPSG',
'EPSG',
'FALSE',
NULL,
NULL,
NULL,
'TRUE',
'TRUE');


-- Inserisco EPSG 7792 (sistema 2D)

INSERT INTO MDSYS.SDO_COORD_REF_SYSTEM (
SRID,
COORD_REF_SYS_NAME,
COORD_REF_SYS_KIND,
COORD_SYS_ID,
DATUM_ID,
geog_crs_datum_id,
SOURCE_GEOG_SRID,
PROJECTION_CONV_ID,
CMPD_HORIZ_SRID,
CMPD_VERT_SRID,
INFORMATION_SOURCE,
DATA_SOURCE,
IS_LEGACY,
LEGACY_CODE,
LEGACY_WKTEXT,
LEGACY_CS_BOUNDS,
is_valid,
supports_sdo_geometry)
VALUES (
7792,
'RDN2008 / UTM zone 33N',
'PROJECTED',
4499,
NULL,
1132,
6706,
16033,
NULL,
NULL,
'EPSG',
'EPSG',
'FALSE',
NULL,
NULL,
NULL,
'TRUE',
'TRUE');



-- Inserisco EPSG 7793 (sistema 2D)

INSERT INTO MDSYS.SDO_COORD_REF_SYSTEM (
SRID,
COORD_REF_SYS_NAME,
COORD_REF_SYS_KIND,
COORD_SYS_ID,
DATUM_ID,
geog_crs_datum_id,
SOURCE_GEOG_SRID,
PROJECTION_CONV_ID,
CMPD_HORIZ_SRID,
CMPD_VERT_SRID,
INFORMATION_SOURCE,
DATA_SOURCE,
IS_LEGACY,
LEGACY_CODE,
LEGACY_WKTEXT,
LEGACY_CS_BOUNDS,
is_valid,
supports_sdo_geometry)
VALUES (
7793,
'RDN2008 / UTM zone 34N',
'PROJECTED',
4499,
NULL,
1132,
6706,
16034,
NULL,
NULL,
'EPSG',
'EPSG',
'FALSE',
NULL,
NULL,
NULL,
'TRUE',
'TRUE');