"""
Name: post_copy_request_to_queue.py
Description:  Posts to two queues - one of the queues notifies copy_files_to_archive lambda that a file is ready for copy
and the other queue updates the file status to STAGED in the DB.

"""
from enum import Enum
import json
import os
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import shared_recovery
import requests_db
import database
from requests_db import DatabaseError

PREFIX = 'dev'
DB_HOST = 'dev-drdb-host'
DATABASE_NAME = 'postgres'
DATABASE_PORT = '5432'
DATABASE_USER = 'rhassan'
DB_PW = '12345678'
OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'
OS_ENVIRON_RECOVERY_QUEUE_URL_KEY = 'DB_QUEUE_URL_RECOVERY'


def lambda_handler(event, context):
    """
    Lambda handler. This lambda queries all entries from orca_recoverfile table 
    that match the given filename and whose status_id is 'PENDING'.
    The result is then sent to the staged-recovery-queue SQS.
    The status_id is updated to STAGED and then sent to status-update-queue SQS.
    
        Environment Vars:
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
    Args:
        event:
            A dictionary from the S3 bucket. See schemas/input.json for more information.
        context: An object required by AWS Lambda. Unused.
    Raises:
        None
    """
    # grab the filename from event
    for record in event['Records']:
        filename = record['s3']['object']['key']

    sql = """
        SELECT
            job_id, granule_id, restore_destination
        FROM
            orca_recoverfile
        WHERE
            filename = %s
        AND
            status_id = %d
    """
    #Gets the dbconnection info.

    db_connect_info = requests_db.get_dbconnect_info()

    try:
        rows = database.single_query(sql, database.db_connect_info, (filename, shared_recovery.OrcaStatus.PENDING))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    if len(rows) == 0:
        return None
    orca_recoveryfile = rows[0]
    # grab the parameters from the db in json format
    job_id = database.result_to_json(orca_recoveryjob)['job_id']
    granule_id = database.result_to_json(orca_recoveryjob)['granule_id']
    restore_destination = database.result_to_json(orca_recoveryjob)['restore_destination']

    #post to staged-recovery-queue
    shared_recovery.post_status_for_file_to_queue(
        job_id = job_id,
        granule_id = granule_id,
        filename = filename,
        restore_destination = restore_destination,
        status_id = shared_recovery.OrcaStatus.PENDING,
        error_message = '',
        request_method = shared_recovery.RequestMethod.NEW,
        db_queue_url= OS_ENVIRON_RECOVERY_QUEUE_URL_KEY
        )

    #post to DB-queue
    shared_recovery.post_status_for_file_to_queue(
        job_id = job_id,
        granule_id = granule_id,
        filename = filename,
        restore_destination = restore_destination,
        status_id = shared_recovery.OrcaStatus.PENDING,
        error_message = '',
        request_method = shared_recovery.RequestMethod.NEW,
        db_queue_url= OS_ENVIRON_DB_QUEUE_URL_KEY
        )