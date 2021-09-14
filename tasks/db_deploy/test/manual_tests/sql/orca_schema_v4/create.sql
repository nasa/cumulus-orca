  
-- Create the inventory tables
SET SESSION AUTHORIZATION orca_dbo;
\ir tables/init.sql;
commit;

\q