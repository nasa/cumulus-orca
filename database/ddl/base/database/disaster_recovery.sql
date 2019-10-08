-- Create the DAAC database
DROP DATABASE IF EXISTS disaster_recovery;

CREATE DATABASE disaster_recovery
    OWNER postgres
    TEMPLATE template0
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF8'
    LC_CTYPE 'en_US.UTF8';

COMMENT ON DATABASE disaster_recovery
    IS 'Disaster Recovery database.';
