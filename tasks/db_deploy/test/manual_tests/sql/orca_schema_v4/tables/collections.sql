
/*
** SCHEMA: orca
** 
** TABLE: collections
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set search path
    SET search_path TO orca, public;

    CREATE TABLE IF NOT EXISTS collections
    (
    collection_id         text NOT NULL
    , shortname             text NOT NULL
    , version               text NOT NULL
    , CONSTRAINT PK_collections PRIMARY KEY (collection_id)
    );

    -- Comments
    COMMENT ON TABLE collections
        IS 'Collections that are in the ORCA archive holdings.';
    COMMENT ON COLUMN collections.collection_id
        IS 'Collection ID from Cumulus usually in the format shortname__version.';
    COMMENT ON COLUMN collections.shortname
        IS 'Collection short name from Cumulus.';
    COMMENT ON COLUMN collections.version
        IS 'Collection version from Cumulus.';       
    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON collections TO orca_app;

COMMIT;