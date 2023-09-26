"""
Name: get_current_archive_list.py

Description: Receives a list of s3 events from an SQS queue,
and loads the s3 inventory specified into postgres.
"""
import json
import os
import os.path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

# noinspection SpellCheckingInspection,PyPackageRequirements
import boto3
import fastjsonschema as fastjsonschema
import orca_shared.reconciliation.shared_reconciliation
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation import (
    OrcaStatus,
    get_partition_name_from_bucket_name,
    update_job,
)
from sqlalchemy import text
from sqlalchemy.future import Engine

OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY = "INTERNAL_REPORT_QUEUE_URL"
OS_ENVIRON_S3_CREDENTIALS_SECRET_ARN_KEY = "S3_CREDENTIALS_SECRET_ARN"  # nosec
OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY = "DB_CONNECT_INFO_SECRET_ARN"  # nosec

S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY = "s3_access_key"
S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY = "s3_secret_key"  # nosec

MESSAGES_KEY = "Messages"
RECORD_REPORT_BUCKET_REGION_KEY = "reportBucketRegion"
RECORD_REPORT_BUCKET_NAME_KEY = "reportBucketName"
RECORD_MANIFEST_KEY_KEY = "manifestKey"

MANIFEST_SOURCE_BUCKET_KEY = "sourceBucket"
MANIFEST_FILE_SCHEMA_KEY = "fileSchema"
MANIFEST_CREATION_TIMESTAMP_KEY = "creationTimestamp"
MANIFEST_FILES_KEY = "files"
FILES_KEY_KEY = "key"

OUTPUT_JOB_ID_KEY = "jobId"
OUTPUT_ORCA_ARCHIVE_LOCATION_KEY = "orcaArchiveLocation"
OUTPUT_RECEIPT_HANDLE_KEY = "messageReceiptHandle"

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
    report_bucket_region: str,
    report_bucket_name: str,
    manifest_key: str,
    s3_access_key: str,
    s3_secret_key: str,
    db_connect_info: Dict,
) -> Dict[str, Any]:
    """
    Reads the record to find the location of manifest.json,
    then uses that information to spawn of business logic
    for pulling manifest's data into sql.

    Args:
        report_bucket_region: The region the report bucket resides in.
        report_bucket_name: The name of the report bucket.
        manifest_key: The key/path to the manifest within the report bucket.
        s3_access_key: The access key that, when paired with s3_secret_key,
        allows postgres to access s3.
        s3_secret_key: The secret key that, when paired with s3_access_key,
        allows postgres to access s3.
        db_connect_info: See shared_db.py's get_configuration for further details.

    Returns: See output.json for details.
    """
    # Filter out non-manifest files. Should be done prior to this.
    filename = os.path.basename(manifest_key)

    if filename != "manifest.json":
        LOGGER.error(f"Illegal file '{filename}'. Must be 'manifest.json'")
        raise Exception(f"Illegal file '{filename}'. Must be 'manifest.json'")

    # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-inventory-location.html
    # for json example.
    manifest = get_manifest(
        manifest_key,
        report_bucket_name,
        report_bucket_region,
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
            report_bucket_name,
            report_bucket_region,
            # There will probably only be one file, but AWS leaves the option open.
            [file[FILES_KEY_KEY] for file in manifest[MANIFEST_FILES_KEY]],
            manifest[MANIFEST_FILE_SCHEMA_KEY],
            job_id,
            admin_engine,
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

    return {
        OUTPUT_JOB_ID_KEY: job_id,
        OUTPUT_ORCA_ARCHIVE_LOCATION_KEY: manifest[MANIFEST_SOURCE_BUCKET_KEY],
    }


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
        LOGGER.debug("Creating status for job.")
        with engine.begin() as connection:
            # Within this transaction import the csv and update the job status
            now = datetime.now(timezone.utc)
            rows = connection.execute(
                create_job_sql(),
                [
                    {
                        "orca_archive_location": orca_archive_location,
                        "inventory_creation_time": inventory_creation_time,
                        "status_id": OrcaStatus.GETTING_S3_LIST.value,
                        "start_time": now,
                        "last_update": now,
                        "end_time": None,
                        "error_message": None,
                    }
                ],
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while creating job: {sql_ex}")
        raise

    return rows.fetchone()["id"]


def create_job_sql() -> text:  # pragma: no cover
    return text(
        """
        INSERT INTO reconcile_job
            ("orca_archive_location", "inventory_creation_time",
            "status_id", "start_time", "last_update", "end_time",
            "error_message")
        VALUES
            (:orca_archive_location, :inventory_creation_time,
            :status_id, :start_time, :last_update, :end_time,
            :error_message)
        RETURNING
            id"""
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
        LOGGER.error(
            f"Error while truncating bucket '{orca_archive_location}': {sql_ex}"
        )
        raise


def truncate_s3_partition_sql(partition_name: str) -> text:
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
    report_bucket_name: str,
    report_bucket_region: str,
    csv_key_paths: List[str],
    manifest_file_schema: str,
    job_id: int,
    engine: Engine,
) -> None:
    """
    Constructs a temporary table capable of holding full data from s3 inventory report,
    triggers load into that table, then moves that data into the proper partition.

    Args:
        s3_access_key: The access key that, when paired with s3_secret_key,
        allows postgres to access s3.
        s3_secret_key: The secret key that, when paired with s3_access_key,
        allows postgres to access s3.
        report_bucket_name: The name of the bucket the csv is located in.
        report_bucket_region: The name of the region the report bucket resides in.
        csv_key_paths: The paths of the csvs within the report bucket.
        manifest_file_schema: The string representing columns present in the csv.
        job_id: The id of the job to associate info with.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    try:
        LOGGER.debug(f"Pulling in s3 inventory records for job {job_id}.")
        temporary_s3_column_list = generate_temporary_s3_column_list(
            manifest_file_schema
        )
        with engine.begin() as connection:
            # Within this transaction import the csv and update the job status
            connection.execute(
                create_temporary_table_sql(temporary_s3_column_list),
                [{}],
            )
            for csv_key_path in csv_key_paths:
                if not csv_key_path.endswith(".csv.gz"):
                    raise Exception(f"Cannot handle file extension on '{csv_key_path}'")
                # Set the required metadata
                add_metadata_to_gzip(report_bucket_name, csv_key_path)
                # Have postgres load the csv
                LOGGER.debug(f"Loading CSV {csv_key_path} for job {job_id}.")
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
            # Now that all csvs are loaded, pull them into main db from temporary table
            LOGGER.debug(f"Translating data to Orca format for job {job_id}.")
            connection.execute(
                translate_s3_import_to_partitioned_data_sql(),
                [
                    {
                        "job_id": job_id,
                    }
                ],
            )
            # Update job status
            LOGGER.debug(f"Posting successful status for job {job_id}.")
            orca_shared.reconciliation.shared_reconciliation.update_job(
                job_id,
                OrcaStatus.STAGED,
                None,
                engine,
            )
    except Exception as sql_ex:
        LOGGER.error(f"Error while processing job '{job_id}': {sql_ex}")
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


def generate_temporary_s3_column_list(manifest_file_schema: str) -> str:
    """
    Creates a list of columns that matches the order of columns in the manifest.
    Columns used by our database are given standardized names.
    Args:
        manifest_file_schema: An ordered CSV representing columns
        in the CSV the manifest points to.

    Returns: A string representing SQL columns to create.
        Columns required for import but unused by orca will be filled in with `junk` values.
        For example, 'orca_archive_location text, key_path text, size_in_bytes bigint,
        last_update timestamptz, etag text,storage_class text, junk7 text, junk8 text,
        junk9 text, junk10 text, junk11 text, junk12 text, junk13 text'

    """
    # Keys indicate columns in the s3 inventory csv.
    # Values indicate the corresponding column in orca.reconcile_s3_object
    column_mappings = {
        "Bucket": "orca_archive_location text",
        "Key": "key_path text",
        "Size": "size_in_bytes bigint",
        "LastModifiedDate": "last_update timestamptz",
        "ETag": "etag text",
        "StorageClass": "storage_class text",
        "IsDeleteMarker": "delete_marker bool",
        "IsLatest": "is_latest bool",
    }
    manifest_file_schema = manifest_file_schema.replace(" ", "")
    columns_in_csv = manifest_file_schema.split(",")
    columns_in_postgres = []
    for column_index, column_in_csv in enumerate(columns_in_csv):
        postgres_column_name = column_mappings.get(
            column_in_csv, "junk" + str(column_index) + " text"
        )
        columns_in_postgres.append(postgres_column_name)
    return ", ".join(columns_in_postgres)


# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html
# To make runnable, run 'CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;'
def create_temporary_table_sql(temporary_s3_column_list: str) -> text:
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


def trigger_csv_load_from_s3_sql() -> text:  # pragma: no cover
    """
    SQL for telling postgres where/how to copy in the s3 inventory data.
    """
    return text(
        """
        SELECT aws_s3.table_import_from_s3(
            's3_import',
            '',
            '(format csv, FORCE_NULL(size_in_bytes))',
            :report_bucket_name,
            :csv_key_path,
            :report_bucket_region,
            :s3_access_key,
            :s3_secret_key,
            ''
        )
        """
    )


def translate_s3_import_to_partitioned_data_sql() -> text:  # pragma: no cover
    """
    SQL for translating between the temporary table and Orca table.
    """
    return text(  # nosec  # noqa
        """
        INSERT INTO orca.reconcile_s3_object (
                job_id,
                orca_archive_location,
                key_path,
                etag,
                last_update,
                size_in_bytes,
                storage_class,
                delete_marker)
            SELECT
            :job_id,
            orca_archive_location,
            key_path,
            CONCAT('"', etag, '"') as etag, /* copy_to_glacier's AWS call presently
                wraps this in quotes. Seems like a bug, but is shown on
                https://boto3.amazonaws.com/v1/documentation/api/latest/
                reference/services/s3.html#S3.Client.list_object_versions */
            last_update,
            COALESCE(size_in_bytes, 0),
            storage_class, delete_marker
            FROM s3_import
            WHERE is_latest = TRUE
        """
    )


def get_s3_credentials_from_secrets_manager(s3_credentials_secret_arn: str) -> tuple:
    """
    Gets the s3 secret from the given arn and decompiles into two strings.
    Args:
        s3_credentials_secret_arn: The arn of the secret containing s3 credentials.

    Returns:
        A tuple consisting of
            (str) An access key
            (str) A secret key
    """
    secretsmanager = boto3.client(
        "secretsmanager", region_name=os.environ["AWS_REGION"]
    )
    LOGGER.debug(f"Getting secret '{s3_credentials_secret_arn}'")
    s3_credentials = json.loads(
        secretsmanager.get_secret_value(SecretId=s3_credentials_secret_arn)["SecretString"]
    )
    s3_access_key = s3_credentials.get(S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY, None)
    if s3_access_key is None or len(s3_access_key) == 0:
        LOGGER.error(f"{S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY} secret is not set.")
        raise ValueError(f"{S3_ACCESS_CREDENTIALS_ACCESS_KEY_KEY} secret is not set.")
    s3_secret_key = s3_credentials.get(S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY, None)
    if s3_secret_key is None or len(s3_secret_key) == 0:
        LOGGER.error(f"{S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY} secret is not set.")
        raise ValueError(f"{S3_ACCESS_CREDENTIALS_SECRET_KEY_KEY} secret is not set.")

    return s3_access_key, s3_secret_key


@dataclass(frozen=True)
class MessageData:
    """
    Data class that manages the message information needed to perform the task.

    Contains:
        report_bucket_region: (str) The region the report bucket resides in
        report_bucket_name: (str) The name of the report bucket
        manifest_key: (str) The key/path to the manifest within the report bucket
        message_receipt: (str) The receipt handle of the message in the queue
    """
    report_bucket_region: str
    report_bucket_name: str
    manifest_key: str
    message_receipt_handle: str


def get_message_from_queue(
    internal_report_queue_url: str,
) -> MessageData:
    """
    Gets a message from the queue and formats it into input.json schema.
    Args:
        internal_report_queue_url: The url of the queue containing the message.

    Returns:
        A MessageData consisting of the relevant data.
    """
    aws_client_sqs = boto3.client("sqs")
    sqs_response = aws_client_sqs.receive_message(
        QueueUrl=internal_report_queue_url,
        MaxNumberOfMessages=1,
    )
    if MESSAGES_KEY not in sqs_response.keys():
        raise Exception("No messages in queue.")
    message = sqs_response[MESSAGES_KEY][0]
    record = json.loads(message["Body"])
    _INPUT_VALIDATE(record)
    return MessageData(
        record[RECORD_REPORT_BUCKET_REGION_KEY],
        record[RECORD_REPORT_BUCKET_NAME_KEY],
        record[RECORD_MANIFEST_KEY_KEY],
        message["ReceiptHandle"],
    )


def check_env_variable(env_name: str) -> str:
    """
    Checks for the lambda environment variable.

    Args:
        env_name (str): The environment variable name set in lambda configuration.

    Raises: KeyError in case the environment variable is not found.
    """
    try:
        env_value = os.environ[env_name]
        if len(env_value) == 0 or env_value is None:
            raise KeyError(f"Empty value for {env_name}")
    except KeyError:
        LOGGER.error(f"{env_name} environment value not found.")
        raise

    return env_value


def handler(event: Dict[str, List], context) -> Dict[str, Any]:
    """
    Lambda handler. Receives a list of s3 events from an SQS queue,
    and loads the s3 inventory specified into postgres.

    Args:
        event: Unused. Data is pulled in by contacting INTERNAL_REPORT_QUEUE_URL
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        INTERNAL_REPORT_QUEUE_URL (string):
            The URL of the SQS queue the job came from.
        S3_CREDENTIALS_SECRET_ARN (string):
            The ARN of the secret containing s3 credentials.
        DB_CONNECT_INFO_SECRET_ARN (string):
            Secret ARN of the AWS secretsmanager secret for connecting to the database.
            See shared_db.py's get_configuration for further details.

    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    # getting the env variables
    s3_access_key, s3_secret_key = get_s3_credentials_from_secrets_manager(
        check_env_variable(OS_ENVIRON_S3_CREDENTIALS_SECRET_ARN_KEY))
    db_connect_info = shared_db.get_configuration(
        check_env_variable(OS_ENVIRON_DB_CONNECT_INFO_SECRET_ARN_KEY))
    message_data = get_message_from_queue(
        check_env_variable(OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY))

    result = task(
        message_data.report_bucket_region,
        message_data.report_bucket_name,
        message_data.manifest_key,
        s3_access_key,
        s3_secret_key,
        db_connect_info,
    )
    result[OUTPUT_RECEIPT_HANDLE_KEY] = message_data.message_receipt_handle
    _OUTPUT_VALIDATE(result)
    return result
