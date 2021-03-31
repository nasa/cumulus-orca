"""
Name: copy_files_to_archive.py

Description:  Lambda function that copies files from one s3 bucket
to another s3 bucket.
"""
import json
from enum import Enum
from typing import Any, List, Dict, Optional

from botocore.client import BaseClient
from botocore.exceptions import ClientError
# noinspection PyUnresolvedReferences
import requests_db
# noinspection PyPackageRequirements
import database
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
    post_values_to_database(table_name, values, override_existing, db_connect_info)


def post_values_to_database(table_name: str, values: Dict[str, Any], request_method: RequestMethod,
                            db_connect_info: Dict):
    try:
        if request_method == RequestMethod.PUT:
            if table_name == 'orca_recoverfile':
                update_orca_recoverfile(values, db_connect_info)
            elif table_name == 'orca_recoveryjob':
                update_orca_recoveryjob(values, db_connect_info)
            else:
                raise NotImplementedError()
        elif request_method == RequestMethod.POST:
            insert_row_from_values(table_name, values, db_connect_info)
    except Exception as ex:
        LOGGER.error(ex)


def insert_row_from_values(table_name: str, values: Dict[str, Any], db_connect_info: Dict):
    sql = f"""
                    INSERT INTO {table_name} ("""
    sql += ', '.join(values.keys())
    sql += f""")
                    VALUES ("""
    sql += ', '.join(['%s'] * len(values))
    sql += ')'

    parameters = tuple(values[value_key] for value_key in values)
    database.single_query(sql, db_connect_info, parameters)


def update_orca_recoverfile(values: Dict[str, Any], db_connect_info: Dict):
    update_row_in_table('orca_recoverfile', ['job_id', 'granule_id', 'filename'], values, db_connect_info)


def update_orca_recoveryjob(values: Dict[str, Any], db_connect_info: Dict):
    update_row_in_table('orca_recoveryjob', ['job_id', 'granule_id'], values, db_connect_info)


def update_row_in_table(table_name: str, table_keys: List[str], values: Dict[str, Any], db_connect_info: Dict):
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
    try:
        database.single_query(sql, db_connect_info, parameters)
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise requests_db.DatabaseError(str(err))


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

