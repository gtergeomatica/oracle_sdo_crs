--select * FROM MDSYS.SDO_COORD_REF_SYS WHERE SRID in (3003,4499,6265,4265,6706,7791,7792,7793);


--select * FROM MDSYS.SDO_COORD_SYS WHERE COORD_SYS_ID in (4499);


--SELECT * FROM MDSYS.SDO_DATUMS WHERE DATUM_ID in (6265, 1132)


--SELECT * FROM MDSYS.SDO_CS_SRS where SRID=3003;


--View

SELECT * FROM MDSYS.SDO_COORD_REF_SYSTEM WHERE SRID in (3003,4499,6265,4265);




--ESEMPIO DI INSERT NELLA VISTA dal sito https://docs.oracle.com/database/121/SPATL/creating-user-defined-coordinate-reference-system.htm#GUID-1C9F778B-DFCC-4944-A298-BCB70EDD747A
-- INSERT INTO SDO_COORD_REF_SYSTEM (
--        SRID,
--        COORD_REF_SYS_NAME,
--        COORD_REF_SYS_KIND,
--        COORD_SYS_ID,
--        DATUM_ID,
--        GEOG_CRS_DATUM_ID,
--        SOURCE_GEOG_SRID,
--        PROJECTION_CONV_ID,
--        CMPD_HORIZ_SRID,
--        CMPD_VERT_SRID,
--        INFORMATION_SOURCE,
--        DATA_SOURCE,
--        IS_LEGACY,
--        LEGACY_CODE,
--        LEGACY_WKTEXT,
--        LEGACY_CS_BOUNDS,
--        IS_VALID,
--        SUPPORTS_SDO_GEOMETRY)
--  VALUES (
--        9992085,
--        'My Own NAD27 / Cuba Norte',
--        'PROJECTED',
--        4532,
--        NULL,
--        6267,
--        4267,
--       18061,
--        NULL,
--        NULL,
--        'Institut Cubano di Hidrografia (ICH)',
--        'EPSG',
--        'FALSE',
--        NULL,
--        NULL,
--       NULL,
--        'TRUE',
--        'TRUE');