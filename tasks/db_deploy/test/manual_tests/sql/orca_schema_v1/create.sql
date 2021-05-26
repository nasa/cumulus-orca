-- Create the database users and roles
\c postgres postgres
\ir roles/init.sql;
commit;

-- Create Schema and extensions in the new database
\c disaster_recovery
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\ir schema/init.sql;
commit;

-- Create the application objects
SET SESSION AUTHORIZATION dbo;
\ir tables/init.sql;
commit;

\q
