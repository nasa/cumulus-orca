"""
This module contains helper functions for the unit tests.
# todo: Kill this file. It recreates wholesale logic from production code. Some of it buggy.
"""
import datetime
import json
import os
import time
import uuid
from unittest.mock import Mock
import boto3

import psycopg2
import psycopg2.extras

import database

#import restore_requests

PROTECTED_BUCKET = "my-protected-bucket"
REQUEST_ID1 = str(uuid.uuid4())
REQUEST_ID2 = str(uuid.uuid4())
REQUEST_ID3 = str(uuid.uuid4())
REQUEST_ID4 = str(uuid.uuid4())
REQUEST_ID5 = str(uuid.uuid4())
REQUEST_ID6 = str(uuid.uuid4())
REQUEST_ID7 = str(uuid.uuid4())
REQUEST_ID8 = str(uuid.uuid4())
REQUEST_ID9 = str(uuid.uuid4())
REQUEST_ID10 = str(uuid.uuid4())
REQUEST_ID11 = str(uuid.uuid4())
REQUEST_ID12 = str(uuid.uuid4())

UTC_NOW_EXP_1 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_1 = str(uuid.uuid4())
UTC_NOW_EXP_2 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_2 = str(uuid.uuid4())
UTC_NOW_EXP_3 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_4 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_3 = str(uuid.uuid4())
UTC_NOW_EXP_5 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_6 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_4 = str(uuid.uuid4())
UTC_NOW_EXP_7 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_8 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_5 = str(uuid.uuid4())
UTC_NOW_EXP_9 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
REQUEST_GROUP_ID_EXP_6 = str(uuid.uuid4())
UTC_NOW_EXP_10 = datetime.datetime.utcnow().isoformat()
time.sleep(1)
UTC_NOW_EXP_11 = datetime.datetime.utcnow().isoformat()

def mock_secretsmanager_get_parameter(n_times):
    """
    mocks the reads from the parameter store for the dbconnect values
    """
    params = []
    db_host = {'SecretString': os.environ['DATABASE_HOST']}
    db_pw = {'SecretString': os.environ['DATABASE_PW']}
    loop = 0
    while loop < n_times:
        params.append(db_host)
        params.append(db_pw)
        loop = loop + 1
    secretsmanager_cli = boto3.client('secretsmanager')
    secretsmanager_cli.get_secret_value = Mock(side_effect=params)

def create_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/request_files_fixture1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/request_files_fixture1.json') as fil:
            event = json.load(fil)
    return event

def create_copy_handler_event():
    """
    create a handler event for testing.
    """
    try:
        with open('test/testevents/copy_exp_event_1.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/copy_exp_event_1.json') as fil:
            event = json.load(fil)
    return event

def create_copy_event2():
    """
    create a second handler event for testing.
    """
    try:
        with open('test/testevents/copy_exp_event_2.json') as fil:
            event = json.load(fil)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        with open('testevents/copy_exp_event_2.json') as fil:
            event = json.load(fil)
    return event


def create_select_requests(request_ids):
    """
    creates jobs in the db
    """
    qresult = []
    exp_result = []
    row = build_row(REQUEST_ID11, REQUEST_GROUP_ID_EXP_6, 'granule_7',
                    'objectkey_7', 'regenerate', None,
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_11,
                    UTC_NOW_EXP_11,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID11 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))

    row = build_row(REQUEST_ID10, REQUEST_GROUP_ID_EXP_5, 'granule_3',
                    'objectkey_3', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_10,
                    UTC_NOW_EXP_10,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID10 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID9, REQUEST_GROUP_ID_EXP_5, 'granule_2',
                    'objectkey_2', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_9,
                    UTC_NOW_EXP_9,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID9 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID8, REQUEST_GROUP_ID_EXP_5, 'granule_1',
                    'objectkey_1', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_8,
                    UTC_NOW_EXP_8,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID8 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID7, REQUEST_GROUP_ID_EXP_4, 'granule_4',
                    'objectkey_4', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_7,
                    UTC_NOW_EXP_7,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID7 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID6, REQUEST_GROUP_ID_EXP_3, 'granule_6',
                    'objectkey_6', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_6,
                    UTC_NOW_EXP_6,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID6 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID5, REQUEST_GROUP_ID_EXP_3, 'granule_5',
                    'objectkey_5', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'inprogress',
                    UTC_NOW_EXP_5,
                    UTC_NOW_EXP_5,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID5 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID4, REQUEST_GROUP_ID_EXP_2, 'granule_4',
                    'objectkey_4', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'error',
                    UTC_NOW_EXP_4,
                    None, "Error message goes here")
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID4 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID3, REQUEST_GROUP_ID_EXP_1, 'granule_3',
                    'objectkey_3', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'complete',
                    UTC_NOW_EXP_3,
                    UTC_NOW_EXP_6,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID3 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID2, REQUEST_GROUP_ID_EXP_1, 'granule_2',
                    'objectkey_2', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'complete',
                    UTC_NOW_EXP_2,
                    UTC_NOW_EXP_5,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID2 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(REQUEST_ID1, REQUEST_GROUP_ID_EXP_1, 'granule_1',
                    'objectkey_1', 'restore', 'my_s3_bucket',
                    PROTECTED_BUCKET, 'complete',
                    UTC_NOW_EXP_1,
                    UTC_NOW_EXP_4,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if REQUEST_ID1 in request_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))

    return qresult, exp_result


def create_insert_request(request_id,          #pylint: disable-msg=too-many-arguments
                          request_group_id, granule_id, object_key, job_type,
                          restore_bucket_dest, archive_bucket_dest, job_status,
                          request_time, last_update_time, err_msg):
    """
    creates jobs in the db
    """
    iresult = []
    row = []
    row.append(('request_id', request_id))
    iresult.append(psycopg2.extras.RealDictRow(row))

    qresult = []
    row = build_row(request_id, request_group_id, granule_id, object_key, job_type,
                    restore_bucket_dest, archive_bucket_dest, job_status, request_time,
                    last_update_time, err_msg)
    qresult.append(psycopg2.extras.RealDictRow(row))
    return iresult, qresult


def build_row(request_id,             #pylint: disable-msg=too-many-arguments
              request_group_id, granule_id, object_key, job_type,
              restore_bucket_dest, archive_bucket_dest, job_status, rq_date,
              lu_date, err_msg):
    """
    builds a row mimicing what would be returned from a call to the db
    """
    row = []
    row.append(('request_id', request_id))
    row.append(('request_group_id', request_group_id))
    row.append(('granule_id', granule_id))
    row.append(('object_key', object_key))
    row.append(('job_type', job_type))
    row.append(('restore_bucket_dest', restore_bucket_dest))
    row.append(('archive_bucket_dest', archive_bucket_dest))
    row.append(('job_status', job_status))
    if rq_date:
        dte = datetime.datetime.strptime(rq_date, "%Y-%m-%dT%H:%M:%S.%f")
        rq_date = datetime.datetime(dte.year, dte.month, dte.day, dte.hour,
                                    dte.minute, dte.second, dte.microsecond,
                                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                        offset=0, name=None))
    row.append(('request_time', rq_date))
    if lu_date:
        dte = datetime.datetime.strptime(lu_date, "%Y-%m-%dT%H:%M:%S.%f")
        lu_date = datetime.datetime(dte.year, dte.month, dte.day, dte.hour,
                                    dte.minute, dte.second, dte.microsecond,
                                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                                        offset=0, name=None))
    row.append(('last_update_time', lu_date))
    row.append(('err_msg', err_msg))
    return row

def print_rows(label):
    """
    prints the rows of a list
    """
    try:
        develop_tests = os.environ['DEVELOP_TESTS']
    except KeyError:
        develop_tests = False

    if develop_tests:
        print("****REQUEST_IDS: 1) ", REQUEST_ID1, " 2) ", REQUEST_ID2, " 3) ", REQUEST_ID3,
              " 4) ", REQUEST_ID4, " 5) ", REQUEST_ID5, " 6) ", REQUEST_ID6,
              " 7) ", REQUEST_ID7, " 8) ", REQUEST_ID8, " 9) ", REQUEST_ID9,
              " 10) ", REQUEST_ID10, " 11) ", REQUEST_ID11, " 12) ", REQUEST_ID12)
        print("****REQUEST_GROUP_EXP_IDs: 1) ", REQUEST_GROUP_ID_EXP_1,
              " 2) ", REQUEST_GROUP_ID_EXP_2,
              " 3) ", REQUEST_GROUP_ID_EXP_3, " 4) ", REQUEST_GROUP_ID_EXP_4,
              " 5) ", REQUEST_GROUP_ID_EXP_5, " 6) ", REQUEST_GROUP_ID_EXP_6)
        rows = get_all_requests()
        print("**** ", label)
        for row in rows:
            print(row)
        print("****")

def get_all_requests():
    """
    Returns all of the requests.
    """
    sql = """
        SELECT
            request_id,
            request_group_id,
            granule_id,
            object_key,
            job_type,
            restore_bucket_dest,
            archive_bucket_dest,
            job_status,
            request_time,
            last_update_time,
            err_msg
        FROM
            request_status
        ORDER BY last_update_time desc """

    try:
        rows = database.single_query(sql, ())
        result = json.loads(json.dumps(rows, default=myconverter))
    except database.DbError as err:
        print(str(err))

    return result

def myconverter(obj):       #pylint: disable-msg=inconsistent-return-statements
    """
    Returns the current utc timestamp as a string in isoformat
    ex. '2019-07-17T17:36:38.494918'
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

class LambdaContextMock:   #pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """
    def __init__(self):
        self.function_name = "request_files"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:065089468788:function:request_files:1"
