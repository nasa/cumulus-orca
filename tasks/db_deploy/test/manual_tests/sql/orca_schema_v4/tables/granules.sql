
/*
** SCHEMA: orca
** 
** TABLE: granules
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set search path
    SET search_path TO orca, public;

    CREATE TABLE IF NOT EXISTS granules
    (
      id                    bigserial NOT NULL
    , collection_id         text NOT NULL
    , cumulus_granule_id    text NOT NULL
    , execution_id          text NOT NULL
    , ingest_time           timestamp with time zone NOT NULL
    , last_update           timestamp with time zone NOT NULL
    , CONSTRAINT PK_granules PRIMARY KEY (id)
    , CONSTRAINT FK_collection_granule FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
    , CONSTRAINT UNIQUE_collection_granule_id UNIQUE (collection_id, cumulus_granule_id)
    );

    -- Comments
    COMMENT ON TABLE granules
        IS 'Granules that are in the ORCA archive holdings.';
    COMMENT ON COLUMN granules.id
        IS 'Internal orca granule ID pseudo key';
    COMMENT ON COLUMN granules.collection_id
        IS 'Collection ID from Cumulus that refrences the Collections table.';
        COMMENT ON COLUMN granules.cumulus_granule_id
        IS 'Granule ID from Cumulus';
        COMMENT ON COLUMN granules.execution_id
        IS 'AWS step function execution id';
    COMMENT ON COLUMN granules.ingest_time
        IS 'Date and time the granule was originally ingested into ORCA.';
    COMMENT ON COLUMN granules.last_update
        IS 'Last time the data for the granule was updated. This generally will coincide with a duplicate or a change to the underlying data file.';                    
    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON granules TO orca_app;

COMMIT;