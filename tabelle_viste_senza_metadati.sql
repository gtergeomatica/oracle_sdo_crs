-- recupero viste e tabelle spaziali ma senza metadati spaziali
--select 
--owner,count("Name") 
--FROM
(select c.owner, 
case 
  when exists (select table_name from dba_tables where owner=c.owner and table_name=c.table_name) then 'Table'
  when exists (select view_name from dba_views where owner=c.owner and view_name=c.table_name) then 'View'
  else 'unknown!'
end as "Type",
c.table_name as "Name",
c.column_name as "Geometry Column"
from  dba_tab_columns c 
where 
--c.owner in ('GTER_USER', 'TOPONOMASTICA','MEDIATORE') 
--    and 
c.data_type='SDO_GEOMETRY'
  and not exists (select table_name from ALL_SDO_GEOM_METADATA where table_name=c.table_name and column_name=c.column_name)
  and  c.table_name not like 'BIN$%'                -- ignore recycle bin
  and  c.table_name not like 'DR$%'                 -- ignore Oracle Text tables
  and  c.table_name not like 'EUL%'                 -- ignore Discoverer End User Layer (EUL) tables
  and  c.table_name not like '%PLAN_TABLE'          -- ignore explain plan tables and Toad explain plan table
  and  c.table_name not like 'MLOG$%'               -- ignore materialized view log tables
  and  c.table_name not like 'RUPD$%'               -- ignore materialized view log table  
order by c.owner,
case 
  when exists (select table_name from dba_tables where owner=c.owner and table_name=c.table_name) then 'Table'
  when exists (select view_name from dba_views where owner=c.owner and view_name=c.table_name) then 'View'
  else 'unknown!'
end,
c.table_name)
--group by owner
--order by owner; 