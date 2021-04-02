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


class RequestMethod(Enum):
    POST = 'post'
    PUT = 'put'


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
    send_values_to_database(table_name, values, request_method, db_connect_info)


table_key_dictionary = {
    'orca_recoverfile': ['job_id', 'granule_id', 'filename'],
    'orca_recoveryjob': ['job_id', 'granule_id']
}


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


# todo: Make sure to grant sqs:ReceiveMessage, sqs:DeleteMessage, and sqs:GetQueueAttributes
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
