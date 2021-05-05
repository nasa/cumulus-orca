"""
Name: post_to_database.py

Description:  Pulls entries from a queue and posts them to a DB.
"""
import json
from enum import Enum
from typing import Any, List, Dict

# noinspection PyPackageRequirements
import database
# noinspection PyUnresolvedReferences
import requests_db
from cumulus_logger import CumulusLogger


# todo: Shared lib
class RequestMethod(Enum):
    """
    An enumeration.
    Provides potential actions for the database lambda to take when posting to the SQS queue.
    """
    NEW_JOB = "new_job"
    UPDATE_FILE = "update_file"


# todo: Shared lib
class OrcaStatus(Enum):
    """
    An enumeration.
    Defines the status value used in the ORCA Recovery database for use by the recovery functions.

    """
    PENDING = 1
    STAGED = 2
    FAILED = 3
    SUCCESS = 4


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
        db_connect_info: See requests_db.py's get_dbconnect_info for further details.
    """
    values = json.loads(record['body'])
    table_name = record['messageAttributes']['TableName']
    request_method = RequestMethod(record['messageAttributes']['RequestMethod'])
    if request_method == RequestMethod.NEW_JOB:
        # todo: Better key checks here and elsewhere
        create_status_for_job_and_files(values['job_id'],
                                        values['granule_id'],
                                        values['request_time'],
                                        values['archive_destination'],
                                        values['files'],
                                        db_connect_info)
        pass
    elif request_method == RequestMethod.UPDATE_FILE:
        # todo: Remember to update job if needed.
        update_status_for_file(values, db_connect_info)
        pass
    else:
        raise ValueError(f"RequestMethod '{request_method}' not found.")

    # todo: Remove
    # send_values_to_database(table_name, values, request_method, db_connect_info)


def create_status_for_job_and_files(job_id: str,
                                    granule_id: str,
                                    request_time: str,
                                    archive_destination: str,
                                    files: List[Dict[str, Any]],
                                    db_connect_info: Dict) -> None:
    """
    todo
    """

    # Create job status in DB
    # todo: Use driver's auto-transaction functionality.
    # engine, with engine, do stuff, do commit
    sql = f"""
            BEGIN TRANSACTION
                INSERT INTO orca_recoveryjob
                    ('job_id', 'granule_id', 'status_id', 'request_time', 'completion_time', 'archive_destination')
                VALUES
                    (%s, %s, %s, %s, %s, %s)"""

    # Create file statuses in DB
    sql += f"""
                INSERT INTO orca_recoverfile
                    ('job_id', 'granule_id', 'filename', 'key_path', 'restore_destination', 'status_id',
                    'error_message', 'request_time', 'last_update', 'completion_time')
                VALUES"""
    found_pending = False
    job_completion_time = None

    sql += ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'] * len(files))
    file_parameters = tuple()
    for file in files:
        if file['status_id'] == OrcaStatus.PENDING.value:
            found_pending = True
        elif file['status_id'] == OrcaStatus.FAILED.value:
            job_completion_time = max(job_completion_time, file['completion_time'])
        else:
            raise ValueError(f"Status ID '{file['status_id']}' not allowed for new status.")
        file_parameters += tuple(file['job_id'], file['granule_id'], file['filename'], file['key_path'],
                                 file['restore_destination'], file['status_id'], file.get('error_message', None),
                                 file['request_time'], file['last_update'], file.get('completion_time', None))

    if found_pending:
        # Most jobs will be this. Some files are still pending.
        job_status = OrcaStatus.PENDING
        job_completion_time = None
    else:
        # All files failed during recovery request.
        job_status = OrcaStatus.FAILED

    parameters = tuple(job_id, granule_id, job_status.value, request_time, job_completion_time,
                       archive_destination) + file_parameters
    # Commit transaction
    sql += f"""
            COMMIT"""

    database.single_query(sql, db_connect_info, parameters)


def update_status_for_file(values: Dict[str, Any], db_connect_info: Dict) -> None:
    """
    todo
    """

    # todo: orca_recoverfile -> recovery_file
    # todo: orca_recoveryjob -> recovery_job
    # todo: orca_status -> recover_status
    # Update entry in DB
    # todo: Use sqlalchemy suggestions from above
    sql = """
            BEGIN TRANSACTION
                UPDATE orca_recoverfile
                SET status_id = %s, last_update = %s, completion_time = %s, error_message = %s
                WHERE job_id = %s AND granule_id = %s AND filename = %s
            COMMIT"""
    # todo: If all files for job completed, update job.
    # todo: Update Select to update the JOB
    # Common Table Expression?

    # (staged)
    # if ALL status == staged
    #   Set job to staged
    # (success)
    # if ALL status == Success
    #   Set job to Success
    # (error)
    # if ALL status == Success OR Error
    #   Set job to Error

    parameters = tuple(values['status_id'], values['last_update'], values['completion_time'], values['error_message'],
                       values['job_id'], values['granule_id'], values['filename'])
    database.single_query(sql, db_connect_info, parameters)


def send_values_to_database(table_name: str, values: Dict[str, Any], request_method: RequestMethod,
                            db_connect_info: Dict) -> None:
    """

    Args:
        table_name: The name of the table to target.
        values: Contains key/value pairs of column names and values for those columns.
        request_method: POST or PUT, depending on if row should be created or updated respectively.
        db_connect_info: See requests_db.py's get_dbconnect_info for further details.
    """
    try:
        if request_method == RequestMethod.PUT:
            keys = table_key_dictionary.get(table_name, None)
            if keys is not None:
                update_row_in_table(table_name, keys, values, db_connect_info)
            else:
                raise NotImplementedError()
        elif request_method == RequestMethod.POST:
            insert_row_from_values(table_name, values, db_connect_info)
    except Exception as ex:
        LOGGER.error(ex)


def insert_row_from_values(table_name: str, values: Dict[str, Any], db_connect_info: Dict) -> None:
    """
    Inserts a new row into the given table.

    Args:
        table_name: The name of the table to target.
        values: Contains key/value pairs of column names and values for those columns.
        db_connect_info: See requests_db.py's get_dbconnect_info for further details.

    Raises: database.DbError if error occurs when contacting database.
    """
    sql = f"""
                    INSERT INTO {table_name} ("""
    sql += ', '.join(values.keys())
    sql += f""")
                    VALUES ("""
    sql += ', '.join(['%s'] * len(values))
    sql += ')'

    parameters = tuple(values[value_key] for value_key in values)
    database.single_query(sql, db_connect_info, parameters)


def update_row_in_table(table_name: str, table_keys: List[str], values: Dict[str, Any], db_connect_info: Dict) -> None:
    """
    Updates a row in the target table, using table_keys to identify the row that should be modified.

    Args:
        table_name: The name of the table to target.
        table_keys: A list of keys. Used to identify the row to change.
        values: Contains key/value pairs of column names and values for those columns.
            If a column name is in table_keys, the value will be used to identify the target row.
        db_connect_info: See requests_db.py's get_dbconnect_info for further details.

    Raises: database.DbError if error occurs when contacting database.
    """
    key_values = {table_key: None for table_key in table_keys}
    updated_values = {}
    for key in values:
        if table_keys.__contains__(key):
            key_values[key] = values[key]
        else:
            updated_values[key] = values[key]
    sql = f"""
                    UPDATE {table_name}
                    SET """

    sql += ", ".join([f"{updating_value_key} = %s" for updating_value_key in updated_values])

    sql += f"""
                    WHERE """

    sql += " AND ".join([f"{table_key} = %s" for table_key in table_keys])

    #    sql += f"""
    #                    LIMIT 1"""

    parameters = tuple(updated_values[updated_value_key] for updated_value_key in updated_values)
    parameters += tuple(key_values[table_key] for table_key in table_keys)
    database.single_query(sql, db_connect_info, parameters)


def handler(event: Dict[str, List], context) -> None:
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: A dict with the following keys:
            'Records' (List): A list of dicts with the following keys:
                'messageId' (str)
                'receiptHandle' (str)
                'body' (str): A json string representing a dict.
                    Contains key/value pairs of column names and values for those columns.
                'attributes' (Dict)
                'messageAttributes' (Dict): A dict with the following keys defined in the functions that write to queue.
                    'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
                    'TableName' (str): The name of the table to target.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars: See requests_db.py's get_dbconnect_info for further details.
        'DATABASE_PORT' (int): Defaults to 5432
        'DATABASE_NAME' (str)
        'DATABASE_USER' (str)
        'PREFIX' (str)
        '{prefix}-drdb-host' (str, secretsmanager)
        '{prefix}-drdb-user-pass' (str, secretsmanager)
    """
    LOGGER.setMetadata(event, context)

    db_connect_info = requests_db.get_dbconnect_info()

    task(event['Records'], db_connect_info)
