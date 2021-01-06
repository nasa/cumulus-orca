"""
Name: test_requests.py

Description:  Unit tests for requests_db.py.
"""

import os
import unittest
from unittest.mock import Mock
import uuid
import boto3

import database
from database import DbError
from test.request_helpers import (REQUEST_GROUP_ID_EXP_1, REQUEST_GROUP_ID_EXP_2,
                             REQUEST_GROUP_ID_EXP_3, REQUEST_ID1, REQUEST_ID2,
                             REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                             REQUEST_ID6, REQUEST_ID7, REQUEST_ID8,
                             REQUEST_ID9, REQUEST_ID10, REQUEST_ID11,
                             UTC_NOW_EXP_1, UTC_NOW_EXP_4, mock_secretsmanager_get_parameter,
                             create_insert_request, create_select_requests)
import requests_db
from requests_db import result_to_json


class TestRequests(unittest.TestCase):  #pylint: disable-msg=too-many-public-methods
    """
    TestRequestFiles.
    """

    def setUp(self):

        prefix = "lab"
        os.environ["PREFIX"] = prefix
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_PORT"] = "50"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"

        self.mock_utcnow = requests_db.get_utc_now_iso
        self.mock_request_group_id = requests_db.request_id_generator
        self.mock_single_query = database.single_query
        self.mock_uuid = uuid.uuid4
        self.mock_boto3_client = boto3.client


    def tearDown(self):
        boto3.client = Mock()
        uuid.uuid4 = self.mock_uuid
        database.single_query = self.mock_single_query
        requests_db.request_id_generator = self.mock_request_group_id
        requests_db.get_utc_now_iso = self.mock_utcnow
        del os.environ["PREFIX"]
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]

    def test_delete_all_requests(self):
        """
        Tests deleting all requests from the request_status table
        """
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                           REQUEST_ID6, REQUEST_ID7, REQUEST_ID8, REQUEST_ID9, REQUEST_ID10,
                           REQUEST_ID11]
        try:
            create_select_requests(exp_request_ids)
            empty_result = []
            mock_secretsmanager_get_parameter(1)
            database.single_query = Mock(
                side_effect=[empty_result])
            result = requests_db.delete_all_requests()
            database.single_query.assert_called()
            self.assertEqual(empty_result, result)
        except requests_db.DatabaseError as err:
            self.fail(f"delete_all_requests. {str(err)}")

    def test_delete_all_requests_dberror(self):
        """
        Tests db error deleting all requests from the request_status table
        """
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        try:
            mock_secretsmanager_get_parameter(1)
            database.single_query = Mock(
                side_effect=[DbError(exp_err)])
            requests_db.delete_all_requests()
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
        database.single_query.assert_called_once()


    def test_delete_request(self):
        """
        Tests deleting a job by request_id
        """
        try:
            exp_result = []
            mock_secretsmanager_get_parameter(1)
            database.single_query = Mock(side_effect=[exp_result])
            result = requests_db.delete_request(REQUEST_ID1)
            self.assertEqual(exp_result, result)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"delete_request. {str(err)}")

    def test_delete_request_no_request_id(self):
        """
        Tests no request_id given for deleting a job by request_id
        """
        try:
            mock_secretsmanager_get_parameter(1)
            database.single_query = Mock(side_effect=
                                         [requests_db.BadRequestError(
                                             "No request_id provided")])
            requests_db.delete_request(None)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual("No request_id provided", str(err))


    def test_delete_request_database_error(self):
        """
        Tests database error while deleting a job by request_id
        """
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        try:
            mock_secretsmanager_get_parameter(1)
            database.single_query = Mock(side_effect=[DbError(exp_err)])
            requests_db.delete_request('x')
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            database.single_query.assert_called_once()


    def test_get_all_requests(self):
        """
        Tests reading all requests
        """
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3, REQUEST_ID4, REQUEST_ID5,
                           REQUEST_ID6, REQUEST_ID7, REQUEST_ID8, REQUEST_ID9, REQUEST_ID10,
                           REQUEST_ID11]
        qresult, exp_result = create_select_requests(exp_request_ids)
        mock_secretsmanager_get_parameter(1)
        database.single_query = Mock(side_effect=[qresult])
        expected = result_to_json(exp_result)
        result = requests_db.get_all_requests()
        database.single_query.assert_called_once()
        self.assertEqual(expected, result)

        mock_secretsmanager_get_parameter(1)
        err_msg = 'Database Error. could not connect to server'
        database.single_query = Mock(side_effect=[DbError(
            err_msg)])
        try:
            requests_db.get_all_requests()
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            database.single_query.assert_called_once()
            self.assertEqual(err_msg, str(err))

    def test_get_jobs_by_status_exceptions(self):
        """
        Tests getting a DatabaseError reading a job by status
        """
        mock_secretsmanager_get_parameter(2)
        database.single_query = Mock(side_effect=[requests_db.BadRequestError(
            'A status must be provided')])
        status = None
        try:
            requests_db.get_jobs_by_status(status)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual('A status must be provided', str(err))

        status = "error"
        err_msg = 'Database Error. could not connect to server'
        database.single_query = Mock(side_effect=[DbError(
            err_msg)])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests_db.get_jobs_by_status(status)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            database.single_query.assert_called_once()
            self.assertEqual(err_msg, str(err))


    def test_get_job_by_request_id_dberror(self):
        """
        Tests getting a DatabaseError reading a job by request_id
        """
        mock_secretsmanager_get_parameter(1)
        exp_msg = 'Database Error. could not connect to server'
        database.single_query = Mock(side_effect=[DbError(exp_msg)])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests_db.get_job_by_request_id('x')
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual(exp_msg, str(err))
            database.single_query.assert_called_once()


    def test_get_request_not_found(self):
        """
        Tests reading a job that doesn't exist
        """
        request_id = "ABCDEFG"
        exp_result = []
        mock_secretsmanager_get_parameter(1)
        database.single_query = Mock(side_effect=[exp_result])
        result = requests_db.get_job_by_request_id(request_id)
        self.assertEqual(exp_result, result)
        database.single_query.assert_called_once()


    def test_get_jobs_by_request_group_id(self):
        """
        Tests reading a job by request_group_id
        """
        mock_secretsmanager_get_parameter(2)
        exp_request_ids = [REQUEST_ID5, REQUEST_ID6]
        _, exp_result = create_select_requests(exp_request_ids)
        database.single_query = Mock(side_effect=[exp_result])
        expected = result_to_json(exp_result)
        try:
            result = requests_db.get_jobs_by_request_group_id(None)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual("A request_group_id must be provided", str(err))
        try:
            result = requests_db.get_jobs_by_request_group_id(REQUEST_GROUP_ID_EXP_3)
        except requests_db.BadRequestError as err:
            self.fail(str(err))
        self.assertEqual(expected, result)
        database.single_query.assert_called_once()
        database.single_query = Mock(side_effect=[DbError("database error")])
        try:
            result = requests_db.get_jobs_by_request_group_id(REQUEST_GROUP_ID_EXP_3)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual("database error", str(err))

    def test_get_jobs_by_granule_id_dberror(self):
        """
        Tests db error reading by granule_id
        """
        mock_secretsmanager_get_parameter(1)
        database.single_query = Mock(side_effect=[DbError("DbError reading requests")])
        try:
            requests_db.get_jobs_by_granule_id("gran_1")
            self.fail("expected DbError")
        except requests_db.DatabaseError as err:
            self.assertEqual("DbError reading requests", str(err))
            database.single_query.assert_called_once()

    def test_get_jobs_by_object_key_dberror(self):
        """
        Tests db error reading by object_key
        """
        mock_secretsmanager_get_parameter(1)
        database.single_query = Mock(side_effect=[DbError("DbError reading requests")])
        try:
            requests_db.get_jobs_by_object_key("file_1.h5")
            self.fail("expected DbError")
        except requests_db.DatabaseError as err:
            self.assertEqual("DbError reading requests", str(err))
            database.single_query.assert_called_once()


    def test_get_jobs_by_object_key(self):
        """
        Tests reading by object_key
        """
        mock_secretsmanager_get_parameter(1)
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3]
        _, exp_result_1 = create_select_requests(exp_request_ids)
        object_key = " "
        expected = result_to_json(exp_result_1)
        database.single_query = Mock(side_effect=[exp_result_1])
        result = requests_db.get_jobs_by_object_key(object_key)
        self.assertEqual(expected, result)
        database.single_query.assert_called_once()

    def test_get_jobs_by_status(self):
        """
        Tests reading by status
        """
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3]
        _, exp_result_2 = create_select_requests(exp_request_ids)
        status = "noexist"
        exp_result_1 = []
        mock_secretsmanager_get_parameter(2)
        database.single_query = Mock(side_effect=[exp_result_1, exp_result_2])
        result = requests_db.get_jobs_by_status(status)
        self.assertEqual(exp_result_1, result)
        database.single_query.assert_called_once()

        status = "complete"
        expected = result_to_json(exp_result_2)
        result = requests_db.get_jobs_by_status(status)
        self.assertEqual(expected, result)
        database.single_query.assert_called()


    def test_get_jobs_by_status_max_days(self):
        """
        Tests reading by status for limited days
        """
        exp_request_ids = [REQUEST_ID1, REQUEST_ID2, REQUEST_ID3]
        _, exp_result = create_select_requests(exp_request_ids)
        status = "noexist"
        mock_secretsmanager_get_parameter(2)
        database.single_query = Mock(side_effect=[[], exp_result])
        result = requests_db.get_jobs_by_status(status)
        self.assertEqual([], result)
        database.single_query.assert_called_once()

        status = "complete"
        expected = result_to_json(exp_result)
        result = requests_db.get_jobs_by_status(status, 5)
        self.assertEqual(expected, result)
        database.single_query.assert_called()


    def test_get_utc_now_iso(self):
        """
        Tests the get_utc_now_iso function
        """
        utc_now_exp = "2019-07-17T17:36:38.494918"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        self.assertEqual(utc_now_exp, requests_db.get_utc_now_iso())


    def test_no_db_connect(self):
        """
        Tests a database connection failure
        """
        uuid.uuid4 = Mock(side_effect=[REQUEST_ID1])
        os.environ["DATABASE_NAME"] = "noexist"
        data = {}
        data["request_id"] = REQUEST_ID1
        data["request_group_id"] = requests_db.request_id_generator()
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "inprogress"
        mock_secretsmanager_get_parameter(1)
        exp_err = 'Database Error. FATAL:  database "noexist" does not exist\n'
        database.single_query = Mock(side_effect=[requests_db.DbError(
            exp_err)])
        try:
            requests_db.submit_request(data)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            database.single_query.assert_called_once()


    def test_request_id_generator(self):
        """
        Tests the request_id_generator function
        """
        requests_db.request_id_generator = Mock(return_value=REQUEST_GROUP_ID_EXP_1)
        self.assertEqual(REQUEST_GROUP_ID_EXP_1, requests_db.request_id_generator())


    def test_submit_request_bad_status(self):
        """
        Tests adding a job with an invalid status
        """
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests_db.request_id_generator = Mock(side_effect=[REQUEST_ID1])
        data = {}
        data["request_id"] = REQUEST_ID1
        data["request_group_id"] = REQUEST_GROUP_ID_EXP_1
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "invalid"
        data["last_update_time"] = utc_now_exp
        mock_err = ('Database Error. new row for relation "request_status" violates '
                    'check constraint "request_status_job_status_check" '
                    f'DETAIL:  Failing row contains (1306, {REQUEST_GROUP_ID_EXP_1}, '
                    'granule_1, thisisanobjectkey, restore, my_s3_bucket, invalid, '
                    '2019-07-31 18:05:19.161362+00, 2019-07-31 18:05:19.161362+00, null).')
        exp_err = ('new row for relation "request_status" violates check constraint '
                   '"request_status_job_status_check"')
        mock_secretsmanager_get_parameter(1)
        database.single_query = Mock(side_effect=[requests_db.DatabaseError(
            mock_err)])
        try:
            requests_db.submit_request(data)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertIn(exp_err, str(err))
            database.single_query.assert_called_once()


    def test_submit_request_error_status(self):
        """
        Tests that an error job is written to the db
        """
        utc_now_exp = UTC_NOW_EXP_4
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests_db.request_id_generator = Mock(side_effect=[REQUEST_ID4])
        data = {}
        data["request_id"] = REQUEST_ID4
        data["err_msg"] = "Error message goes here"
        data["request_group_id"] = REQUEST_GROUP_ID_EXP_2
        data["granule_id"] = "granule_4"
        data["object_key"] = "objectkey_4"
        data["job_type"] = "restore"
        data["job_status"] = "error"
        data["request_time"] = utc_now_exp
        qresult, exp_result = create_insert_request(
            REQUEST_ID4, data["request_group_id"],
            data["granule_id"], data["object_key"], data["job_type"],
            None, None, data["job_status"], data["request_time"],
            None, data["err_msg"])
        database.single_query = Mock(side_effect=[qresult, exp_result, None, None])
        mock_secretsmanager_get_parameter(4)
        try:
            requests_db.submit_request(data)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")

        try:
            result = requests_db.get_job_by_request_id(REQUEST_ID4)
            expected = result_to_json(exp_result)
            self.assertEqual(expected, result)
        except requests_db.DatabaseError as err:
            self.fail(f"get_job_by_request_id. {str(err)}")

    def test_create_data(self):
        """
        Tests the create_data function
        """
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"

        obj = {}
        obj["request_group_id"] = "my_request_group_id"
        obj["granule_id"] = "granule_1"
        obj["glacier_bucket"] = "my_bucket"
        obj["dest_bucket"] = "your_bucket"
        obj["key"] = "my_file"
        requests_db.request_id_generator = Mock(side_effect=[REQUEST_ID1])
        exp_data = {}
        exp_data["request_id"] = REQUEST_ID1
        exp_data["request_group_id"] = obj["request_group_id"]
        exp_data["granule_id"] = obj["granule_id"]
        exp_data["object_key"] = obj["key"]
        exp_data["job_type"] = "restore"
        exp_data["restore_bucket_dest"] = obj["glacier_bucket"]
        exp_data["archive_bucket_dest"] = obj["dest_bucket"]
        exp_data["job_status"] = "inprogress"
        exp_data["request_time"] = utc_now_exp
        exp_data["last_update_time"] = utc_now_exp

        data = requests_db.create_data(obj, exp_data["job_type"], exp_data["job_status"],
                                       utc_now_exp, utc_now_exp)

        self.assertEqual(exp_data, data)

    def test_submit_request_inprogress_status(self):
        """
        Tests that an inprogress job is written to the db
        """
        utc_now_exp = UTC_NOW_EXP_1
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests_db.request_id_generator = Mock(side_effect=[REQUEST_ID1])
        data = {}
        data["request_id"] = REQUEST_ID1
        data["request_group_id"] = REQUEST_GROUP_ID_EXP_1
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["archive_bucket_dest"] = "your_s3_bucket"
        data["job_status"] = "inprogress"
        data["request_time"] = utc_now_exp
        qresult, exp_result = create_insert_request(
            REQUEST_ID1, data["request_group_id"], data["granule_id"],
            data["object_key"], data["job_type"],
            data["restore_bucket_dest"], data["job_status"],
            data["archive_bucket_dest"],
            data["request_time"], None, None)
        database.single_query = Mock(side_effect=[qresult, exp_result, None, None])
        mock_secretsmanager_get_parameter(4)
        try:
            requests_db.submit_request(data)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")

        try:
            result = requests_db.get_job_by_request_id(REQUEST_ID1)
            expected = result_to_json(exp_result)
            self.assertEqual(expected, result)
        except requests_db.DatabaseError as err:
            self.fail(f"get_job_by_request_id. {str(err)}")


    def test_submit_request_missing_granuleid(self):
        """
        Tests adding a job with no granule_id
        """
        utc_now_exp = UTC_NOW_EXP_1
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests_db.request_id_generator = Mock(side_effect=[REQUEST_ID1])
        data = {}
        data["request_id"] = REQUEST_ID1
        data["request_group_id"] = REQUEST_GROUP_ID_EXP_1
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "invalid"
        data["request_time"] = utc_now_exp
        try:
            requests_db.submit_request(data)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            exp_msg = "Missing 'granule_id' in input data"
            self.assertEqual(exp_msg, str(err))


    def test_update_request_status_for_job(self):
        """
        Tests updating a job to an 'inprogress' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        request_id = REQUEST_ID3
        job_status = "inprogress"
        exp_result = []
        database.single_query = Mock(side_effect=[exp_result])
        mock_secretsmanager_get_parameter(1)
        try:
            result = requests_db.update_request_status_for_job(request_id, job_status)
            self.assertEqual([], result)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"update_request_status_for_job. {str(err)}")

    def test_update_request_status_for_job_exceptions(self):
        """
        Tests updating a job to an 'inprogress' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        request_id = REQUEST_ID3
        job_status = "inprogress"
        exp_err = 'A new status must be provided'
        try:
            requests_db.update_request_status_for_job(request_id, None)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual(exp_err, str(err))

        exp_err = 'No request_id provided'
        try:
            requests_db.update_request_status_for_job(None, job_status)
            self.fail("expected BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual(exp_err, str(err))

        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        database.single_query = Mock(side_effect=[DbError(exp_err)])
        mock_secretsmanager_get_parameter(1)
        try:
            requests_db.update_request_status_for_job(request_id, job_status)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            database.single_query.assert_called_once()


    def test_update_request_status_complete(self):
        """
        Tests updating a job to a 'complete' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        request_id = "thisisarequestid"
        job_status = "complete"
        exp_result = []
        database.single_query = Mock(side_effect=[exp_result])
        mock_secretsmanager_get_parameter(1)
        try:
            result = requests_db.update_request_status_for_job(request_id, job_status)
            self.assertEqual([], result)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")


    def test_update_request_status_error(self):
        """
        Tests updating a job to an 'error' status
        """
        _, exp_result = create_select_requests([REQUEST_ID4])
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        granule_id = "granule_4"
        job_status = "error"
        err_msg = "Error message goes here"

        empty_result = []
        database.single_query = Mock(side_effect=[empty_result, exp_result])
        mock_secretsmanager_get_parameter(2)
        try:
            result = requests_db.update_request_status_for_job(REQUEST_ID4, job_status, err_msg)
            self.assertEqual([], result)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")
        result = requests_db.get_jobs_by_granule_id(granule_id)
        self.assertEqual(err_msg, result[0]["err_msg"])


    def test_update_request_status_exception(self):
        """
        Tests updating a job to an invalid status
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        job_status = "invalid"
        exp_msg = ('Database Error. new row for relation "request_status" violates '
                   'check constraint "request_status_job_status_check"')
        database.single_query = Mock(side_effect=[requests_db.DatabaseError(exp_msg)])
        mock_secretsmanager_get_parameter(1)
        try:
            requests_db.update_request_status_for_job(REQUEST_ID6, job_status)
            self.fail("expected DatabaseError")
        except requests_db.DatabaseError as err:
            self.assertIn(exp_msg, str(err))
            database.single_query.assert_called_once()


    def test_update_request_status_missing_key(self):
        """
        Tests updating a job where the object_key isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        job_status = "invalid"
        exp_msg = "No object_key provided"
        database.single_query = Mock(side_effect=[requests_db.BadRequestError(exp_msg)])
        mock_secretsmanager_get_parameter(1)
        try:
            requests_db.update_request_status_for_job(REQUEST_ID1, job_status)
            self.fail("expected requests_db.BadRequestError")
        except requests_db.BadRequestError as err:
            self.assertEqual(exp_msg, str(err))


    def test_update_request_status_missing_status(self):
        """
        Tests updating a job where the status isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        request_id = None
        job_status = None
        exp_msg = "No request_id provided"
        try:
            result = requests_db.update_request_status_for_job(request_id, job_status)
            self.assertEqual([], result)
        except requests_db.BadRequestError as err:
            self.assertEqual(exp_msg, str(err))

    def test_update_request_status_notfound(self):
        """
        Tests updating a job where the object_key doesn't exist
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests_db.get_utc_now_iso = Mock(return_value=utc_now_exp)
        request_id = "notexists"
        job_status = "invalid"
        exp_result = []
        database.single_query = Mock(side_effect=[exp_result])
        mock_secretsmanager_get_parameter(1)
        try:
            result = requests_db.update_request_status_for_job(request_id, job_status)
            self.assertEqual([], result)
            database.single_query.assert_called_once()
        except requests_db.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")

