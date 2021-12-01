CREATE DATABASE orca
    OWNER postgres
    TEMPLATE template1
    ENCODING 'UTF8';

COMMENT ON DATABASE orca
    IS 'Operational Recovery Cloud Archive (ORCA) database.';
