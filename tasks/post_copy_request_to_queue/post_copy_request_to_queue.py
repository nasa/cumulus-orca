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
import shared_db

OS_ENVIRON_DB_QUEUE_URL_KEY = 'DB_QUEUE_URL'
OS_ENVIRON_RECOVERY_QUEUE_URL_KEY = 'DB_QUEUE_URL_RECOVERY'

INPUT_JOB_ID_KEY = 'job_id'
INPUT_GRANULE_ID_KEY = 'granule_id'
INPUT_FILENAME_KEY = 'filename'
INPUT_TARGET_BUCKET_KEY = 'restore_destination'
INPUT_SOURCE_BUCKET_KEY = 'source_bucket'
DATABASE_NAME = 'disaster-recovery'
DATABASE_PORT = '5432'
DATABASE_USER = 'user'


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

    # SQL for checking database
    query_db_sql = (
        """
        SELECT
            job_id, granule_id, restore_destination
        FROM
            orca_recoverfile
        WHERE
            filename = %s
        AND
            status_id = 1
    """
    )

    # Run the query
    results = connection.execute(query_db_sql)
    for row in results:
        db_exists = row[0]

    #post to staged-recovery-queue

    shared_recovery.post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        status_id,
        error_message,
        request_method,
        db_queue_url= OS_ENVIRON_RECOVERY_QUEUE_URL_KEY
        )

    #post to DB-queue

    shared_recovery.post_status_for_file_to_queue(
        job_id,
        granule_id,
        filename,
        restore_destination,
        status_id,
        error_message,
        request_method,
        db_queue_url= OS_ENVIRON_DB_QUEUE_URL_KEY
        )