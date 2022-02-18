"""
Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.
"""
import json
from datetime import datetime, timezone
from typing import Dict, List, Any

import fastjsonschema
import orca_shared
import orca_shared.reconciliation.shared_reconciliation
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation.shared_reconciliation import (
    OrcaStatus,
    get_partition_name_from_bucket_name,
)
from sqlalchemy import text
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause

INPUT_JOB_ID_KEY = "jobId"
OUTPUT_JOB_ID_KEY = "jobId"

LOGGER = CumulusLogger()
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
    with open("schemas/output.json", "r") as raw_schema:
        _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
        job_id: int,
        db_connect_info: Dict,
) -> Dict[str, Any]:
    """
    Reads the record to find the location of manifest.json, then uses that information to spawn of business logic
    for pulling manifest's data into sql.
    Args:
        job_id: The id of the job containing s3 inventory info.
        db_connect_info: See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """

    user_engine = shared_db.get_user_connection(db_connect_info)
    orca_shared.reconciliation.shared_reconciliation.update_job(
        job_id,
        orca_shared.reconciliation.OrcaStatus.GETTING_S3_LIST,
        datetime.now(timezone.utc).isoformat(),
        None,
        user_engine,
        LOGGER
    )

    try:
        # todo: populate reconcile_orphan_report with files in reconcile_s3_object but NOT orca.files
        # todo: populate reconcile_phantom_report with files in orca.files but NOT reconcile_s3_object
        # todo: populate reconcile_mismatch_report with files in both, but with a difference
        orca_shared.reconciliation.shared_reconciliation.update_job(
            job_id,
            orca_shared.reconciliation.OrcaStatus.SUCCESS,
            datetime.now(timezone.utc).isoformat(),
            None,
            user_engine,
            LOGGER
        )
    except Exception as fatal_exception:
        # On error, set job status to failure.
        LOGGER.error(f"Encountered a fatal error: {fatal_exception}")
        # noinspection PyArgumentList
        orca_shared.reconciliation.shared_reconciliation.update_job(
            job_id,
            orca_shared.reconciliation.OrcaStatus.ERROR,
            datetime.now(timezone.utc).isoformat(),
            str(fatal_exception),
            user_engine,
            LOGGER,
        )
        raise
    return {OUTPUT_JOB_ID_KEY: job_id}


@shared_db.retry_operational_error()
def generate_reports(job_id: int, orca_archive_location: str, engine: Engine) -> None:
    """
    todo

    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the bucket to generate the reports for.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Generating reports for job id {job_id}.")
        partition_name = get_partition_name_from_bucket_name(orca_archive_location)
        with engine.begin() as connection:
            connection.execute(
                generate_reports_sql(),
                [{}],
            )
    except Exception as sql_ex:
        LOGGER.error(
            f"Error while generating reports for job {job_id}: {sql_ex}"
        )
        raise


def generate_reports_sql(report_table_name: str) -> TextClause:
    """
    SQL for generating reports on differences between s3 and Orca catalog.
    """
    return text(
        # todo
        f"""
        INSERT INTO orca.{report_table_name} (job_id, orca_archive_location, key_path, etag, last_update, size_in_bytes, storage_class, delete_flag)
            SELECT :job_id, orca_archive_location, key_path, etag, last_update, size_in_bytes, storage_class, delete_flag
            FROM s3_import
            WHERE is_latest = TRUE
        """
    )


def handler(event: Dict[str, int], context) -> Dict[str, Any]:
    """
    Lambda handler. Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.
    Args:
        event: See input.json for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    _INPUT_VALIDATE(event)

    job_id = event[INPUT_JOB_ID_KEY]

    db_connect_info = shared_db.get_configuration()

    result = task(
        job_id, db_connect_info
    )
    _OUTPUT_VALIDATE(result)
    return result
