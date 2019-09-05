"""
Name: test_requests.py

Description:  Unit tests for requests.py.
"""

import os
import unittest
from unittest.mock import Mock

import requests
from requests import result_to_json
import utils
import utils.database
from utils.database import DbError
from request_helpers import (
    JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5, JOB_ID_6, JOB_ID_7,
    JOB_ID_8, JOB_ID_9, JOB_ID_10, JOB_ID_11, REQUEST_ID_EXP_1,
    REQUEST_ID_EXP_2, REQUEST_ID_EXP_3, UTC_NOW_EXP_1, UTC_NOW_EXP_4,
    create_insert_request, create_select_requests)


class TestRequests(unittest.TestCase):
    """
    TestRequestFiles.
    """

    def setUp(self):

        prefix = "lab"
        os.environ["PREFIX"] = prefix
        os.environ["DATABASE_HOST"] = "my.db.host.gov"
        os.environ["DATABASE_NAME"] = "sndbx"
        os.environ["DATABASE_USER"] = "unittestdbuser"
        os.environ["DATABASE_PW"] = "unittestdbpw"

        self.mock_utcnow = requests.get_utc_now_iso
        self.mock_request_id = requests.request_id_generator
        self.mock_single_query = utils.database.single_query


    def tearDown(self):
        utils.database.single_query = self.mock_single_query
        requests.request_id_generator = self.mock_request_id
        requests.get_utc_now_iso = self.mock_utcnow
        del os.environ["PREFIX"]
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]


    def test_delete_all_requests(self):
        """
        Tests deleting all requests from the request_status table
        """
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5,
                       JOB_ID_6, JOB_ID_7, JOB_ID_8, JOB_ID_9, JOB_ID_10,
                       JOB_ID_11]
        try:
            qresult = create_select_requests(exp_job_ids)
            empty_result = []
            utils.database.single_query = Mock(
                side_effect=[qresult, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result, empty_result, empty_result,
                             empty_result])
            result = requests.delete_all_requests()
            utils.database.single_query.assert_called()
            self.assertEqual(empty_result, result)
        except requests.DatabaseError as err:
            self.fail(f"delete_all_requests. {str(err)}")

    def test_delete_all_requests_dberror(self):
        """
        Tests db error deleting all requests from the request_status table
        """
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        try:
            utils.database.single_query = Mock(
                side_effect=[DbError(exp_err)])
            requests.delete_all_requests()
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
        utils.database.single_query.assert_called_once()

    def test_delete_all_requests_dberror2(self):
        """
        Tests db error deleting one of the individual requests from the request_status table
        """
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5,
                       JOB_ID_6, JOB_ID_7, JOB_ID_8, JOB_ID_9, JOB_ID_10,
                       JOB_ID_11]
        try:
            qresult = create_select_requests(exp_job_ids)
            empty_result = []
            utils.database.single_query = Mock(
                side_effect=[qresult, empty_result,
                             DbError(exp_err),
                             empty_result])
            requests.delete_all_requests()
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
        utils.database.single_query.assert_called()

    def test_delete_request(self):
        """
        Tests deleting a job by job_id
        """
        try:
            exp_result = []
            utils.database.single_query = Mock(side_effect=[exp_result])
            result = requests.delete_request(JOB_ID_1)
            self.assertEqual(exp_result, result)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"delete_request. {str(err)}")

    def test_delete_request_no_job_id(self):
        """
        Tests no job_id given for deleting a job by job_id
        """
        try:
            utils.database.single_query = Mock(side_effect=
                                               [requests.BadRequestError("No job_id provided")])
            requests.delete_request(None)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual("No job_id provided", str(err))


    def test_delete_request_database_error(self):
        """
        Tests database error while deleting a job by job_id
        """
        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        try:
            utils.database.single_query = Mock(side_effect=[DbError(exp_err)])
            requests.delete_request('x')
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            utils.database.single_query.assert_called_once()


    def test_get_all_requests(self):
        """
        Tests reading all requests
        """
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3, JOB_ID_4, JOB_ID_5,
                       JOB_ID_6, JOB_ID_7, JOB_ID_8, JOB_ID_9, JOB_ID_10,
                       JOB_ID_11]
        qresult, exp_result = create_select_requests(exp_job_ids)
        utils.database.single_query = Mock(side_effect=[qresult])
        expected = result_to_json(exp_result)
        result = requests.get_all_requests()
        utils.database.single_query.assert_called_once()
        self.assertEqual(expected, result)


    def test_get_jobs_by_status_exceptions(self):
        """
        Tests getting a DatabaseError reading a job by status
        """
        utils.database.single_query = Mock(side_effect=[requests.BadRequestError(
            'A status must be provided')])
        status = None
        try:
            requests.get_jobs_by_status(status)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual('A status must be provided', str(err))

        status = "error"
        err_msg = 'Database Error. could not connect to server'
        utils.database.single_query = Mock(side_effect=[DbError(
            err_msg)])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests.get_jobs_by_status(status)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            utils.database.single_query.assert_called_once()
            self.assertEqual(err_msg, str(err))


    def test_get_job_by_job_id_dberror(self):
        """
        Tests getting a DatabaseError reading a job by job_id
        """
        exp_msg = 'Database Error. could not connect to server'
        utils.database.single_query = Mock(side_effect=[DbError(exp_msg)])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests.get_job_by_job_id('x')
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_msg, str(err))
            utils.database.single_query.assert_called_once()


    def test_get_request_not_found(self):
        """
        Tests reading a job that doesn't exist
        """
        job_id = 500000
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result])
        result = requests.get_job_by_job_id(job_id)
        self.assertEqual(exp_result, result)
        utils.database.single_query.assert_called_once()


    def test_get_jobs_by_request_id(self):
        """
        Tests reading a job by request_id
        """
        exp_job_ids = [JOB_ID_5, JOB_ID_6]
        _, exp_result = create_select_requests(exp_job_ids)
        utils.database.single_query = Mock(side_effect=[exp_result])
        expected = result_to_json(exp_result)
        try:
            result = requests.get_jobs_by_request_id(None)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual("A request_id must be provided", str(err))
        try:
            result = requests.get_jobs_by_request_id(REQUEST_ID_EXP_3)
        except requests.BadRequestError as err:
            self.fail(str(err))
        self.assertEqual(expected, result)
        utils.database.single_query.assert_called_once()

    def test_get_jobs_by_granule_id_dberror(self):
        """
        Tests db error reading by granule_id
        """
        utils.database.single_query = Mock(side_effect=[DbError("DbError reading requests")])
        try:
            requests.get_jobs_by_granule_id("gran_1")
            self.fail("expected DbError")
        except requests.DatabaseError as err:
            self.assertEqual("DbError reading requests", str(err))
            utils.database.single_query.assert_called_once()


    def test_get_jobs_by_status(self):
        """
        Tests reading by status
        """
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3]
        _, exp_result_2 = create_select_requests(exp_job_ids)
        status = "noexist"
        exp_result_1 = []
        utils.database.single_query = Mock(side_effect=[exp_result_1, exp_result_2])
        result = requests.get_jobs_by_status(status)
        self.assertEqual(exp_result_1, result)
        utils.database.single_query.assert_called_once()

        status = "complete"
        expected = result_to_json(exp_result_2)
        result = requests.get_jobs_by_status(status)
        self.assertEqual(expected, result)
        utils.database.single_query.assert_called()


    def test_get_jobs_by_status_max_days(self):
        """
        Tests reading by status for limited days
        """
        exp_job_ids = [JOB_ID_1, JOB_ID_2, JOB_ID_3]
        _, exp_result = create_select_requests(exp_job_ids)
        status = "noexist"
        utils.database.single_query = Mock(side_effect=[[], exp_result])
        result = requests.get_jobs_by_status(status)
        self.assertEqual([], result)
        utils.database.single_query.assert_called_once()

        status = "complete"
        expected = result_to_json(exp_result)
        result = requests.get_jobs_by_status(status, 5)
        self.assertEqual(expected, result)
        utils.database.single_query.assert_called()


    def test_get_utc_now_iso(self):
        """
        Tests the get_utc_now_iso function
        """
        utc_now_exp = "2019-07-17T17:36:38.494918"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        self.assertEqual(utc_now_exp, requests.get_utc_now_iso())


    def test_no_db_connect(self):
        """
        Tests a database connection failure
        """
        os.environ["DATABASE_NAME"] = "noexist"
        data = {}
        data["request_id"] = "0000a0a0-a000-00a0-00a0-0000a0000000"
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "inprogress"
        exp_err = 'Database Error. FATAL:  database "noexist" does not exist\n'
        utils.database.single_query = Mock(side_effect=[requests.DatabaseError(
            exp_err)])
        try:
            requests.submit_request(data)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            utils.database.single_query.assert_called_once()


    def test_request_id_generator(self):
        """
        Tests the request_id_generator function
        """
        request_id = requests.request_id_generator()
        requests.request_id_generator = Mock(return_value=request_id)
        self.assertEqual(request_id, requests.request_id_generator())


    def test_submit_request_bad_status(self):
        """
        Tests adding a job with an invalid status
        """
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        request_id_exp = "0000a0a0-a000-00a0-00a0-0000a0000000"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests.request_id_generator = Mock(return_value=request_id_exp)
        data = {}
        data["request_id"] = request_id_exp
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "invalid"
        data["last_update_time"] = utc_now_exp
        mock_err = ('Database Error. new row for relation "request_status" violates '
                    'check constraint "request_status_job_status_check" '
                    f'DETAIL:  Failing row contains (1306, {request_id_exp}, '
                    'granule_1, thisisanobjectkey, restore, my_s3_bucket, invalid, '
                    '2019-07-31 18:05:19.161362+00, 2019-07-31 18:05:19.161362+00, null).')
        exp_err = ('new row for relation "request_status" violates check constraint '
                   '"request_status_job_status_check"')
        utils.database.single_query = Mock(side_effect=[requests.DatabaseError(
            mock_err)])
        try:
            requests.submit_request(data)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertIn(exp_err, str(err))
            utils.database.single_query.assert_called_once()


    def test_submit_request_error_status(self):
        """
        Tests that an error job is written to the db
        """
        utc_now_exp = UTC_NOW_EXP_4
        request_id_exp = REQUEST_ID_EXP_2
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests.request_id_generator = Mock(return_value=request_id_exp)

        data = {}
        data["err_msg"] = "Error message goes here"
        data["request_id"] = requests.request_id_generator()
        data["granule_id"] = "granule_4"
        data["object_key"] = "objectkey_4"
        data["job_type"] = "restore"
        #data["restore_bucket_dest"] = ""
        data["job_status"] = "error"
        data["request_time"] = utc_now_exp
        qresult, exp_result = create_insert_request(
            JOB_ID_4, data["request_id"],
            data["granule_id"], data["object_key"], data["job_type"],
            None, data["job_status"], data["request_time"],
            None, data["err_msg"])
        utils.database.single_query = Mock(side_effect=[qresult, exp_result, None, None])
        try:
            job_id = requests.submit_request(data)
            self.assertEqual(JOB_ID_4, job_id)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")

        try:
            result = requests.get_job_by_job_id(job_id)
            expected = result_to_json(exp_result)
            self.assertEqual(expected, result)
        except requests.DatabaseError as err:
            self.fail(f"get_job_by_job_id. {str(err)}")

    def test_create_data(self):
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        exp_data = {}
        
        exp_data["request_id"] = "my_request_id"
        exp_data["granule_id"] = "granule_1"
        exp_data["object_key"] = "my_file"
        exp_data["job_type"] = "restore"
        exp_data["restore_bucket_dest"] = "my_bucket"
        exp_data["job_status"] = "inprogress"
        exp_data["request_time"] = utc_now_exp
        exp_data["last_update_time"] = utc_now_exp

        data = requests.create_data("my_request_id", "granule_1", "my_file", "restore",
                "my_bucket", "inprogress", utc_now_exp,
                utc_now_exp)

        self.assertEqual(exp_data, data)

    def test_submit_request_inprogress_status(self):
        """
        Tests that an inprogress job is written to the db
        """
        utc_now_exp = UTC_NOW_EXP_1
        request_id_exp = REQUEST_ID_EXP_1
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests.request_id_generator = Mock(return_value=request_id_exp)

        data = {}
        data["request_id"] = requests.request_id_generator()
        data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "inprogress"
        data["request_time"] = utc_now_exp
        qresult, exp_result = create_insert_request(
            JOB_ID_1, data["request_id"], data["granule_id"],
            data["object_key"], data["job_type"],
            data["restore_bucket_dest"], data["job_status"],
            data["request_time"], None, None)
        utils.database.single_query = Mock(side_effect=[qresult, exp_result, None, None])
        try:
            job_id = requests.submit_request(data)
            self.assertEqual(JOB_ID_1, job_id)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")

        try:
            result = requests.get_job_by_job_id(job_id)
            expected = result_to_json(exp_result)
            self.assertEqual(expected, result)
        except requests.DatabaseError as err:
            self.fail(f"get_job_by_job_id. {str(err)}")


    def test_submit_request_missing_granuleid(self):
        """
        Tests adding a job with no granule_id
        """
        utc_now_exp = UTC_NOW_EXP_1
        request_id_exp = REQUEST_ID_EXP_1
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        requests.request_id_generator = Mock(return_value=request_id_exp)
        data = {}
        data["request_id"] = request_id_exp
        #data["granule_id"] = "granule_1"
        data["object_key"] = "thisisanobjectkey"
        data["job_type"] = "restore"
        data["restore_bucket_dest"] = "my_s3_bucket"
        data["job_status"] = "invalid"
        data["request_time"] = utc_now_exp
        try:
            requests.submit_request(data)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            exp_msg = "Missing 'granule_id' in input data"
            self.assertEqual(exp_msg, str(err))


    def test_update_request_status_for_job(self):
        """
        Tests updating a job to an 'inprogress' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        job_id = JOB_ID_3
        job_status = "inprogress"
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = requests.update_request_status_for_job(job_id, job_status)
            self.assertEqual([], result)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"update_request_status_for_job. {str(err)}")

    def test_update_request_status_for_job_exceptions(self):
        """
        Tests updating a job to an 'inprogress' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        job_id = JOB_ID_3
        job_status = "inprogress"
        exp_err = 'A new status must be provided'
        try:
            requests.update_request_status_for_job(job_id, None)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual(exp_err, str(err))

        exp_err = 'No job_id provided'
        try:
            requests.update_request_status_for_job(None, job_status)
            self.fail("expected BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual(exp_err, str(err))

        exp_err = 'Database Error. Internal database error, please contact LP DAAC User Services'
        utils.database.single_query = Mock(side_effect=[DbError(exp_err)])
        #exp_result = []
        #utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            requests.update_request_status_for_job(job_id, job_status)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))
            utils.database.single_query.assert_called_once()


    def test_update_request_status_complete(self):
        """
        Tests updating a job to a 'complete' status
        """
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "thisisanobjectkey"
        old_status = "inprogress"
        job_status = "complete"
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = requests.update_request_status(object_key, old_status, job_status)
            self.assertEqual([], result)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")


    def test_update_request_status_error(self):
        """
        Tests updating a job to an 'error' status
        """
        _, exp_result = create_select_requests(
            [JOB_ID_4])
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "objectkey_4"
        granule_id = "granule_4"
        old_status = "inprogress"
        job_status = "error"
        err_msg = "Error message goes here"

        empty_result = []
        utils.database.single_query = Mock(side_effect=[empty_result, exp_result])
        try:
            result = requests.update_request_status(object_key, old_status, job_status, err_msg)
            self.assertEqual([], result)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")
        result = requests.get_jobs_by_granule_id(granule_id)
        self.assertEqual(err_msg, result["err_msg"])


    def test_update_request_status_exception(self):
        """
        Tests updating a job to an invalid status
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "objectkey_6"
        old_status = "inprogress"
        job_status = "invalid"
        exp_msg = ('Database Error. new row for relation "request_status" violates '
                   'check constraint "request_status_job_status_check"')
        utils.database.single_query = Mock(side_effect=[requests.DatabaseError(exp_msg)])
        try:
            requests.update_request_status(object_key, old_status, job_status)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertIn(exp_msg, str(err))
            utils.database.single_query.assert_called_once()


    def test_update_request_status_missing_key(self):
        """
        Tests updating a job where the object_key isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = None
        old_status = "inprogress"
        job_status = "invalid"
        exp_msg = "No object_key provided"
        utils.database.single_query = Mock(side_effect=[requests.BadRequestError(exp_msg)])
        try:
            requests.update_request_status(object_key, old_status, job_status)
            self.fail("expected requests.BadRequestError")
        except requests.BadRequestError as err:
            self.assertEqual(exp_msg, str(err))


    def test_update_request_status_missing_status(self):
        """
        Tests updating a job where the status isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        old_status = "inprogress"
        object_key = "noexist"
        job_status = None
        exp_msg = "A new status must be provided"
        try:
            result = requests.update_request_status(object_key, old_status, job_status)
            self.assertEqual([], result)
        except requests.BadRequestError as err:
            self.assertEqual(exp_msg, str(err))

        old_status = None
        job_status = "complete"
        exp_msg = "An old status must be provided"
        try:
            result = requests.update_request_status(object_key, old_status, job_status)
            self.assertEqual([], result)
        except requests.BadRequestError as err:
            self.assertEqual(exp_msg, str(err))


    def test_update_request_status_notfound(self):
        """
        Tests updating a job where the object_key doesn't exist
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "noexist"
        old_status = "inprogress"
        job_status = "invalid"
        exp_result = []
        utils.database.single_query = Mock(side_effect=[exp_result])
        try:
            result = requests.update_request_status(object_key, old_status, job_status)
            self.assertEqual([], result)
            utils.database.single_query.assert_called_once()
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")
