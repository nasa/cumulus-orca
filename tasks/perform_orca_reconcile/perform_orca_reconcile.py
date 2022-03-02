"""
Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.
"""
import json
from typing import Any, Dict, Union

import fastjsonschema
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation import update_job, OrcaStatus
from sqlalchemy import text
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause

INPUT_JOB_ID_KEY = "jobId"
INPUT_ORCA_ARCHIVE_LOCATION_KEY = "orcaArchiveLocation"
OUTPUT_JOB_ID_KEY = "jobId"

LOGGER = CumulusLogger(name="ORCA")
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
    orca_archive_location: str,
    db_connect_info: Dict,
) -> Dict[str, Any]:
    """
    Reads the record to find the location of manifest.json, then uses that information to spawn of business logic
    for pulling manifest's data into sql.
    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the glacier bucket the job targets.
        db_connect_info: See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """

    user_engine = shared_db.get_user_connection(db_connect_info)
    update_job(
        job_id,
        OrcaStatus.GENERATING_REPORTS,
        None,
        user_engine,
    )

    try:
        generate_reports(job_id, orca_archive_location, user_engine)
        update_job(
            job_id,
            OrcaStatus.SUCCESS,
            None,
            user_engine,
        )
    except Exception as fatal_exception:
        # On error, set job status to failure.
        LOGGER.error(f"Encountered a fatal error: {fatal_exception}")
        # noinspection PyArgumentList
        update_job(
            job_id,
            OrcaStatus.ERROR,
            str(fatal_exception),
            user_engine,
        )
        raise
    return {OUTPUT_JOB_ID_KEY: job_id}


@shared_db.retry_operational_error()
def generate_reports(job_id: int, orca_archive_location: str, engine: Engine) -> None:
    """
    Generates and posts phantom, orphan, and mismatch reports within the same transaction.

    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the bucket to generate the reports for.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Generating phantom reports for job id {job_id}.")
        with engine.begin() as connection:
            LOGGER.debug(f"Generating phantom reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_phantom_report with files in orca.files but NOT reconcile_s3_object
                generate_phantom_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            LOGGER.debug(f"Generating orphan reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_orphan_report with files in reconcile_s3_object but NOT orca.files
                generate_orphan_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            LOGGER.debug(f"Generating mismatch reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_orphan_report with files in reconcile_s3_object and orca.files but with differences.
                generate_mismatch_reports_sql(),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while generating reports for job {job_id}: {sql_ex}")
        raise


def generate_phantom_reports_sql() -> TextClause:
    """
    SQL for generating reports on files in the Orca catalog, but not S3.
    """
    return text(
        """
        WITH 
            phantom_files AS 
            (
                SELECT 
                    files.granule_id, 
                    files.name, 
                    files.key_path, 
                    files.etag, 
                    files.size_in_bytes
                FROM
                    files
                LEFT OUTER JOIN reconcile_s3_object USING 
                (
                    orca_archive_location, key_path
                )
                WHERE
                    files.orca_archive_location = :orca_archive_location AND
                    reconcile_s3_object.key_path IS NULL
            ),
            phantom_reports AS 
            (
                SELECT 
                    granule_id, 
                    collection_id, 
                    name, 
                    key_path, 
                    etag, 
                    last_update, 
                    size_in_bytes, 
                    cumulus_granule_id 
                FROM 
                    phantom_files
                INNER JOIN granules ON 
                (
                    phantom_files.granule_id=granules.id
                )
            )
        INSERT INTO reconcile_phantom_report 
        (
            job_id, 
            collection_id, 
            granule_id, 
            filename, 
            key_path, 
            orca_etag, 
            orca_last_update, 
            orca_size
        )
        SELECT 
            :job_id, 
            collection_id, 
            cumulus_granule_id, 
            name, 
            key_path, 
            etag, 
            last_update, 
            size_in_bytes
        FROM 
            phantom_reports"""
    )


def generate_orphan_reports_sql() -> TextClause:
    """
    SQL for generating reports on files in S3, but not the Orca catalog.
    """
    return text(
        f"""
        WITH 
            orphan_reports AS 
            (
                SELECT 
                    reconcile_s3_object.key_path, 
                    reconcile_s3_object.etag, 
                    reconcile_s3_object.last_update,
                    reconcile_s3_object.size_in_bytes, 
                    reconcile_s3_object.storage_class
                FROM
                    reconcile_s3_object
                LEFT OUTER JOIN files USING 
                (
                    orca_archive_location, key_path
                )
                WHERE
                    reconcile_s3_object.orca_archive_location = :orca_archive_location AND
                    files.key_path IS NULL
            )
        INSERT INTO reconcile_orphan_report 
        (
            job_id, 
            key_path, 
            etag, 
            last_update, 
            size_in_bytes, 
            storage_class
        )
            SELECT 
                :job_id, 
                key_path, 
                etag, 
                last_update, 
                size_in_bytes, 
                storage_class
            FROM 
                orphan_reports"""
    )


def generate_mismatch_reports_sql() -> TextClause:
    """
    SQL for retrieving mismatches between entries in S3 and the Orca catalog.
    """
    return text(
        f"""
        INSERT INTO orca.reconcile_catalog_mismatch_report 
        (
            job_id, 
            collection_id, 
            granule_id, 
            filename, 
            key_path, 
            cumulus_archive_location, 
            orca_etag, 
            s3_etag,
            orca_last_update, 
            s3_last_update, 
            orca_size_in_bytes, 
            s3_size_in_bytes, 
            discrepancy_type
        )
        SELECT
            :job_id,
            granules.collection_id, 
            granules.cumulus_granule_id AS granule_id, 
            files.name AS filename, 
            files.key_path,
            files.cumulus_archive_location, 
            files.etag AS orca_etag, 
            reconcile_s3_object.etag AS s3_etag,
            granules.last_update AS orca_last_update,
            reconcile_s3_object.last_update AS s3_last_update,
            files.size_in_bytes AS orca_size_in_bytes, 
            reconcile_s3_object.size_in_bytes AS s3_size_in_bytes,
            CASE 
                WHEN (files.etag != reconcile_s3_object.etag AND files.size_in_bytes != reconcile_s3_object.size_in_bytes AND files.ingest_time !=  reconcile_s3_object.last_update) 
                    THEN 'etag, size_in_bytes, last_update'
                WHEN (files.etag != reconcile_s3_object.etag AND files.size_in_bytes != reconcile_s3_object.size_in_bytes) 
                    THEN 'etag, size_in_bytes'
                WHEN (files.etag != reconcile_s3_object.etag AND files.ingest_time !=  reconcile_s3_object.last_update) 
                    THEN 'etag, last_update'
                WHEN (files.size_in_bytes != reconcile_s3_object.size_in_bytes AND files.ingest_time !=  reconcile_s3_object.last_update) 
                    THEN 'size_in_bytes, last_update'
                WHEN files.etag != reconcile_s3_object.etag 
                    THEN 'etag'
                WHEN files.size_in_bytes != reconcile_s3_object.size_in_bytes 
                    THEN 'size_in_bytes'
                WHEN files.ingest_time !=  reconcile_s3_object.last_update 
                    THEN 'last_update'
                ELSE 'UNKNOWN'
            END AS discrepancy_type
        FROM 
            reconcile_s3_object
        INNER JOIN files USING 
        (
            orca_archive_location, key_path
        )
        INNER JOIN granules ON 
        (
            files.granule_id=granules.id
        )
        WHERE
            reconcile_s3_object.orca_archive_location = :orca_archive_location
            AND
            (
                files.etag != reconcile_s3_object.etag OR
                files.ingest_time != reconcile_s3_object.last_update OR
                files.size_in_bytes != reconcile_s3_object.size_in_bytes
            )"""
    )


def handler(event: Dict[str, Union[str, int]], context) -> Dict[str, Any]:
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
    orca_archive_location = event[INPUT_ORCA_ARCHIVE_LOCATION_KEY]

    db_connect_info = shared_db.get_configuration()

    result = task(job_id, orca_archive_location, db_connect_info)
    _OUTPUT_VALIDATE(result)
    return result
