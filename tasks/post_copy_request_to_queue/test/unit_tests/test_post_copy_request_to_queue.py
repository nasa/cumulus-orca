"""
Name: test_post_copy_request_to_queue.py
Description: unit tests for post_copy_request_to_queue.py 

"""
import boto3
import os
from moto import mock_sqs
from post_copy_request_to_queue import handler, task, exponential_delay
from unittest import TestCase
from unittest.mock import patch, MagicMock
from shared_recovery import OrcaStatus


class TestPostCopyRequestToQueue(TestCase):
    """
    Unit tests for the post_copy_request_to_queue lambda function.
    """

    # Create the mock instance for unit tests
    mock_sqs = mock_sqs()

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.db_queue = self.test_sqs.create_queue(QueueName="dbqueue")
        self.recovery_queue = self.test_sqs.create_queue(QueueName="recoveryqueue")
        self.db_queue_url = self.db_queue.url
        self.recovery_queue_url = self.recovery_queue.url
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
    # --------------------------------------unit test for task fn.---------------------------------
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
    @patch("requests_db.get_dbconnect_info")

    def test_task_happy_path(self, mock_get_db_connect_info: MagicMock, mock_single_query: MagicMock):
        """
        happy path. Mocks db_connect_info and single_query.
        """
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
        #calling the task function
        task(records, *backoff_args)

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
        for record in records:
            key_path = record["s3"]["object"]["key"]

        mock_single_query.assert_called_once_with(
            sql, mock_get_db_connect_info.return_value, (key_path, OrcaStatus.PENDING.value)
        )
# -----------------------------------------------------------------------------------------------------

    @patch.dict(
    os.environ,
    {
        "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
        "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
        "MAX_RETRIES": "2",
        "RETRY_SLEEP_SECS": "2",
        "RETRY_BACKOFF": "2",
    },
    clear=True,
    )
    
    def test_event_var_None_empty(self):
        """
        Validates that an error is thrown if an expected environment variable is not
        set.
        """
        env_names = [
            "DB_QUEUE_URL",
            "RECOVERY_QUEUE_URL",
            "MAX_RETRIES",
            "RETRY_SLEEP_SECS",
            "RETRY_BACKOFF"
        ]
        env_bad_values = [None, ""]

        for name in env_names:
            good_value = os.getenv(name)
            for bad_value in env_bad_values:
                with self.subTest(
                    name=name, bad_value=bad_value, good_value=good_value
                ):
                    # Set the variable to the bad value and create the message
                    if bad_value is None:
                        del os.environ[name]
                    else:
                        os.environ[name] = bad_value
                    # Run the test
                    self.assertRaises(Exception, handler, self.event, context=None)
                    # Reset the value
                    os.environ[name] = good_value

# -----------------------------------------------------------------------------------------------------
    @patch.dict(
        os.environ,
        {
            "DB_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            "RECOVERY_QUEUE_URL": "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
            "MAX_RETRIES": "non-integer",
            "RETRY_SLEEP_SECS": "non-integer",
            "RETRY_BACKOFF": "non-integer",
        },
        clear=True,
    )
    def test_event_non_int(self):
        """
        raises ValueError when MAX_RETRIES, RETRY_SLEEP_SECS, RETRY_BACKOFF is non-integer.
        """
        env_names = [
            "DB_QUEUE_URL",
            "RECOVERY_QUEUE_URL",
            "MAX_RETRIES",
            "RETRY_SLEEP_SECS",
            "RETRY_BACKOFF"
        ]

        for name in env_names:
            value = os.getenv(name)
            with self.subTest(
                name=name, value=value
            ):
                if name in ["MAX_RETRIES", "RETRY_SLEEP_SECS", "RETRY_BACKOFF"]:
                    self.assertRaises(ValueError, handler, self.event, context=None)

    # --------------------------------------exponential delay test---------------------------------
    def test_exponential_delay(self):
        """
        tests delay function. Raises TypeError when args are non-integer
        """

        base_delay = "non-integer"
        exponential_backoff = "non-integer"

        self.assertRaises(TypeError, exponential_delay, base_delay, exponential_backoff)