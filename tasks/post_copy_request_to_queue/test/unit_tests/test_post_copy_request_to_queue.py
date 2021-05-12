"""
Name: test_post_copy_request_to_queue.py
Description: unit tests for post_copy_request_to_queue.py 

"""
import boto3
import json
import os
import random
from moto import mock_sqs, mock_secretsmanager
from post_copy_request_to_queue import handler, task, exponential_delay
from unittest import mock, TestCase
from unittest.mock import Mock, call, patch, MagicMock
from requests_db import get_dbconnect_info, DatabaseError
from database import single_query, result_to_json, get_db_connect_info
from shared_recovery import OrcaStatus


class TestPostCopyRequestToQueue(TestCase):
    """
    Unit tests for the post_copy_request_to_queue lambda function.
    """

    # Create the mock instance for unit tests
    mock_sqs = mock_sqs()
    mock_sm = mock_secretsmanager()

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.mock_sm.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.db_queue = self.test_sqs.create_queue(QueueName="dbqueue")
        self.recovery_queue = self.test_sqs.create_queue(QueueName="recoveryqueue")
        self.db_queue_url = self.db_queue.url
        self.recovery_queue_url = self.recovery_queue.url

        self.test_sm = boto3.client("secretsmanager", region_name="us-west-2")
        self.test_sm.create_secret(
            Name="dev-drdb-host", SecretString="aws.postgresrds.host"
        )
        self.test_sm.create_secret(
            Name="dev-drdb-user-pass", SecretString="MySecretUserPassword"
        )

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

    def tearDown(self):
        """
        Perform tear down actions
        """
        self.mock_sqs.stop()
        self.mock_sm.stop()

    # ------------------------------test key_path is missing from event---------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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

        self.assertRaises(TypeError, exponential_delay, base_delay, exponential_backoff)

    # --------------------------------------task test that is having issues---------------------------------

    @patch.dict(
        os.environ,
        {
            "PREFIX": "dev",
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
            "MAX_RETRIES": "2",
            "RETRY_SLEEP_SECS": "2",
            "RETRY_BACKOFF": "2",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "disaster_recovery",
            "DATABASE_USER": "rhassan",
        },
        clear=True,
    )
    @patch("database.single_query")
    def test_task_happy_path(self, mock_single_query: MagicMock):
        mock_single_query.return_value = {
            "job_id": "1",
            "granule_id": "3",
            "filename": "f1.doc",
            "restore_destination": "s3://restore",
        }
        records = self.event["Records"]
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            2,
            2,
            2,
        ]
        # task(records, *backoff_args)

        sql = """
            SELECT
                job_id, granule_id, filename, restore_destination
            FROM
                orca_recoverfile
            WHERE
                key_path = %s
            AND
                status_id = %d
            """
        db_connect_info = get_dbconnect_info()
        for record in records:
            key_path = record["s3"]["object"]["key"]

        mock_single_query.assert_called_once_with(
            sql, db_connect_info, (key_path, OrcaStatus.PENDING.value)
        )
