"""
This module contains helper functions for the unit tests.
"""
import datetime
import json
import time

import psycopg2
import psycopg2.extras

import requests

JOB_ID_1 = 101
JOB_ID_2 = 102
JOB_ID_3 = 103
JOB_ID_4 = 104
JOB_ID_5 = 105
JOB_ID_6 = 106
JOB_ID_7 = 107
JOB_ID_8 = 108
JOB_ID_9 = 109
JOB_ID_10 = 110
JOB_ID_11 = 111

UTC_NOW_EXP_1 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_1 = requests.request_id_generator()
UTC_NOW_EXP_2 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_2 = requests.request_id_generator()
UTC_NOW_EXP_3 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_4 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_3 = requests.request_id_generator()
UTC_NOW_EXP_5 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_6 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_4 = requests.request_id_generator()
UTC_NOW_EXP_7 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_8 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_5 = requests.request_id_generator()
UTC_NOW_EXP_9 = requests.get_utc_now_iso()
time.sleep(1)
REQUEST_ID_EXP_6 = requests.request_id_generator()
UTC_NOW_EXP_10 = requests.get_utc_now_iso()
time.sleep(1)
UTC_NOW_EXP_11 = requests.get_utc_now_iso()


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


class LambdaContextMock:
    """
    create a lambda context for testing.
    """
    def __init__(self):
        self.function_name = "request_files"
        self.function_version = 1
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:065089468788:function:request_files:1"


def create_select_requests(job_ids):
    """
    creates jobs in the db
    """
    qresult = []
    exp_result = []
    row = build_row(JOB_ID_1, REQUEST_ID_EXP_1, 'granule_1',
                    'objectkey_1', 'restore', 'my_s3_bucket', 'complete',
                    UTC_NOW_EXP_1,
                    UTC_NOW_EXP_4,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_1 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_2, REQUEST_ID_EXP_1, 'granule_2',
                    'objectkey_2', 'restore', 'my_s3_bucket', 'complete',
                    UTC_NOW_EXP_2,
                    UTC_NOW_EXP_5,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_2 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_3, REQUEST_ID_EXP_1, 'granule_3',
                    'objectkey_3', 'restore', 'my_s3_bucket', 'complete',
                    UTC_NOW_EXP_3,
                    UTC_NOW_EXP_6,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_3 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_4, REQUEST_ID_EXP_2, 'granule_4',
                    'objectkey_4', 'restore', 'my_s3_bucket', 'error',
                    UTC_NOW_EXP_4,
                    None, "Error message goes here")
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_4 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_5, REQUEST_ID_EXP_3, 'granule_5',
                    'objectkey_5', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_5,
                    UTC_NOW_EXP_5,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_5 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_6, REQUEST_ID_EXP_3, 'granule_6',
                    'objectkey_6', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_6,
                    UTC_NOW_EXP_6,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_6 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_7, REQUEST_ID_EXP_4, 'granule_4',
                    'objectkey_4', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_7,
                    UTC_NOW_EXP_7,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_7 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_8, REQUEST_ID_EXP_5, 'granule_1',
                    'objectkey_1', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_8,
                    UTC_NOW_EXP_8,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_8 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_9, REQUEST_ID_EXP_5, 'granule_2',
                    'objectkey_2', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_9,
                    UTC_NOW_EXP_9,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_9 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_10, REQUEST_ID_EXP_5, 'granule_3',
                    'objectkey_3', 'restore', 'my_s3_bucket', 'inprogress',
                    UTC_NOW_EXP_10,
                    UTC_NOW_EXP_10,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_10 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    row = build_row(JOB_ID_11, REQUEST_ID_EXP_6, 'granule_7',
                    'objectkey_7', 'regenerate', None, 'inprogress',
                    UTC_NOW_EXP_11,
                    UTC_NOW_EXP_11,
                    None)
    qresult.append(psycopg2.extras.RealDictRow(row))
    if JOB_ID_11 in job_ids:
        exp_result.append(psycopg2.extras.RealDictRow(row))
    return qresult[0], exp_result[0]


def create_insert_request(job_id, request_id, granule_id, object_key, job_type,
                          restore_bucket_dest, job_status, request_time,
                          last_update_time, err_msg):
    """
    creates jobs in the db
    """
    iresult = []
    row = []
    row.append(('job_id', job_id))
    iresult.append(psycopg2.extras.RealDictRow(row))

    qresult = []
    row = build_row(job_id, request_id, granule_id, object_key, job_type,
                    restore_bucket_dest, job_status, request_time,
                    last_update_time, err_msg)
    qresult.append(psycopg2.extras.RealDictRow(row))
    return iresult, qresult


def build_row(job_id, request_id, granule_id, object_key, job_type,
              restore_bucket_dest, job_status, rq_date,
              lu_date, err_msg):
    """
    builds a row mimicing what would be returned from a call to the db
    """
    row = []
    row.append(('job_id', job_id))
    row.append(('request_id', request_id))
    row.append(('granule_id', granule_id))
    row.append(('object_key', object_key))
    row.append(('job_type', job_type))
    row.append(('restore_bucket_dest', restore_bucket_dest))
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
