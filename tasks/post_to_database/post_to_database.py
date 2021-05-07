"""
Name: post_to_database.py

Description:  Pulls entries from a queue and posts them to a DB.
"""
import datetime
import json
from typing import Any, List, Dict, Optional

# noinspection PyUnresolvedReferences
from cumulus_logger import CumulusLogger
# todo: Auto-copy shared libs
from sqlalchemy import text

from orca_shared import shared_db, shared_recovery
from orca_shared.shared_recovery import RequestMethod, OrcaStatus

LOGGER = CumulusLogger()


def task(records: List[Dict[str, Any]], db_connect_info: Dict):
    for record in records:
        send_record_to_database(record, db_connect_info)


def send_record_to_database(record: Dict[str, Any], db_connect_info: Dict) -> None:
    """
    Deconstructs a record to its components and calls send_values_to_database with the result.

    Args:
        record: Contains the following keys:
            'body' (str): A json string representing a dict.
                Contains key/value pairs of column names and values for those columns.
            'messageAttributes' (dict): Contains the following keys:
                'TableName' (str): The name of the table to target.
                'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
        db_connect_info: See shared_db.py's get_configuration for further details.
    """
    values = json.loads(record['body'])
    request_method = RequestMethod(record['messageAttributes']['RequestMethod'])
    if request_method == RequestMethod.NEW_JOB:
        # todo: Better key checks here and elsewhere
        create_status_for_job_and_files(values['job_id'],
                                        values['granule_id'],
                                        values['request_time'],
                                        values['archive_destination'],
                                        values['files'],
                                        db_connect_info)
    elif request_method == RequestMethod.UPDATE_FILE:
        update_status_for_file(values['job_id'],
                               values['granule_id'],
                               values['filename'],
                               values['last_update'],
                               values.get('completion_time', None),
                               values['status_id'],
                               values.get('error_message', None),
                               db_connect_info)
    else:
        raise ValueError(f"RequestMethod '{request_method}' not found.")


def create_status_for_job_and_files(job_id: str,
                                    granule_id: str,
                                    request_time: str,
                                    archive_destination: str,
                                    files: List[Dict[str, Any]],
                                    db_connect_info: Dict) -> None:
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
        db_connect_info: See shared_db.py's get_configuration for further details.
    """

    # Create job status in DB
    job_sql = text("""
            INSERT INTO recovery_job
                ("job_id", "granule_id", "status_id", "request_time", "completion_time", "archive_destination")
            VALUES
                (:job_id, :granule_id, :status_id, :request_time, :completion_time, :archive_destination)""")

    # Create file statuses in DB
    file_sql = text("""
            INSERT INTO recovery_file
                ("job_id", "granule_id", "filename", "key_path", "restore_destination", "status_id",
                "error_message", "request_time", "last_update", "completion_time")
            VALUES
                (:job_id, :granule_id, :filename, :key_path, :restore_destination, :status_id, :error_message, 
                :request_time, :last_update, :completion_time)""")

    found_pending = False
    job_completion_time = None
    file_parameters = []
    for file in files:
        if file['status_id'] == OrcaStatus.PENDING.value:
            found_pending = True
        elif file['status_id'] == OrcaStatus.FAILED.value:
            job_completion_time = max(job_completion_time, file['completion_time'])
        else:
            raise ValueError(f"Status ID '{file['status_id']}' not allowed for new status.")
        file_parameters.append({'job_id': job_id, 'granule_id': granule_id, 'filename': file['filename'],
                                'key_path': file['key_path'], 'restore_destination': file['restore_destination'],
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

    engine = shared_db.get_user_connection(db_connect_info)
    with engine.begin() as connection:
        connection.execute(job_sql, [{'job_id': job_id, 'granule_id': granule_id, 'status_id': job_status.value,
                                      'request_time': request_time, 'completion_time': job_completion_time,
                                      'archive_destination': archive_destination}])
        connection.execute(file_sql, file_parameters)


def update_status_for_file(job_id: str,
                           granule_id: str,
                           filename: str,
                           last_update: str,
                           completion_time: Optional[str],
                           status_id: OrcaStatus,
                           error_message: Optional[str],
                           db_connect_info: Dict) -> None:
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

        db_connect_info: See shared_db.py's get_configuration for further details.
    """
    # Update entry in DB
    file_sql = text("""
            UPDATE recovery_file
            SET status_id = :status_id, last_update = :last_update, completion_time = :completion_time,
                error_message = :error_message
            WHERE job_id = :job_id AND granule_id = :granule_id AND filename = :filename""")
    job_sql = text("""
            with granule_status as (
                SELECT
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
            )
            UPDATE
                recovery_job
            SET
                status_id = granule_status.status_id,
                completion_time = granule_status.completion_time
            WHERE
                recovery_job.job_id = :job_id
            AND
                recovery_job.granule_id = :granule_id""")

    file_parameters = {'status_id': status_id, 'last_update': last_update,
                       'completion_time': completion_time, 'error_message': error_message,
                       'job_id': job_id, 'granule_id': granule_id, 'filename': filename}
    job_parameters = {'job_id': job_id, 'granule_id': granule_id}
    engine = shared_db.get_user_connection(db_connect_info)
    with engine.begin() as connection:
        connection.execute(file_sql, file_parameters)
        connection.execute(job_sql, job_parameters)


def handler(event: Dict[str, List], context) -> None:
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: A dict with the following keys:
            'Records' (List): A list of dicts with the following keys:
                'messageId' (str)
                'receiptHandle' (str)
                'body' (str): A json string representing a dict.
                    See files in schemas for details.  # todo: write them up.
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


temp_db_connect_info = {
    'host': 'localhost',
    'port': '5432',
    'database': 'disaster_recovery',
    'app_user': 'postgres',
    'app_user_password': 'postgres'
}


def test1():
    print(task([{
        'body': json.dumps({
            'job_id': 'job_id_0',
            'granule_id': 'granule_id_0',
            'request_time': datetime.datetime.now().utcnow().isoformat().__str__(),
            'archive_destination': 'archive_destination_0',
            'files': [
                {
                    'key_path': 'key_path0',
                    'restore_destination': 'restore_destination0',
                    'status_id': shared_recovery.OrcaStatus.PENDING.value,
                    'filename': 'filename0',
                    'request_time': datetime.datetime.now().utcnow().isoformat().__str__(),
                    'last_update': datetime.datetime.now().utcnow().isoformat().__str__()
                }
            ]
        }, indent=4),
        'messageAttributes': {'RequestMethod': 'new_job'}
    }], temp_db_connect_info))


def test2():
    print(task([{
        'body': json.dumps({
            'status_id': OrcaStatus.FAILED.value,
            'last_update': datetime.datetime.now().utcnow().isoformat().__str__(),
            'completion_time': datetime.datetime.now().utcnow().isoformat().__str__(),
            'error_message': 'WHY!???',
            'job_id': 'job_id_0',
            'granule_id': 'granule_id_0',
            'filename': 'filename0',

        }, indent=4),
        'messageAttributes': {'RequestMethod': RequestMethod.UPDATE_FILE.value}
    }], temp_db_connect_info))


test2()
