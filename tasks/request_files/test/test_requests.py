"""
Name: test_requests.py

Description:  Unit tests for requests.py.
"""

import os
import time
import unittest
from unittest.mock import Mock

import psycopg2

import requests
#import utils
from requests import create_data

#from psycopg2 import connect as psycopg2_connect



class TestRequests(unittest.TestCase):
    """
    TestRequestFiles.
    """

    def setUp(self):

        prefix = "lab"
        os.environ["PREFIX"] = prefix
        os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
        os.environ["DATABASE_NAME"] = "labsndbx"
        os.environ["DATABASE_USER"] = "druser"
        os.environ["DATABASE_PW"] = "July2019"
        self.utc_now_exp_1 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_1 = requests.request_id_generator()
        self.utc_now_exp_2 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_2 = requests.request_id_generator()
        self.utc_now_exp_3 = requests.get_utc_now_iso()
        time.sleep(1)
        self.utc_now_exp_4 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_3 = requests.request_id_generator()
        self.utc_now_exp_5 = requests.get_utc_now_iso()
        time.sleep(1)
        self.utc_now_exp_6 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_4 = requests.request_id_generator()
        self.utc_now_exp_7 = requests.get_utc_now_iso()
        time.sleep(1)
        self.utc_now_exp_8 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_5 = requests.request_id_generator()
        self.utc_now_exp_9 = requests.get_utc_now_iso()
        time.sleep(1)
        self.request_id_exp_6 = requests.request_id_generator()
        self.utc_now_exp_10 = requests.get_utc_now_iso()
        time.sleep(1)
        self.utc_now_exp_11 = requests.get_utc_now_iso()
        self.mock_utcnow = requests.get_utc_now_iso
        self.mock_request_id = requests.request_id_generator
        self.mock_connect = psycopg2.connect


    def tearDown(self):
        try:
            results = requests.get_all_requests()
            for job in results:
                print("job: ", job)
            self.delete_all_requests()
        except requests.NotFound:
            pass
        except requests.DatabaseError:
            pass

        psycopg2.connect = self.mock_connect
        requests.request_id_generator = self.mock_request_id
        requests.get_utc_now_iso = self.mock_utcnow
        del os.environ["PREFIX"]
        del os.environ["DATABASE_HOST"]
        del os.environ["DATABASE_NAME"]
        del os.environ["DATABASE_USER"]
        del os.environ["DATABASE_PW"]

    def delete_all_requests(self):
        """
        Deletes all jobs from the request_status table
        """
        try:
            result = requests.get_all_requests()
            for job in result:
                requests.delete_request(job["job_id"])
        except requests.NotFound:
            pass
        except requests.DatabaseError:
            pass


    def create_test_requests(self):
        """
        creates jobs in the db
        """
        #utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        #request_id_exp = "0000a0a0-a000-00a0-00a0-0000a0000000"
        requests.get_utc_now_iso = Mock(side_effect=[self.utc_now_exp_1, self.utc_now_exp_4,
                                                     self.utc_now_exp_2, self.utc_now_exp_5,
                                                     self.utc_now_exp_3, self.utc_now_exp_6,
                                                     self.utc_now_exp_4, self.utc_now_exp_4,
                                                     self.utc_now_exp_5, self.utc_now_exp_5,
                                                     self.utc_now_exp_6, self.utc_now_exp_6,
                                                     self.utc_now_exp_7, self.utc_now_exp_7,
                                                     self.utc_now_exp_8, self.utc_now_exp_8,
                                                     self.utc_now_exp_9, self.utc_now_exp_9,
                                                     self.utc_now_exp_10, self.utc_now_exp_10,
                                                     self.utc_now_exp_11, self.utc_now_exp_11])
        requests.request_id_generator = Mock(side_effect=[self.request_id_exp_1,
                                                          self.request_id_exp_2,
                                                          self.request_id_exp_3,
                                                          self.request_id_exp_4,
                                                          self.request_id_exp_5,
                                                          self.request_id_exp_6])

        try:
            data = create_data(self.request_id_exp_1, "granule_1", "objectkey_1",
                               "restore", "my_s3_bucket",
                               "complete", self.utc_now_exp_1, self.utc_now_exp_4)
            self.job_id_1 = requests.submit_request(data)
            data = create_data(self.request_id_exp_1, "granule_2", "objectkey_2",
                               "restore", "my_s3_bucket",
                               "complete", self.utc_now_exp_2, self.utc_now_exp_5)
            self.job_id_2 = requests.submit_request(data)
            data = create_data(self.request_id_exp_1, "granule_3", "objectkey_3",
                               "restore", "my_s3_bucket",
                               "complete", self.utc_now_exp_3, self.utc_now_exp_6)
            self.job_id_3 = requests.submit_request(data)

            data = create_data(self.request_id_exp_2, "granule_4", "objectkey_4",
                               "restore", "my_s3_bucket",
                               "error", self.utc_now_exp_4, None)
            self.job_id_4 = requests.submit_request(data)

            data = create_data(self.request_id_exp_3, "granule_5", "objectkey_5",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_5, self.utc_now_exp_5)
            self.job_id_5 = requests.submit_request(data)
            data = create_data(self.request_id_exp_3, "granule_6", "objectkey_6",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_6, self.utc_now_exp_6)
            self.job_id_6 = requests.submit_request(data)

            data = create_data(self.request_id_exp_4, "granule_4", "objectkey_4",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_7, self.utc_now_exp_7)
            self.job_id_7 = requests.submit_request(data)

            data = create_data(self.request_id_exp_5, "granule_1", "objectkey_1",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_8, self.utc_now_exp_8)
            self.job_id_8 = requests.submit_request(data)
            data = create_data(self.request_id_exp_5, "granule_2", "objectkey_2",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_9, self.utc_now_exp_9)
            self.job_id_9 = requests.submit_request(data)
            data = create_data(self.request_id_exp_5, "granule_3", "objectkey_3",
                               "restore", "my_s3_bucket",
                               "inprogress", self.utc_now_exp_10, self.utc_now_exp_10)
            self.job_id_10 = requests.submit_request(data)

            data = create_data(self.request_id_exp_6, "granule_7", "objectkey_7",
                               "regenerate", None,
                               "inprogress", self.utc_now_exp_11, self.utc_now_exp_11)
            self.job_id_11 = requests.submit_request(data)
            #results = requests.get_all_requests()
            #for job in results:
            #    print("job: ", job)
        except requests.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")


    def test_get_utc_now_iso(self):
        """
        Tests the get_utc_now_iso function
        """
        utc_now_exp = "2019-07-17T17:36:38.494918"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        self.assertEqual(utc_now_exp, requests.get_utc_now_iso())

    def test_request_id_generator(self):
        """
        Tests the request_id_generator function
        """
        request_id = requests.request_id_generator()
        #request_id = "0000a0a0-a000-00a0-00a0-0000a0000000"
        requests.request_id_generator = Mock(return_value=request_id)
        self.assertEqual(request_id, requests.request_id_generator())

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

        try:
            requests.submit_request(data)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual(exp_err, str(err))

    def test_submit_request(self):
        """
        Tests that a job is written to the db
        """
        self.create_test_requests()
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        request_id_exp = "0000a0a0-a000-00a0-00a0-0000a0000000"
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
        try:
            job_id = requests.submit_request(data)
            self.assertGreater(job_id, 0, "job_id should be greater than 0")
        except requests.DatabaseError as err:
            self.fail(f"submit_request. {str(err)}")

        try:
            result = requests.get_request_by_job_id(job_id)
            result.pop("job_id")
            data["last_update_time"] = utc_now_exp
            self.assertEqual(data, result)
        except requests.DatabaseError as err:
            self.fail(f"get_request_by_job_id. {str(err)}")

    def test_get_request_not_found(self):
        """
        Tests reading a job that doesn't exist
        """
        job_id = 500000

        try:
            requests.get_request_by_job_id(job_id)
            self.fail("expected NotFound")
        except requests.NotFound as err:
            self.assertEqual(f"Unknown job_id: {job_id}", str(err))

    def test_get_request_exception(self):
        """
        Tests getting a DatabaseError reading a job
        """
        self.create_test_requests()
        #psycopg2.connect = Mock(side_effect=[psycopg2.DbError(
        #    "Internal database error, please contact LP DAAC User Services")])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests.get_request_by_job_id('x')
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            exp_msg = ('Database Error. could not connect to server: Connection timed out')
            self.assertIn(exp_msg, str(err))

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
        try:
            requests.submit_request(data)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            exp_msg = ('new row for relation "request_status" violates check constraint '
                       '"request_status_job_status_check"')
            self.assertIn(exp_msg, str(err))

    def test_submit_request_missing_granuleid(self):
        """
        Tests adding a job with no granule_id
        """
        utc_now_exp = "2019-07-31 18:05:19.161362+00:00"
        request_id_exp = "0000a0a0-a000-00a0-00a0-0000a0000000"
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

    def test_update_request_status_complete(self):
        """
        Tests updating a job to a 'complete' status
        """
        self.create_test_requests()
        utc_now_exp = "2019-07-31 21:07:15.234362+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "thisisanobjectkey"
        job_status = "complete"
        try:
            result = requests.update_request_status(object_key, job_status)
            self.assertEqual([], result)
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")

    def test_update_request_status_error(self):
        """
        Tests updating a job to a 'error' status
        """
        self.create_test_requests()
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "objectkey_5"
        job_status = "error"
        try:
            result = requests.update_request_status(object_key, job_status)
            self.assertEqual([], result)
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")

    def test_update_request_status_exception(self):
        """
        Tests updating a job to an invalid status
        """
        self.create_test_requests()
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "objectkey_6"
        job_status = "invalid"
        try:
            requests.update_request_status(object_key, job_status)
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            exp_msg = ('Database Error. new row for relation "request_status" violates '
                       'check constraint "request_status_job_status_check"')
            self.assertIn(exp_msg, str(err))

    def test_update_request_status_notfound(self):
        """
        Tests updating a job where the object_key doesn't exist
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "noexist"
        job_status = "invalid"
        try:
            result = requests.update_request_status(object_key, job_status)
            self.assertEqual([], result)
        except requests.DatabaseError as err:
            self.fail(f"update_request_status. {str(err)}")

    def test_update_request_status_missing_key(self):
        """
        Tests updating a job where the object_key isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = None
        job_status = "invalid"
        try:
            result = requests.update_request_status(object_key, job_status)
            self.assertEqual([], result)
        except requests.BadRequestError as err:
            exp_msg = "No object_key provided"
            self.assertEqual(exp_msg, str(err))

    def test_update_request_status_missing_status(self):
        """
        Tests updating a job where the status isn't given
        """
        utc_now_exp = "2019-07-31 19:21:38.263364+00:00"
        requests.get_utc_now_iso = Mock(return_value=utc_now_exp)
        object_key = "noexist"
        job_status = None
        try:
            result = requests.update_request_status(object_key, job_status)
            self.assertEqual([], result)
        except requests.BadRequestError as err:
            exp_msg = "A new status must be provided"
            self.assertEqual(exp_msg, str(err))

    def test_get_all_requests(self):
        """
        Tests reading all requests
        """
        self.create_test_requests()
        result = requests.get_all_requests()
        exp_ids = [self.job_id_1, self.job_id_2, self.job_id_3, self.job_id_4, self.job_id_5,
                   self.job_id_6, self.job_id_7, self.job_id_8, self.job_id_9, self.job_id_10,
                   self.job_id_11]
        idx = 0
        for job in result:
            self.assertEqual(exp_ids[idx], job["job_id"])
            idx = idx + 1

    def test_get_requests_by_status(self):
        """
        Tests reading by status
        """
        self.create_test_requests()
        status = "noexist"
        try:
            result = requests.get_requests_by_status(status)
            self.fail("expected NotFound")
        except requests.NotFound as err:
            self.assertEqual("No jobs found", str(err))

        status = "complete"
        result = requests.get_requests_by_status(status)
        exp_ids = [self.job_id_1, self.job_id_2, self.job_id_3]
        idx = 0
        for job in result:
            self.assertEqual(exp_ids[idx], job["job_id"])
            idx = idx + 1


    def test_get_requests_by_status_max_days(self):
        """
        Tests reading by status
        """
        self.create_test_requests()
        status = "noexist"
        try:
            result = requests.get_requests_by_status(status)
            self.fail("expected NotFound")
        except requests.NotFound as err:
            self.assertEqual("No jobs found", str(err))

        status = "complete"
        result = requests.get_requests_by_status(status, 5)
        exp_ids = [self.job_id_1, self.job_id_2, self.job_id_3]
        idx = 0
        for job in result:
            self.assertEqual(exp_ids[idx], job["job_id"])
            idx = idx + 1


    def test_get_request_by_status_exception(self):
        """
        Tests getting a DatabaseError reading a job by status
        """
        self.create_test_requests()
        status = None
        try:
            requests.get_requests_by_status(status)
            self.fail("expected DatabaseError")
        except requests.BadRequestError as err:
            self.assertEqual('A status must be provided', str(err))

        status = "error"
        #psycopg2.connect = Mock(side_effect=[psycopg2.DbError(
        #    "Internal database error, please contact LP DAAC User Services")])
        os.environ["DATABASE_HOST"] = "unknown.cr.usgs.gov"
        try:
            requests.get_requests_by_status(status)
            #os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            #os.environ["DATABASE_HOST"] = "elpdvx143.cr.usgs.gov"
            exp_msg = ('Database Error. could not connect to server: Connection timed out')
            self.assertIn(exp_msg, str(err))

    def test_delete_request(self):
        """
        Tests deleting a job by job_id
        """
        try:
            self.create_test_requests()
            result = requests.delete_request(self.job_id_1)
            self.assertEqual([], result)
        except requests.DatabaseError as err:
            self.fail(f"delete_request. {str(err)}")

    def test_delete_request_exception(self):
        """
        Tests deleting a job by job_id
        """
        try:
            #self.create_test_requests()
            requests.delete_request('x')
            self.fail("expected DatabaseError")
        except requests.DatabaseError as err:
            self.assertEqual("Database Error. Internal database error, "
                             "please contact LP DAAC User Services", str(err))
