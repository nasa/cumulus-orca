-- Create the database users and roles
\c postgres postgres
\ir database/init.sql;
\ir roles/init.sql;
\ir users/init.sql;
commit;

-- Create Schema and extensions in the new database
\c labsndbx
SET SESSION AUTHORIZATION dbo;
\ir schema/init.sql;

-- Create the application objects
\ir tables/init.sql;
commit;
