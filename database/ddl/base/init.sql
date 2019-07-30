-- Create the database users and roles
\c postgres postgres
\ir database/init.sql;
\ir roles/init.sql;
\ir users/init.sql;
commit;

-- Create Schema and extensions in the new database
\c labsndbx
\ir schema/init.sql;
commit;

-- Create the application objects
SET SESSION AUTHORIZATION dbo;
\ir tables/init.sql;
commit;

