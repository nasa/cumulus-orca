"""
Name: test_post_copy_request_to_queue.py
Description: unit tests for post_copy_request_to_queue.py

"""
import random
import uuid
from unittest import TestCase
import os
from unittest.mock import patch, MagicMock, Mock
import boto3
from moto import mock_sqs

import post_copy_request_to_queue
from orca_shared.recovery import shared_recovery
from post_copy_request_to_queue import handler, task, exponential_delay


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
        post_copy_request_to_queue.exponential_delay = Mock()
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
            "DATABASE_USER": "orcauser",
        },
        clear=True,
    )
    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.shared_recovery.post_entry_to_queue")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.get_metadata_sql")
    def test_task_happy_path(
        self,
        mock_get_metadata_sql: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_post_entry_to_queue: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        happy path. Mocks db_connect_info,single_query,
        post_entry_to_queue and update_status_for_file.
        """
        multipart_chunksize_mb = random.randint(1, 10000)
        mock_execute = Mock(
            return_value=[("1", "3", "f1.doc", "s3://restore", multipart_chunksize_mb)]
        )
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock()
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine

        record = self.event["Records"][0]
        new_data = {
            "job_id": "1",
            "granule_id": "3",
            "filename": "f1.doc",
            # todo: Value incorrect here and elsewhere. As written, must match mock_execute's return value.
            "restore_destination": "s3://restore",
            "multipart_chunksize_mb": multipart_chunksize_mb,
            "target_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "source_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "source_bucket": "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            2,
            2,
            2,
        ]
        # calling the task function
        task(record, *backoff_args)
        key_path = record["s3"]["object"]["key"]

        mock_get_user_connection.assert_called_once_with(
            mock_get_configuration.return_value
        )
        mock_execute.assert_called_once_with(mock_get_metadata_sql.return_value)
        mock_update_status_for_file.assert_called_once_with(
            "1",
            "3",
            "f1.doc",
            shared_recovery.OrcaStatus.STAGED,
            None,
            self.db_queue_url,
        )
        mock_post_entry_to_queue.assert_called_with(
            new_data,
            shared_recovery.RequestMethod.NEW_JOB,
            self.recovery_queue_url,
        )
        mock_exit.assert_called_once()

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
            "RETRY_BACKOFF",
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
    def test_event_non_int(self):
        """
        raises ValueError when MAX_RETRIES, RETRY_SLEEP_SECS, RETRY_BACKOFF is non-integer.
        """
        env_names = ["MAX_RETRIES", "RETRY_SLEEP_SECS", "RETRY_BACKOFF"]
        env_bad_values = ["non-int"]
        for name in env_names:
            good_value = os.getenv(name)
            for bad_value in env_bad_values:
                with self.subTest(
                    name=name, bad_value=bad_value, good_value=good_value
                ):
                    os.environ[name] = bad_value
                    # run the test
                    with self.assertRaises(ValueError) as ve:
                        message = f"{name} must be set to an integer."
                        handler(self.event, context=None)
                        self.assertEqual(ve.message, message)

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.shared_recovery.post_entry_to_queue")
    @patch("post_copy_request_to_queue.LOGGER")
    def test_task_post_entry_to_queue_exception(
        self,
        mock_LOGGER: MagicMock,
        mock_post_entry_to_queue: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        mocks post_entry_to_queue to raise an exception.
        """
        multipart_chunksize_mb = None
        mock_execute = Mock(return_value=[("1", "3", "f1.doc", "s3://restore", None)])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock()
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine
        mock_post_entry_to_queue.side_effect = Exception

        record = self.event["Records"][0]
        new_data = {
            "job_id": "1",
            "granule_id": "3",
            "filename": "f1.doc",
            "restore_destination": "s3://restore",
            "multipart_chunksize_mb": multipart_chunksize_mb,
            "source_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "target_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "source_bucket": "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            2,
            2,
            2,
        ]
        # calling the task function
        message = "Error sending message to recovery_queue_url for {new_data}"
        with self.assertRaises(Exception) as ex:
            task(record, *backoff_args)
            # Check the message from the exception
        self.assertEqual(str.format(message, new_data=new_data), ex.exception.args[0])
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(new_data))

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.LOGGER")
    def test_task_update_status_for_file_exception(
        self,
        mock_LOGGER: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        mocks update_status_for_file to raise an exception.
        """
        multipart_chunksize_mb = random.randint(1, 10000)
        mock_execute = Mock(
            return_value=[("1", "3", "f1.doc", "s3://restore", multipart_chunksize_mb)]
        )
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock()
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine
        # set the mock_update_status_for_file to Exception
        mock_update_status_for_file.side_effect = Exception

        record = self.event["Records"][0]
        new_data = {
            "job_id": "1",
            "granule_id": "3",
            "filename": "f1.doc",
            "restore_destination": "s3://restore",
            "multipart_chunksize_mb": multipart_chunksize_mb,
            "source_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "target_key": "b21b84d653bb07b05b1e6b33684dc11b",
            "source_bucket": "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            2,
            2,
            2,
        ]
        # calling the task function
        # calling the task function
        message = "Error sending message to db_queue_url for {record}"
        with self.assertRaises(Exception) as ex:
            task(record, *backoff_args)
        # Check the message from the exception
        self.assertEqual(str.format(message, record=new_data), ex.exception.args[0])
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(new_data))

    def test_exponential_delay(self):
        """
        tests delay function. Raises Exception when args are non-integer
        """
        base_delay_values = [2, "non-integer"]
        exponential_backoff_values = ["non-integer", 2]

        for i in range(2):
            base_delay = base_delay_values[i]
            exponential_backoff = exponential_backoff_values[i]
            self.assertRaises(
                ValueError, exponential_delay, base_delay, exponential_backoff
            )

        base_delay = 2
        exponential_backoff = 2
        self.assertEqual(
            exponential_delay(base_delay, exponential_backoff),
            base_delay * exponential_backoff,
        )

    def test_get_metadata_sql_happy_path(self):
        key_path = uuid.uuid4().__str__()
        result = post_copy_request_to_queue.get_metadata_sql(key_path)
        self.assertEqual(
            f"""
            SELECT
                job_id, granule_id, filename, restore_destination, multipart_chunksize_mb
            FROM
                recovery_file
            WHERE
                key_path = '{key_path}'
            AND
                status_id = {shared_recovery.OrcaStatus.PENDING.value}
        """,
            result.text,
        )
