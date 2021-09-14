"""
Name: post_to_database.py

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

from orca_shared import shared_db
from orca_shared.shared_recovery import RequestMethod, OrcaStatus

LOGGER = CumulusLogger()
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/new_job_input.json", "r") as raw_schema:
        _NEW_JOB_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
    with open("schemas/update_file_input.json", "r") as raw_schema:
        _UPDATE_FILE_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
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
                Must match one of the schemas.
            'messageAttributes' (dict): Contains the following keys:
                'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
        engine: The sqlalchemy engine to use for contacting the database.
    """
    values = json.loads(record['body'])
    request_method = RequestMethod(record['messageAttributes']['RequestMethod']['stringValue'])
    if request_method == RequestMethod.NEW_JOB:
        _NEW_JOB_VALIDATE(values)
        create_status_for_job_and_files(values['job_id'],
                                        values['granule_id'],
                                        values['request_time'],
                                        values['archive_destination'],
                                        values['files'],
                                        engine)
    elif request_method == RequestMethod.UPDATE_FILE:
        _UPDATE_FILE_VALIDATE(values)
        update_status_for_file(values['job_id'],
                               values['granule_id'],
                               values['filename'],
                               values['last_update'],
                               values.get('completion_time', None),
                               values['status_id'],
                               values.get('error_message', None),
                               engine)
    else:
        error = ValueError(f"RequestMethod '{request_method.value}' not found.")
        LOGGER.critical(error)
        raise error


def create_status_for_job_and_files(job_id: str,
                                    granule_id: str,
                                    request_time: str,
                                    archive_destination: str,
                                    files: List[Dict[str, Any]],
                                    engine: Engine) -> None:
    """
    Posts the entry for the job, followed by individual entries for each file.

    Args:
        job_id: The unique identifier used for tracking requests.
        granule_id: The id of the granule being restored.
        archive_destination: The S3 bucket destination of where the data is archived.
        request_time: The time the restore was requested in utc and iso-format.
        files: A List of Dicts with the following keys:
            'filename' (str)
            'key_path' (str)
            'restore_destination' (str)
            'status_id' (int)
            'error_message' (str, Optional)
            'request_time' (str)
            'last_update' (str)
            'completion_time' (str, Optional)
        engine: The sqlalchemy engine to use for contacting the database.
    """
    found_pending = False
    job_completion_time = None
    file_parameters = []
    for file in files:
        if file['status_id'] == OrcaStatus.PENDING.value:
            found_pending = True
        elif file['status_id'] == OrcaStatus.FAILED.value:
            file_completion_time = datetime.datetime.fromisoformat(file['completion_time'])
            if job_completion_time is None:
                job_completion_time = file_completion_time
            else:
                job_completion_time = max(job_completion_time,
                                          file_completion_time)
        else:
            error = ValueError(f"Status ID '{file['status_id']}' not allowed for new status.")
            LOGGER.critical(error)
            raise error
        file_parameters.append({'job_id': job_id, 'granule_id': granule_id, 'filename': file['filename'],
                                'key_path': file['key_path'], 'restore_destination': file['restore_destination'],
                                'multipart_chunksize_mb': file['multipart_chunksize_mb'],
                                'status_id': file['status_id'], 'error_message': file.get('error_message', None),
                                'request_time': file['request_time'], 'last_update': file['last_update'],
                                'completion_time': file.get('completion_time', None)})

    if found_pending:
        # Most jobs will be this. Some files are still pending.
        job_status = OrcaStatus.PENDING
        job_completion_time = None
    else:
        # All files failed during recovery request.
        job_status = OrcaStatus.FAILED
        job_completion_time = job_completion_time.isoformat().__str__()

    try:
        LOGGER.debug(f"Creating recovery records for job_id {job_id}.")
        with engine.begin() as connection:
            connection.execute(create_job_sql(),
                               [{'job_id': job_id, 'granule_id': granule_id, 'status_id': job_status.value,
                                 'request_time': request_time,
                                 'completion_time': job_completion_time,
                                 'archive_destination': archive_destination}])
            connection.execute(create_file_sql(), file_parameters)
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("Error while creating statuses for job '{job_id}': {sql_ex}", job_id=job_id, sql_ex=sql_ex)
        raise


def update_status_for_file(job_id: str,
                           granule_id: str,
                           filename: str,
                           last_update: str,
                           completion_time: Optional[str],
                           status_id: int,
                           error_message: Optional[str],
                           engine: Engine) -> None:
    """
    Updates a given file's status entry, modifying the job if all files for that job have advanced in status.

    Args:
        job_id: The unique identifier used for tracking requests.
        granule_id: The id of the granule being restored.
        filename: The name of the file being copied.
        last_update: The time this status update occurred, in UTC iso-format.
        completion_time: The completion time, in UTC iso-format.
        status_id: Defines the status id used in the ORCA Recovery database.
        error_message: message displayed on error.

        engine: The sqlalchemy engine to use for contacting the database.
    """
    file_parameters = {'status_id': status_id, 'last_update': last_update,
                       'completion_time': completion_time, 'error_message': error_message,
                       'job_id': job_id, 'granule_id': granule_id, 'filename': filename}
    job_parameters = {'job_id': job_id, 'granule_id': granule_id}
    try:
        LOGGER.debug(f"Updating status for recovery record job_id {job_id} granule_id {granule_id} and file {filename}." )
        with engine.begin() as connection:
            connection.execute(update_file_sql(), file_parameters)
            connection.execute(update_job_sql(), job_parameters)
    except Exception as sql_ex:
        # Can't use f"" because of '{}' bug in CumulusLogger.
        LOGGER.error("Error while creating statuses for job '{job_id}': {sql_ex}", job_id=job_id, sql_ex=sql_ex)
        raise


def create_job_sql():
    return text("""
        INSERT INTO recovery_job
            ("job_id", "granule_id", "status_id", "request_time", "completion_time", "archive_destination")
        VALUES
            (:job_id, :granule_id, :status_id, :request_time, :completion_time, :archive_destination)""")


def create_file_sql():
    return text("""
        INSERT INTO recovery_file
            ("job_id", "granule_id", "filename", "key_path", "restore_destination", "multipart_chunksize_mb", 
            "status_id", "error_message", "request_time", "last_update", "completion_time")
        VALUES
            (:job_id, :granule_id, :filename, :key_path, :restore_destination, :multipart_chunksize_mb, :status_id, 
            :error_message, :request_time, :last_update, :completion_time)""")


def update_file_sql():
    return text("""
        UPDATE recovery_file
        SET status_id = :status_id, last_update = :last_update, completion_time = :completion_time,
            error_message = :error_message
        WHERE job_id = :job_id AND granule_id = :granule_id AND filename = :filename""")


def update_job_sql():
    return text("""
        with granule_status as (
            SELECT
                job_id,
                granule_id,
                MIN(status_id) AS status_id,
                CASE
                    WHEN MIN(status_id) IN (3, 4) THEN MAX(completion_time)
                    ELSE NULL
                END AS completion_time
            FROM
                recovery_file
            WHERE
                job_id = :job_id
            AND
                granule_id = :granule_id
            GROUP BY job_id, granule_id
        )
        UPDATE
            recovery_job
        SET
            status_id = granule_status.status_id,
            completion_time = granule_status.completion_time
        FROM
            granule_status
        WHERE
            recovery_job.job_id = granule_status.job_id
        AND
            recovery_job.granule_id = granule_status.granule_id""")


def handler(event: Dict[str, List], context) -> None:
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: A dict with the following keys:
            'Records' (List): A list of dicts with the following keys:
                'messageId' (str)
                'receiptHandle' (str)
                'body' (str): A json string representing a dict.
                    See files in schemas for details.
                'attributes' (Dict)
                'messageAttributes' (Dict): A dict with the following keys defined in the functions that write to queue.
                    'RequestMethod' (str): Matches to a shared_recovery.RequestMethod.
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

    db_connect_info = shared_db.get_configuration()

    task(event['Records'], db_connect_info)
