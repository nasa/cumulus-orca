INSERT INTO orca.providers
SELECT 
    uuid_generate_v4() AS provider_id
    ,substr(md5(random()::text), 0, 25) AS name
FROM
    generate_series(1,10)
;


INSERT INTO orca.collections
SELECT
    shortname || '__' || lpad(version::text, 3, '0') AS collection_id
   ,shortname AS shortname
   ,lpad(version::text, 3, '0') AS version
FROM (
    SELECT
       substr(md5(random()::text), 0, 25) AS shortname
       ,floor(random() * (199-1+1) + 1)::int AS version
    FROM
       generate_series(1,10) 
    ) x
;

DO $$
DECLARE
    my_query text := 'INSERT INTO orca.granules (provider_id, collection_id, cumulus_granule_id, execution_id, ingest_time, cumulus_create_time, last_update)
                      SELECT 
                          (SELECT provider_id from orca.providers limit 1 offset $1) AS provider_id
                          ,(SELECT collection_id from orca.collections limit 1 offset $1) AS collection_id
                          ,granule_id AS cumulus_granule_id
                          ,uuid_generate_v4() AS execution_id
                          ,now() AS ingest_time
                          ,now() AS cumulus_create_time
                          ,now() AS last_update
                      FROM orca.recovery_job 
                      LIMIT 33 
                      OFFSET $2
                      RETURNING provider_id, collection_id, cumulus_granule_id';
    my_record record;
    granule_offset int;
BEGIN
    for my_offset in 0..9 loop
        granule_offset := my_offset * 33;
        for my_record in execute my_query using my_offset, granule_offset loop
            raise notice 'INSERTED - PROVIDER: %; COLLECTION: %; GRANULE: %', my_record.provider_id, my_record.collection_id, my_record.cumulus_granule_id;
        end loop;
    end loop;
END; $$
;

INSERT INTO orca.files (granule_id, name, orca_archive_location, cumulus_archive_location, key_path, ingest_time, etag, version, size_in_bytes, hash, hash_type, storage_class_id)
SELECT DISTINCT
    g.id AS granule_id
    ,rf.filename AS name
    ,'my_orca_archive' AS orca_archive_location
    ,rf.restore_destination AS cumulus_archive_location
    ,rf.key_path AS key_path
    ,now() AS ingest_time
    ,uuid_generate_v4() AS etag
    ,'latest' AS version
    ,floor(random() * (99999999-6+1) + 6)::int AS size_in_bytes
    ,NULL AS hash
    ,NULL AS hash_type
    ,floor(random() * (2-1+1) +1)::int AS storage_class_id
FROM
    orca.recovery_file rf
JOIN
    orca.granules g ON (g.cumulus_granule_id = rf.granule_id)
;