"""
Name: copy_files_to_archive.py

Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""
import json
import os
import time
import logging
from enum import Enum
from typing import Any, List, Dict, Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import requests_db
from cumulus_logger import CumulusLogger


class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'


LOGGER = CumulusLogger()


def task(records: List[Dict[str, Any]], db_connect_info: Dict):
    for record in records:
        post_record_to_database(record, db_connect_info)


def post_record_to_database(record: Dict[str, Any], db_connect_info: Dict):
    values = json.loads(record['body'])
    table_name = record['messageAttributes']['TableName']
    override_existing = RequestMethod(record['messageAttributes']['RequestMethod'])
    post_values_to_database(values, table_name, override_existing, db_connect_info)


def post_values_to_database(values: Dict[str, Any], table_name: str, request_method: RequestMethod, db_connect_info: Dict):
    if request_method is RequestMethod.PUT:
        pass
        # todo: If PUT, get existing entry and update with values.
        # todo: Will need some special logic to get an entry based on keys for the given table_name.
    elif request_method is RequestMethod.POST:
        pass
        # todo: If POST, create a new entry in DB with values.
    # todo: If error raised, log.


# todo: Make sure to grant sqs:ReceiveMessage, sqs:DeleteMessage, and sqs:GetQueueAttributes
def handler(event: Dict[str, List], context):
    """
    Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.

    Args:
        event: A dict with the following keys:
            'Records' (List): A list of dicts with the following keys:
                'messageId' (str)
                'receiptHandle' (str)
                'body' (str): A json formatted string representing a dict of values to write as DB entry.
                'attributes' (Dict)
                'messageAttributes' (Dict): A dict with the following keys defined in the functions that write to queue.
                    'RequestMethod' (str): 'post' or 'put'.
                        If post, no entry with the same keys can exist.
                        If put, an entry with the same keys must exist, and will be updated with the values in 'body'.
                    'TableName': (str): The name of the table to write to.
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
    pass
