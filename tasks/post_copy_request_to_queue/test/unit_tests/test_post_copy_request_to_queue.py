"""
Name: test_post_copy_request_to_queue.py
Description: unit tests for post_copy_request_to_queue.py 

"""
import boto3
import json
import os
import random
from moto import mock_secretsmanager
from post_copy_request_to_queue import handler, task, exponential_delay
from unittest import mock, TestCase
from unittest.mock import Mock, call, patch, MagicMock
from requests_db import get_dbconnect_info, DatabaseError
from database import single_query, result_to_json
from botocore.exceptions import ClientError

class TestPostCopyRequestToQueue(TestCase):
    """
    Unit tests for the post_copy_request_to_queue lambda function.
    """
    # Create the mock instance of secrets manager
    mock_sm = mock_secretsmanager()

    def setUp(self):
        self.event = {
            "Records": [
                {
                    "eventName": "ObjectRestore:Completed",
                    "s3": {
                        "bucket": {
                            "name": "lambda-artifacts-deafc19498e3f2df",
                            "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df",
                        },
                        "object": {"key": "b21b84d653bb07b05b1e6b33684dc11b"},
                    },
                }
            ]
        }
        self.mock_sm.start()
        self.test_sm = boto3.client("secretsmanager", region_name="us-west-2")
        self.test_sm.create_secret(
            Name="dev-drdb-host", SecretString="postgres"
        )
        self.test_sm.create_secret(
            Name="dev-drdb-user-pass", SecretString="MySecretUserPassword"
        )

    def tearDown(self):
        """
        Perform tear down actions
        """
        self.mock_sm.stop()

    # ------------------------------test key_path is missing from event---------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_no_db_queue(self):
        """
        raises exception if db_queue_url is missing
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_empty_db_queue(self):
        """
        raises exception if db_queue_url is empty string
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    # ------------------------------test RECOVERY_QUEUE_URL env var---------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_no_recovery_queue(self):
        """
        raises exception if recovery_queue_url is missing.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_empty_recovery_queue(self):
        """
        raises exception if recovery_queue_url is empty string.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    # ------------------------------test MAX_RETRIES env var---------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_no_max_retries(self):
        """
        raises exception if MAX_RETRIES is missing.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_empty_max_retries(self):
        """
        raises exception if MAX_RETRIES is empty string.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "non-integer",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_non_int_max_retries(self):
        """
        raises ValueError if MAX_RETRIES is non-integer.
        """
        self.assertRaises(ValueError, handler, self.event, context=None)

    # ------------------------------test RETRY_SLEEP_SECS env var---------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_no_retry_sleep_secs(self):
        """
        raises exception if RETRY_SLEEP_SECS is missing.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_empty_retry_sleep_secs(self):
        """
        raises exception if RETRY_SLEEP_SECS is empty string.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "non-integer",
            "RETRY_BACKOFF": "2",
        },
        clear=True,
    )
    def test_event_non_int_retry_sleep_secs(self):
        """
        raises ValueError if RETRY_SLEEP_SECS is non-integer.
        """
        self.assertRaises(ValueError, handler, self.event, context=None)

    # ------------------------------test RETRY_BACKOFF env var---------------------------------------------------------------

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
        },
        clear=True,
    )
    def test_event_no_retry_backoff(self):
        """
        raises exception if RETRY_BACKOFF is missing.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "",
        },
        clear=True,
    )
    def test_event_empty_retry_backoff(self):
        """
        raises exception if RETRY_BACKOFF is empty string.
        """
        self.assertRaises(Exception, handler, self.event, context=None)

    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
            "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "non-integer",
        },
        clear=True,
    )
    def test_event_non_int_retry_backoff(self):
        """
        raises ValueError if RETRY_BACKOFF is non-integer.
        """
        self.assertRaises(ValueError, handler, self.event, context=None)

    # --------------------------------------exponential delay test---------------------------------
    def test_exponential_delay(self):
        """
        tests delay function. Raises TypeError when args are non-integer
        """
    
        base_delay = "non-integer"
        exponential_backoff = "non-integer"

        self.assertRaises(TypeError, exponential_delay, base_delay,exponential_backoff)

    # --------------------------------------task test---------------------------------

    # @patch.dict(
    #     os.environ,
    #     {
    #         "DB_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
    #         "RECOVERY_QUEUE_URL": "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
    #         "MAX_RETRIES": "2",
    #         "RETRY_SLEEP_SECS": "2",
    #         "RETRY_BACKOFF": "2",
    #         "DATABASE_PORT": "5432",
    #         "DATABASE_NAME": "disaster_recovery",
    #         "DATABASE_USER": "rhassan",
    #         # "dev-drdb-host": "test",
    #         # "dev-drdb-user-pass": "1234"
    #     },
    #     clear=True,
    # )
    # def test_task_others(self):
    #     """
    #     raises ClientError if secrets are not present in secrets manager
    #     """
    #     records = self.event["Records"]
    #     backoff_args = [
    #         "sqs.us-west-2.amazonaws.com/1234567890/dbqueue",
    #         "sqs.us-west-2.amazonaws.com/1234567890/recoveryqueue",
    #         2,
    #         2,
    #         2,
    #     ]
    #     self.assertRaises(ClientError, task, records, *backoff_args)