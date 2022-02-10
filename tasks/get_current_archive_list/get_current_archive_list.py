"""
Name: get_current_archive_list.py

Description:  Pulls entries from a queue and posts them to a DB.
"""
import json
import os.path
from datetime import datetime, timezone
from typing import Any, List, Dict

# noinspection SpellCheckingInspection,PyPackageRequirements
import boto3
import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation.shared_reconciliation import (
    OrcaStatus,
    get_partition_name_from_bucket_name,
)
from sqlalchemy import text
from sqlalchemy.future import Engine

OS_S3_ACCESS_KEY_KEY = "S3_ACCESS_KEY"
OS_S3_SECRET_KEY_KEY = "S3_SECRET_KEY"

EVENT_RECORDS_KEY = "Records"
RECORD_AWS_REGION_KEY = "awsRegion"
RECORD_S3_KEY = "s3"
S3_BUCKET_KEY = "bucket"
BUCKET_NAME_KEY = "name"
S3_OBJECT_KEY = "object"
OBJECT_KEY_KEY = "key"

MANIFEST_SOURCE_BUCKET_KEY = "sourceBucket"
MANIFEST_FILE_SCHEMA_KEY = "fileSchema"
MANIFEST_CREATION_TIMESTAMP_KEY = "creationTimestamp"
MANIFEST_FILES_KEY = "files"
FILES_KEY_KEY = "key"

OUTPUT_JOB_ID_KEY = "jobId"

LOGGER = CumulusLogger()
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
    with open("schemas/output.json", "r") as raw_schema:
        _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    # Can't use f"" because of '{}' bug in CumulusLogger.
    LOGGER.error("Could not build schema validator: {ex}", ex=ex)
    raise


def task(
    record: Dict[str, Any],
    s3_access_key: str,
    s3_secret_key: str,
    db_connect_info: Dict,
) -> Dict[str, Any]:
    """
    Sends each individual record to send_record_to_database.

    Args:
        record: See input.json for details.
        s3_access_key: The access key that, when paired with s3_secret_key, allows postgres to access s3.
        s3_secret_key: The secret key that, when paired with s3_access_key, allows postgres to access s3.
        db_connect_info: See shared_db.py's get_configuration for further details.

    Returns: See output.json for details.
    """
    # Filter out non-manifest files
    filename = os.path.basename(record[RECORD_S3_KEY][S3_OBJECT_KEY][OBJECT_KEY_KEY])

    if filename != "manifest.json":
        LOGGER.info(f"Ignoring file '{filename}'.")
        return {OUTPUT_JOB_ID_KEY: None}  # todo: Shut down workflow.

    # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-inventory-location.html for json example.
    manifest = get_manifest(
        record[RECORD_S3_KEY][S3_OBJECT_KEY][OBJECT_KEY_KEY],
        record[RECORD_S3_KEY][S3_BUCKET_KEY][BUCKET_NAME_KEY],
        record[RECORD_AWS_REGION_KEY],
    )

    user_engine = shared_db.get_user_connection(db_connect_info)
    admin_engine = shared_db.get_admin_connection(
        db_connect_info, db_connect_info["user_database"]
    )
    # Create initial job
    # noinspection PyArgumentList
    job_id = create_job(
        manifest[MANIFEST_SOURCE_BUCKET_KEY],
        datetime.utcfromtimestamp(
            int(manifest[MANIFEST_CREATION_TIMESTAMP_KEY]) / 1000
        ).replace(tzinfo=timezone.utc),
        user_engine,
    )

    try:
        # noinspection PyArgumentList
        truncate_s3_partition(manifest[MANIFEST_SOURCE_BUCKET_KEY], admin_engine)
        # noinspection PyArgumentList
        update_job_with_s3_inventory_in_postgres(
            s3_access_key,
            s3_secret_key,
            manifest[MANIFEST_SOURCE_BUCKET_KEY],
            record[RECORD_S3_KEY][S3_BUCKET_KEY][BUCKET_NAME_KEY],
            record[RECORD_AWS_REGION_KEY],
            # There will probably only be one file, but AWS leaves the option open.
            [file[FILES_KEY_KEY] for file in manifest[MANIFEST_FILES_KEY]],
            manifest[MANIFEST_FILE_SCHEMA_KEY],
            job_id,
            admin_engine,
        )
    except Exception as fatal_exception:
        # On error, set job status to failure.
        LOGGER.error("Encountered a fatal error: {ex}", ex=fatal_exception)
        # noinspection PyArgumentList
        update_job_with_failure(job_id, str(fatal_exception), user_engine)
        raise

    return {OUTPUT_JOB_ID_KEY: job_id}


def get_manifest(
    manifest_key_path: str, report_bucket_name: str, report_bucket_region: str
) -> Dict[str, Any]:
    """

    Args:
        manifest_key_path: The full path within the s3 bucket to the manifest.
        report_bucket_name: The name of the bucket the manifest is located in.
        report_bucket_region: The name of the region the report bucket resides in.

    Returns: The key of the csv specified in the manifest.
    """
    s3_client = boto3.client("s3", region_name=report_bucket_region)
    file_object = s3_client.get_object(Bucket=report_bucket_name, Key=manifest_key_path)
    file_data = file_object["Body"].read()
    file_str = file_data.decode("utf-8")
    manifest = json.loads(file_str)
    return manifest


@shared_db.retry_operational_error()
def create_job(
    orca_archive_location: str, inventory_creation_time: datetime, engine: Engine
) -> int:
    """
    Creates the initial status entry for a job.

    Args:
        orca_archive_location: The name of the bucket to generate the reports for.
        inventory_creation_time: The time the s3 Inventory report was created.
        engine: The sqlalchemy engine to use for contacting the database.

    Returns: The auto-incremented job_id from the database.
    """
    try:
        LOGGER.debug(f"Creating status for job.")
        with engine.begin() as connection:
            # Within this transaction import the csv and update the job status
            now = datetime.now(timezone.utc).isoformat()
            rows = connection.execute(
                create_job_sql(),
                [
                    {
                        "orca_archive_location": orca_archive_location,
                        "inventory_creation_time": inventory_creation_time,
                        "status_id": OrcaStatus.STAGED.value,
                        "start_time": now,
                        "last_update": now,
                        "end_time": None,
                        "error_message": None,
                    }
                ],
            )
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while creating job: {sql_ex}",
            sql_ex=sql_ex,
        )
        raise

    for row in rows:  # Easiest way to get first row.
        return row["id"]


def create_job_sql():
    return text(
        """
        INSERT INTO reconcile_job
            ("orca_archive_location", "inventory_creation_time", "status_id", "start_time", "last_update", "end_time", 
            "error_message")
        VALUES
            (:orca_archive_location, :inventory_creation_time, :status_id, :start_time, :last_update, :end_time, 
            :error_message)
        RETURNING
            id"""
    )


@shared_db.retry_operational_error()
def update_job_with_failure(job_id: int, error_message: str, engine: Engine) -> None:
    """
    Updates the status entry for a job.

    Args:
        job_id: The id of the job to associate info with.
        error_message: The error to post to the job.
        engine: The sqlalchemy engine to use for contacting the database.

    """
    try:
        LOGGER.debug(f"Creating reconcile records for job {job_id}.")
        with engine.begin() as connection:
            now = datetime.now(timezone.utc).isoformat()
            connection.execute(
                update_job_sql(),
                [
                    {
                        "id": job_id,
                        "status_id": OrcaStatus.ERROR.value,
                        "last_update": now,
                        "end_time": now,
                        "error_message": error_message,
                    }
                ],
            )
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while updating job '{job_id}': {sql_ex}",
            job_id=job_id,
            sql_ex=sql_ex,
        )
        raise


def update_job_sql():
    return text(
        """
        UPDATE
            orca.reconcile_job
        SET
            status_id = :status_id,
            last_update = :last_update,
            end_time = :end_time,
            error_message = :error_message
        WHERE
            id = :id"""
    )


@shared_db.retry_operational_error()
def truncate_s3_partition(orca_archive_location: str, engine: Engine) -> None:
    """
    Truncates the partition for the given orca_archive_location, removing its data.

    Args:
        orca_archive_location: The name of the bucket to generate the reports for.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Truncating old s3 data for bucket {orca_archive_location}.")
        partition_name = get_partition_name_from_bucket_name(orca_archive_location)
        with engine.begin() as connection:
            connection.execute(
                truncate_s3_partition_sql(partition_name),
                [{}],
            )
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while truncating bucket '{orca_archive_location}': {sql_ex}",
            orca_archive_location=orca_archive_location,
            sql_ex=sql_ex,
        )
        raise


def truncate_s3_partition_sql(partition_name: str):
    # Quickly removes data from the partition
    return text(
        f"""
        TRUNCATE TABLE orca.{partition_name}
        """
    )


@shared_db.retry_operational_error()
def update_job_with_s3_inventory_in_postgres(
    s3_access_key: str,
    s3_secret_key: str,
    orca_archive_location: str,
    report_bucket_name: str,
    report_bucket_region: str,
    csv_key_paths: str,
    manifest_file_schema: str,
    job_id: int,
    engine: Engine,
) -> None:
    """
    Deconstructs a record to its components and calls send_values_to_database with the result.

    Args:
        s3_access_key: The access key that, when paired with s3_secret_key, allows postgres to access s3.
        s3_secret_key: The secret key that, when paired with s3_access_key, allows postgres to access s3.
        orca_archive_location: The name of the bucket to generate the reports for.
        report_bucket_name: The name of the bucket the csv is located in.
        report_bucket_region: The name of the region the report bucket resides in.
        csv_key_paths: The paths of the csvs within the report bucket.
        manifest_file_schema: The string representing columns present in the csv.
        job_id: The id of the job to associate info with.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Pulling in s3 inventory records for job {job_id}.")
        with engine.begin() as connection:
            # Within this transaction import the csv and update the job status
            for csv_key_path in csv_key_paths:
                if not csv_key_path.endswith(".csv.gz"):
                    raise Exception(f"Cannot handle file extension on '{csv_key_path}'")
                # Set the required metadata
                add_metadata_to_gzip(report_bucket_name, csv_key_path)
                connection.execute(
                    create_temporary_table_sql(
                        generate_temporary_s3_column_list(manifest_file_schema)
                    ),
                    [{}],
                )
                # Have postgres load the csv
                LOGGER.debug(f"Loading CSV for job {job_id}.")
                connection.execute(
                    trigger_csv_load_from_s3_sql(),
                    [
                        {
                            "report_bucket_name": report_bucket_name,
                            "csv_key_path": csv_key_path,
                            "report_bucket_region": report_bucket_region,
                            "s3_access_key": s3_access_key,
                            "s3_secret_key": s3_secret_key,
                        }
                    ],
                )
                LOGGER.debug(f"Translating data to Orca format for job {job_id}.")
                connection.execute(
                    translate_s3_import_to_partitioned_data_sql(
                        get_partition_name_from_bucket_name(orca_archive_location)
                    ),
                    [
                        {
                            "job_id": job_id,
                        }
                    ],
                )
            # Update job status
            LOGGER.debug(f"Posting successful status for job {job_id}.")
            connection.execute(
                update_job_sql(),
                [
                    {
                        "id": job_id,
                        "status_id": OrcaStatus.STAGED.value,
                        "last_update": datetime.now(timezone.utc).isoformat(),
                        "end_time": None,
                        "error_message": None,
                    }
                ],
            )
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error(
            "Error while processing job '{job_id}': {sql_ex}",
            job_id=job_id,
            sql_ex=sql_ex,
        )
        raise


def add_metadata_to_gzip(report_bucket_name: str, gzip_key_path: str) -> None:
    """
    AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
    Must add manually.
    Args:
        report_bucket_name: The name of the bucket the csv is located in.
        gzip_key_path: The path within the bucket to the gzip file that needs metadata updated.
    """
    s3 = boto3.resource("s3")
    s3_object = s3.Object(report_bucket_name, gzip_key_path)
    # Only add if needed.
    if s3_object.content_encoding is None:
        s3_object.copy_from(
            CopySource={"Bucket": report_bucket_name, "Key": gzip_key_path},
            Metadata=s3_object.metadata,
            MetadataDirective="REPLACE",
            ContentEncoding="gzip",
        )


# Keys indicate columns in the s3 inventory csv. Values indicate the corresponding column in orca.reconcile_s3_object
column_mappings = {
    "Bucket": "orca_archive_location text",
    "Key": "key_path text",
    "Size": "size_in_bytes bigint",
    "LastModifiedDate": "last_update timestamptz",
    "ETag": "etag text",
    "StorageClass": "storage_class text",
}


def generate_temporary_s3_column_list(manifest_file_schema: str) -> str:
    """
    Creates a list of columns that matches the order of columns in the manifest.
    Columns used by our database are given standardized names.
    Args:
        manifest_file_schema: An ordered CSV representing columns in the CSV the manifest points to.

    Returns: A string representing SQL columns to create.
        Columns required for import but unused by orca will be filled in with `junk` values.
        For example, 'orca_archive_location text, key_path text, size_in_bytes bigint, last_update timestamptz, etag text, storage_class text, junk7 text, junk8 text, junk9 text, junk10 text, junk11 text, junk12 text, junk13 text, junk14 text'

    """
    column_index = 0
    manifest_file_schema = manifest_file_schema.replace(" ", "")
    columns_in_csv = manifest_file_schema.split(",")
    columns_in_postgres = []
    for column_in_csv in columns_in_csv:
        column_index = column_index + 1
        postgres_column_name = column_mappings.get(
            column_in_csv, "junk" + str(column_index) + " text"
        )
        columns_in_postgres.append(postgres_column_name)
    return ", ".join(columns_in_postgres)


# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html
# To make runnable, run 'CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;'
def create_temporary_table_sql(temporary_s3_column_list: str):
    """
    Creates a temporary table to store inventory data.
    Args:
        temporary_s3_column_list: The list of columns that need to be created to store csv data.
            Be very careful to avoid injection.
    """
    return text(
        f"""
        CREATE TEMPORARY TABLE s3_import(
            {temporary_s3_column_list}
        )
        """
    )


def trigger_csv_load_from_s3_sql():
    """
    SQL for telling postgres where/how to copy in the s3 inventory data.
    """
    return text(
        """
        SELECT aws_s3.table_import_from_s3(
            's3_import',
            '',
            '(format csv)',
            :report_bucket_name,
            :csv_key_path,
            :report_bucket_region,
            :s3_access_key,
            :s3_secret_key,
            ''
        )
        """
    )


def translate_s3_import_to_partitioned_data_sql(report_table_name: str):
    """
    SQL for translating between the temporary table and Orca table.
    """
    return text(
        f"""
        INSERT INTO orca.{report_table_name} (job_id, orca_archive_location, key_path, etag, last_update, size_in_bytes, storage_class, delete_marker)
            SELECT :job_id, orca_archive_location, key_path, etag, last_update, size_in_bytes, storage_class, false 
            FROM s3_import
        """
    )


def handler(event: Dict[str, List], context) -> Dict[str, Any]:
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: See input.json for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        S3_ACCESS_KEY: The access key that, when paired with s3_secret_key, allows postgres to access s3.
        S3_SECRET_KEY: The secret key that, when paired with s3_access_key, allows postgres to access s3.
        See shared_db.py's get_configuration for further details.

    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    _INPUT_VALIDATE(event)

    if len(event[EVENT_RECORDS_KEY]) != 1:
        raise ValueError(f"Must be passed a single record. Was {len(event['Records'])}")

    s3_access_key = os.environ.get(OS_S3_ACCESS_KEY_KEY, None)
    if s3_access_key is None or len(s3_access_key) == 0:
        LOGGER.error("S3_ACCESS_KEY environment variable is not set.")
        raise KeyError("S3_ACCESS_KEY environment variable is not set.")
    s3_secret_key = os.environ.get(OS_S3_SECRET_KEY_KEY, None)
    if s3_secret_key is None or len(s3_secret_key) == 0:
        LOGGER.error("S3_SECRET_KEY environment variable is not set.")
        raise KeyError("S3_SECRET_KEY environment variable is not set.")

    db_connect_info = shared_db.get_configuration()

    result = task(
        event[EVENT_RECORDS_KEY][0], s3_access_key, s3_secret_key, db_connect_info
    )
    _OUTPUT_VALIDATE(result)
    return result
