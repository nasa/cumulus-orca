
/*
** SCHEMA: orca
** 
** TABLE: providers
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set search path
    SET search_path TO orca, public;

    CREATE TABLE IF NOT EXISTS providers
    (
        provider_id         text NOT NULL
    , name                text NOT NULL
    , CONSTRAINT PK_providers PRIMARY KEY (provider_id)
    );

    -- Comments
    COMMENT ON TABLE providers
        IS 'Providers that are in the ORCA holdings.';
    COMMENT ON COLUMN providers.provider_id
        IS 'Provider ID supplied by Cumulus.';
    COMMENT ON COLUMN providers.name
        IS 'User friendly name of the provider provided by Cumulus.';
    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON providers TO orca_app;

COMMIT;