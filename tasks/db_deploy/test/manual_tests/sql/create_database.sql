CREATE DATABASE disaster_recovery
    OWNER postgres
    TEMPLATE template1
    ENCODING 'UTF8';

COMMENT ON DATABASE disaster_recovery
    IS 'Operational Recovery Cloud Archive (ORCA) database.';
