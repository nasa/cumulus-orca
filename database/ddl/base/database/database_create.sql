-- Create the DR database

CREATE DATABASE disaster_recovery
    OWNER postgres
    TEMPLATE template0
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF8'
    LC_CTYPE 'en_US.UTF8';
