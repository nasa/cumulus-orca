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
from shared_recovery import OrcaStatus, RequestMethod, post_status_for_file_to_queue, post_status_for_job_to_queue
import requests_db
import database
from requests_db import DatabaseError
from cumulus_logger import CumulusLogger

# instantiate CumulusLogger
LOGGER = CumulusLogger()

PREFIX = os.environ['PREFIX']
DATABASE_NAME = os.environ['DATABASE_NAME']
DATABASE_PORT = os.environ['DATABASE_PORT']
DATABASE_USER = os.environ['DATABASE_USER']
DB_QUEUE_URL = os.environ['DB_QUEUE_URL']
RECOVERY_QUEUE_URL = os.environ['RECOVERY_QUEUE_URL']


def handler(event, context):
    """
    Lambda handler. This lambda queries all entries from orca_recoverfile table 
    that match the given filename and whose status_id is 'PENDING'.
    The result is then sent to the staged-recovery-queue SQS.
    The status_id is updated to STAGED and then sent to status-update-queue SQS.
    
        Environment Vars:
            PREFIX (string): the prefix
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DB_QUEUE_URL (string): the SQS URL for status-update-queue
            RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
        Parameter store:
            {prefix}-drdb-host (string): host name that will be retrieved from secrets manager
            {prefix}-drdb-user-pass (string):db password that will be retrieved from secrets manager
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
        rows = database.single_query(sql, database.db_connect_info, (filename, OrcaStatus.PENDING.value))
    except Exception as ex:
        LOGGER.error(ex)

    if len(rows) == 0:
        raise Exception("length of rows cannot be empty since there will always be a record in the database")
    orca_recoveryfile = rows[0]
    # grab the parameters from the db in json format
    job_id = database.result_to_json(orca_recoveryjob)['job_id']
    granule_id = database.result_to_json(orca_recoveryjob)['granule_id']
    restore_destination = database.result_to_json(orca_recoveryjob)['restore_destination']

    #post to staged-recovery-queue
    post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        OrcaStatus.STAGED.value,
        '',
        RequestMethod.NEW.value,
        RECOVERY_QUEUE_URL
        )

    #post to DB-queue
    post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        OrcaStatus.STAGED.value,
        '',
        RequestMethod.NEW.value,
        DB_QUEUE_URL
        )
