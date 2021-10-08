"""
Name: post_to_catalog.py

Description:  Pulls entries from a queue and posts them to a DB.
"""
import datetime
import json
from typing import Any, List, Dict, Optional

# noinspection SpellCheckingInspection
import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from sqlalchemy import text
from sqlalchemy.future import Engine

from orca_shared.database import shared_db

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
    for record in records:
        send_record_to_database(record, engine)


def send_record_to_database(record: Dict[str, Any], engine: Engine) -> None:
    """
    Deconstructs a record to its components and calls send_values_to_database with the result.

    Args:
        record: Contains the following keys:
            'body' (str): A json string representing a dict.
                Contains key/value pairs of column names and values for those columns.
                Must match catalog_record_input.json.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    values = json.loads(record["body"])
    _CATALOG_RECORD_VALIDATE(values)
    create_status_for_job_and_files(
        values["job_id"],
        values["granule_id"],
        values["request_time"],
        values["archive_destination"],
        values["files"],
        engine,
    )


def create_catalog_records(
    engine: Engine,
) -> None:
    """
    Posts the information to the catalog database.

    Args:
        engine: The sqlalchemy engine to use for contacting the database.
    """
    # todo

    try:
        LOGGER.debug(f"Creating catalog records for TODO.")
        with engine.begin() as connection:
            connection.execute(
                post_to_catalog_sql(),
                [
                    {
                        # todo: named params matching sql
                    }
                ],
            )
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while creating statuses for job '{job_id}': {sql_ex}",
            job_id=job_id,
            sql_ex=sql_ex,
        )
        raise


def post_to_catalog_sql():
    return text(
        """
        TODO"""
    )


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
