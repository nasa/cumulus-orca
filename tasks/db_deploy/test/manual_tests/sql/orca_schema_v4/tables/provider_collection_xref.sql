
/*
** SCHEMA: orca
** 
** TABLE: provider_collection_xref
**
** 
*/

-- Start a transaction
BEGIN;
    -- Set search path
    SET search_path TO orca, public;

    CREATE TABLE IF NOT EXISTS provider_collection_xref
    (
      provider_id           text NOT NULL
    , collection_id         text NOT NULL
    , CONSTRAINT PK_provider_collection_xref PRIMARY KEY (provider_id,collection_id)
    , CONSTRAINT FK_provider_collection FOREIGN KEY (provider_id) REFERENCES providers (provider_id)
    , CONSTRAINT FK_collection_provider FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
    );

    -- Comments
    COMMENT ON TABLE provider_collection_xref
        IS 'Cross refrence table that ties a collection and provider together and resolves the many to many relationship.';
    COMMENT ON COLUMN provider_collection_xref.provider_id
        IS 'Provider ID from the providers table.';
    COMMENT ON COLUMN provider_collection_xref.collection_id
        IS 'Collection ID from the collections table.';     
    -- Grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON provider_collection_xref TO orca_app;

COMMIT;