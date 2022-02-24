"""
Name: perform_orca_reconcile.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, Union

import fastjsonschema
import orca_shared
import orca_shared.reconciliation.shared_reconciliation
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation.shared_reconciliation import (
    get_partition_name_from_bucket_name,
)
from sqlalchemy import text
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause

INPUT_JOB_ID_KEY = "jobId"
INPUT_ORCA_ARCHIVE_LOCATION_KEY = "orcaArchiveLocation"
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
    orca_shared.reconciliation.shared_reconciliation.update_job(
        job_id,
        orca_shared.reconciliation.OrcaStatus.GENERATING_REPORTS,
        datetime.now(timezone.utc).isoformat(),
        None,
        user_engine,
        LOGGER,
    )

    try:
        generate_reports(job_id, orca_archive_location, user_engine)
        orca_shared.reconciliation.shared_reconciliation.update_job(
            job_id,
            orca_shared.reconciliation.OrcaStatus.SUCCESS,
            datetime.now(timezone.utc).isoformat(),
            None,
            user_engine,
            LOGGER,
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
    Generates and posts phantom, orphan, and mismatch reports within the same transaction.

    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the bucket to generate the reports for.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Generating phantom reports for job id {job_id}.")
        partition_name = get_partition_name_from_bucket_name(orca_archive_location)
        with engine.begin() as connection:
            LOGGER.debug(f"Generating phantom reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_phantom_report with files in orca.files but NOT reconcile_s3_object
                generate_phantom_reports_sql(partition_name),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            LOGGER.debug(f"Generating orphan reports for job id {job_id}.")
            connection.execute(
                # populate reconcile_orphan_report with files in reconcile_s3_object but NOT orca.files
                generate_orphan_reports_sql(partition_name),
                [{"job_id": job_id, "orca_archive_location": orca_archive_location}],
            )
            # populate reconcile_mismatch_report with files in both, but with a difference
            generate_mismatch_reports(job_id, orca_archive_location, partition_name, connection)
    except Exception as sql_ex:
        LOGGER.error(f"Error while generating reports for job {job_id}: {sql_ex}")
        raise


def generate_phantom_reports_sql(partition_name: str) -> TextClause:
    """
    SQL for generating reports on files in the Orca catalog, but not S3.
    """
    return text(
        f"""
        WITH 
            phantom_files AS (
                SELECT files.*
                FROM
                    files
                LEFT OUTER JOIN {partition_name} USING (key_path)
                WHERE
                    files.orca_archive_location = :orca_archive_location AND
                    {partition_name}.key_path IS NULL
            ),
            phantom_reports AS (SELECT * FROM phantom_files
            INNER JOIN granules ON (phantom_files.granule_id=granules.id))
        INSERT INTO reconcile_phantom_report (job_id, collection_id, granule_id, filename, key_path, orca_etag, orca_last_update, orca_size)
            SELECT :job_id, collection_id, cumulus_granule_id, name, key_path, etag, last_update, size_in_bytes
            FROM phantom_reports"""
    )


def generate_orphan_reports_sql(partition_name: str) -> TextClause:
    """
    SQL for generating reports on files in S3, but not the Orca catalog.
    """
    return text(
        f"""
        WITH 
            orphan_reports AS (
                SELECT {partition_name}.*
                FROM
                    {partition_name}
                LEFT OUTER JOIN files USING (key_path)
                WHERE
                    files.orca_archive_location = :orca_archive_location AND
                    files.key_path IS NULL
            )
        INSERT INTO reconcile_orphan_report (job_id, key_path, etag, last_update, size_in_bytes, storage_class)
            SELECT :job_id, key_path, etag, last_update, size_in_bytes, storage_class
            FROM orphan_reports"""
    )


PAGE_SIZE = 500
discrepancy_checks = ["etag", "last_update", "size_in_bytes"]
def generate_mismatch_reports(job_id: int, orca_archive_location: str, partition_name: str, connection):
    """
    Generates and posts phantom, orphan, and mismatch reports within the same transaction.

    Args:
        job_id: The id of the job containing s3 inventory info.
        orca_archive_location: The name of the bucket to generate the reports for.
        partition_name: The name of the partition to retrieve s3 information from.
        connection: The sqlalchemy connection to use for contacting the database.
    """
    another_page = True  # Indicates if there may be another page in Postgres
    page_index = 0
    while another_page:
        LOGGER.debug(
            f"Generating mismatch reports for job id {job_id}, page {page_index}."
        )
        mismatches = connection.execute(
            get_mismatches_sql(partition_name),
            [
                {
                    "orca_archive_location": orca_archive_location,
                    "page_index": page_index,
                    "page_size": PAGE_SIZE,
                }
            ],
        )
        another_page = False
        mismatch_insert_params = []
        for mismatch in mismatches:
            discrepancies = []
            for discrepancy_check in discrepancy_checks:
                if (
                        mismatch[f"s3_{discrepancy_check}"]
                        != mismatch[f"orca_{discrepancy_check}"]
                ):
                    discrepancies.append(discrepancy_check)
            params = {
                "job_id": job_id,
                "collection_id": mismatch["collection_id"],
                "granule_id": mismatch["granule_id"],
                "filename": mismatch["filename"],
                "key_path": mismatch["key_path"],
                "cumulus_archive_location": mismatch[
                    "cumulus_archive_location"
                ],
                "orca_etag": mismatch["orca_etag"],
                "s3_etag": mismatch["s3_etag"],
                "orca_last_update": mismatch["orca_last_update"],
                "s3_last_update": mismatch["s3_last_update"],
                "orca_size_in_bytes": mismatch["orca_size_in_bytes"],
                "s3_size_in_bytes": mismatch["s3_size_in_bytes"],
                "discrepancy_type": ", ".join(discrepancies),
            }
            mismatch_insert_params.append(params)

        if any(mismatch_insert_params):
            if len(mismatch_insert_params) == PAGE_SIZE:
                another_page = True
            LOGGER.debug(
                f"Inserting mismatch reports for job id {job_id}, page {page_index}."
            )
            connection.execute(insert_mismatch_sql(), mismatch_insert_params)
        page_index = page_index + 1


def get_mismatches_sql(partition_name: str) -> TextClause:
    """
    SQL for retrieving mismatches between entries in S3 and the Orca catalog.
    """
    return text(
        f"""
        SELECT
            granules.collection_id, 
            granules.cumulus_granule_id as granule_id, 
            files.name as filename, 
            files.key_path,
             files.cumulus_archive_location, 
            files.etag as orca_etag, 
            {partition_name}.etag as s3_etag,
            granules.last_update as orca_last_update,
            {partition_name}.last_update as s3_last_update,
            files.size_in_bytes as orca_size_in_bytes, 
            {partition_name}.size_in_bytes as s3_size_in_bytes
        FROM {partition_name}
        INNER JOIN files USING (key_path)
        INNER JOIN granules ON (files.granule_id=granules.id)
        WHERE
            files.orca_archive_location = :orca_archive_location
            AND
            (
                files.etag != {partition_name}.etag OR
                granules.last_update != {partition_name}.last_update OR
                files.size_in_bytes != {partition_name}.size_in_bytes
            )
        LIMIT :page_size
        OFFSET :page_index*:page_size"""
    )


def insert_mismatch_sql() -> TextClause:
    """
    SQL for posting a mismatch to reconcile_catalog_mismatch_report.
    """
    return text(
        """
        INSERT INTO reconcile_catalog_mismatch_report
        VALUES(:job_id, :collection_id, :granule_id, :filename, :key_path, :cumulus_archive_location, :orca_etag, :s3_etag,
            :orca_last_update, :s3_last_update, :orca_size_in_bytes, :s3_size_in_bytes, :discrepancy_type)
        """
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
