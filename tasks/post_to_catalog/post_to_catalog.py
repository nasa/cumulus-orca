"""
Name: post_to_catalog.py

Description:  Pulls entries from a queue and posts them to a DB.
"""
import json
from datetime import datetime, timezone
from typing import Any, List, Dict, Union

# noinspection SpellCheckingInspection
import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine

LOGGER = CumulusLogger()
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/catalog_record_input.json", "r") as raw_schema:
        _CATALOG_RECORD_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    # Can't use f"" because of '{}' bug in CumulusLogger.
    LOGGER.error("Could not build schema validator: {ex}", ex=ex)
    raise


def task(records: List[Dict[str, Any]], db_connect_info: Dict) -> None:
    """
    Sends each individual record to send_record_to_database.

    Args:
        records: A list of Dicts. See send_record_to_database for schema info.
        db_connect_info: See shared_db.py's get_configuration for further details.
    """
    engine = shared_db.get_user_connection(db_connect_info)
    for (
        record
    ) in (
        records
    ):  # todo: https://github.com/nasa/cumulus-orca/pull/167/commits/7ce364b7b83fc741e92c57f63e34aa2e2c55f11e ?
        send_record_to_database(record, engine)


def send_record_to_database(record: Dict[str, Any], engine: Engine) -> None:
    """
    Deconstructs a record to its components and calls create_catalog_records with the result.

    Args:
        record: Contains the following keys:
            'body' (str): A json string representing a dict.
                Contains key/value pairs of column names and values for those columns.
                Must match catalog_record_input.json.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    values = json.loads(record["body"])
    _CATALOG_RECORD_VALIDATE(values)
    create_catalog_records(
        values["provider"],
        values["collection"],
        values["granule"],
        engine,
    )


def create_catalog_records(
    provider: Dict[str, str],
    collection: Dict[str, str],
    granule: Dict[str, Union[str, List[Dict[str, Union[str, int]]]]],
    engine: Engine,
) -> None:
    """
    Posts the information to the catalog database.

    Args:
        provider: See schemas/catalog_record_input.json.
        collection: See schemas/catalog_record_input.json.
        granule: See schemas/catalog_record_input.json.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Creating catalog records for TODO.")
        with engine.begin() as connection:
            connection.execute(
                create_provider_sql(),
                [
                    {
                        "provider_id": provider["providerId"],
                        "name": provider["name"],
                    }
                ],
            )
            connection.execute(
                create_collection_sql(),
                [
                    {
                        "collection_id": collection["collectionId"],
                        "shortname": collection["shortname"],
                        "version": collection["version"],
                    }
                ],
            )
            results = connection.execute(
                create_granule_sql(),
                [
                    {
                        "collection_id": collection["collectionId"],
                        "cumulus_granule_id": granule["cumulusGranuleId"],
                        "execution_id": granule["executionId"],
                        "ingest_time": granule["ingestTime"],
                        "cumulus_create_time": granule["cumulusCreateTime"],
                        "last_update": granule["lastUpdate"],
                    }
                ],
            )

            for (
                row
            ) in (
                results
            ):  # Need loop due to limitations on the underlying object. Welcome alternatives.
                granule_id = row["id"]

            file_parameters = []
            for file in granule["files"]:
                file_parameters.append(
                    {
                        "granule_id": granule_id,
                        "name": file["name"],
                        "cumulus_archive_location": file["cumulusArchiveLocation"],
                        "orca_archive_location": file["orcaArchiveLocation"],
                        "key_path": file["keyPath"],
                        "size_in_bytes": file["sizeInBytes"],
                        "hash": file.get("hash", None),
                        "hash_type": file.get("hashType", None),
                        "version": file["version"],
                        "ingest_time": file["ingestTime"],
                        "etag": file["etag"],
                    }
                )
            if any(file_parameters):
                connection.execute(create_file_sql(), file_parameters)
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while posting provider '{provider_id}', collection '{collection_id}', "
            "granule '{cumulus_granule_id}' to inventory: {sql_ex}",
            provider_id=provider["providerId"],
            collection_id=collection["collectionId"],
            cumulus_granule_id=granule["cumulusGranuleId"],
            sql_ex=sql_ex,
        )
        raise


def create_provider_sql():
    return text(
        """
        INSERT INTO providers
            ("provider_id", "name")
        VALUES
            (:provider_id, :name)
        ON CONFLICT DO NOTHING
        """
    )


def create_collection_sql():
    return text(
        """
    INSERT INTO collections
            ("collection_id", "shortname", "version")
    VALUES
        (:collection_id, :shortname, :version)
    ON CONFLICT DO NOTHING
    """
    )


def create_granule_sql():
    return text(
        """
    INSERT INTO granules
        ("collection_id", "cumulus_granule_id", "execution_id", "ingest_time", "cumulus_create_time", "last_update")
    VALUES
        (:collection_id, :cumulus_granule_id, :execution_id, :ingest_time, :cumulus_create_time, :last_update)
    ON CONFLICT ("collection_id", "cumulus_granule_id") DO UPDATE
        SET "execution_id"=:execution_id, "last_update"=:last_update
    RETURNING id"""
    )
    # ON CONFLICT will only trigger if both collection_id and cumulus_granule_id match.


def create_file_sql():
    return text(
        """
    INSERT INTO files
        ("granule_id", "name", "orca_archive_location", "cumulus_archive_location", "key_path", "ingest_time", "etag", 
        "version", "size_in_bytes", "hash", "hash_type")
    VALUES
        (:granule_id, :name, :orca_archive_location, :cumulus_archive_location, :key_path, :ingest_time, :etag, 
        :version, :size_in_bytes, :hash, :hash_type)
    ON CONFLICT ("cumulus_archive_location", "key_path") DO UPDATE
        SET "granule_id"=:granule_id, "name"=:name, "orca_archive_location"=:orca_archive_location, 
        "ingest_time"=:ingest_time, "etag"=:etag, "version"=:version, "size_in_bytes"=:size_in_bytes, "hash"=:hash, 
        "hash_type"=:hash_type"""
    )
    # ON CONFLICT will only trigger if all listed properties match.


def handler(event: Dict[str, List], context) -> None:
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: A dict with the following keys:
            'Records' (List): A list of dicts with the following keys:
                'messageId' (str)
                'receiptHandle' (str)
                'body' (str): A json string representing a dict.
                    See catalog_record_input in schemas for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars: See shared_db.py's get_configuration for further details.
        'DATABASE_PORT' (int): Defaults to 5432
        'DATABASE_NAME' (str)
        'APPLICATION_USER' (str)
        'PREFIX' (str)
        '{prefix}-drdb-host' (str, secretsmanager)
        '{prefix}-drdb-user-pass' (str, secretsmanager)
    """
    LOGGER.setMetadata(event, context)

    # todo: Make sure this works somehow.
    db_connect_info = shared_db.get_configuration()

    task(event["Records"], db_connect_info)
