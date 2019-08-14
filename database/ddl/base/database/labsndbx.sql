-- Create the DAAC database
DROP DATABASE IF EXISTS labsndbx;

CREATE DATABASE labsndbx
    OWNER postgres
    TEMPLATE template0
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF8'
    LC_CTYPE 'en_US.UTF8';

COMMENT ON DATABASE labsndbx
    IS 'Lisa sandbox database.';
