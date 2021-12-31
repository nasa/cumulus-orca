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

    # todo: Rewrite tests for individual functions, rather than full run-throughs.

    # Create the mock instance for unit tests
    mock_sqs = mock_sqs()

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        # todo: Once tests are limited in scope to one-function-per-test, only set up these mocks when needed.
        post_copy_request_to_queue.exponential_delay = Mock()
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.db_queue = self.test_sqs.create_queue(QueueName=uuid.uuid4().__str__())
        self.recovery_queue = self.test_sqs.create_queue(
            QueueName=uuid.uuid4().__str__()
        )
        self.db_queue_url = self.db_queue.url
        self.recovery_queue_url = self.recovery_queue.url
        # todo: Delete hardcoded values.
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

    @patch("post_copy_request_to_queue.task")
    def test_handler_happy_path(self,
                                mock_task: MagicMock
                                ):
        record = {uuid.uuid4().__str__(): uuid.uuid4().__str__()}
        event = {"Records": [record]}

        db_queue_url = uuid.uuid4().__str__()
        recovery_queue_url = uuid.uuid4().__str__()
        max_retries = random.randint(0, 100)
        retry_sleep_secs = random.randint(0, 100)
        retry_backoff = random.randint(0, 100)

        with patch.dict(
                os.environ,
                {
                    post_copy_request_to_queue.OS_ENVIRON_DB_QUEUE_URL_KEY: db_queue_url,
                    post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: recovery_queue_url,
                    post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: str(max_retries),
                    post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: str(retry_sleep_secs),
                    post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: str(retry_backoff),
                },
                clear=True,
        ):
            handler(event, None)
        mock_task.assert_called_once_with(record, db_queue_url, recovery_queue_url, max_retries, retry_sleep_secs,
                                          retry_backoff)

    @patch("post_copy_request_to_queue.task")
    def test_handler_multiple_records_raises_error(self,
                                                   mock_task: MagicMock,
                                                   ):
        """
        Code can currently only handle one record per invocation.
        """
        event = {"Records": [Mock(), Mock()]}

        with self.assertRaises(ValueError) as cm:
            with patch.dict(
                    os.environ,
                    {
                        post_copy_request_to_queue.OS_ENVIRON_DB_QUEUE_URL_KEY: uuid.uuid4().__str__(),
                        post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: uuid.uuid4().__str__(),
                        post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: str(random.randint(0, 100)),
                        post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: str(random.randint(0, 100)),
                        post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: str(random.randint(0, 100)),
                    },
                    clear=True,
            ):
                handler(event, None)
        self.assertEqual("Must be passed a single record. Was 2", str(cm.exception))
        mock_task.assert_not_called()

    @patch.dict(
        os.environ,
        {
            post_copy_request_to_queue.OS_ENVIRON_DB_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
            post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: "1",
            post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: "2",
            post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: "3",
        },
        clear=True,
    )
    def test_handler_event_var_None_empty(self):
        """
        Validates that an error is thrown if an expected environment variable is not
        set.
        """
        env_names = [
            post_copy_request_to_queue.OS_ENVIRON_DB_QUEUE_URL_KEY,
            post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY,
            post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY,
            post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY,
            post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY,
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
            post_copy_request_to_queue.OS_ENVIRON_DB_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            # todo: This value doesn't seem to need to match
            post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
            # todo: This value doesn't seem to need to match
            post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: "1",
            post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: "2",
            post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: "3",
        },
        clear=True,
    )
    def test_handler_event_non_int(self):
        """
        raises ValueError when MAX_RETRIES, RETRY_SLEEP_SECS, RETRY_BACKOFF is non-integer.
        """
        env_names = [
            post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY,
            post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY,
            post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY,
        ]
        env_bad_values = ["non-int"]
        for name in env_names:
            good_value = os.getenv(name)
            for bad_value in env_bad_values:
                with self.subTest(
                        name=name, bad_value=bad_value, good_value=good_value
                ):
                    with (
                            patch.dict(
                                os.environ,
                                {
                                    name: bad_value,
                                },
                            )
                    ):
                        # run the test
                        with self.assertRaises(ValueError) as cm:
                            handler(self.event, context=None)
                        message = f"{name} must be set to an integer."
                        self.assertEqual(str(cm.exception), message)

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
            mock_get_configuration: MagicMock,  # todo: Indicates that test goes beyond `task`
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
            post_copy_request_to_queue.JOB_ID_KEY: "1",  # todo: randomize values here and elsewhere
            post_copy_request_to_queue.GRANULE_ID_KEY: "3",
            post_copy_request_to_queue.FILENAME_KEY: "f1.doc",
            post_copy_request_to_queue.RESTORE_DESTINATION_KEY: "s3://restore",
            post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: multipart_chunksize_mb,
            post_copy_request_to_queue.TARGET_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.SOURCE_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.SOURCE_BUCKET_KEY: "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            1,
            2,
            3,
        ]
        # calling the task function
        task(record, *backoff_args)

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
            mock_get_configuration: MagicMock,  # todo: Indicates that test goes beyond `task`
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
            post_copy_request_to_queue.JOB_ID_KEY: "1",
            post_copy_request_to_queue.GRANULE_ID_KEY: "3",
            post_copy_request_to_queue.FILENAME_KEY: "f1.doc",
            post_copy_request_to_queue.RESTORE_DESTINATION_KEY: "s3://restore",
            post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: multipart_chunksize_mb,
            post_copy_request_to_queue.SOURCE_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.TARGET_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.SOURCE_BUCKET_KEY: "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            1,
            2,
            3,
        ]
        # calling the task function
        message = "Error sending message to recovery_queue_url for {new_data}"
        with self.assertRaises(Exception) as cm:
            task(record, *backoff_args)
            # Check the message from the exception
        self.assertEqual(str.format(message, new_data=new_data), cm.exception.args[0])
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(new_data))
        mock_update_status_for_file.assert_called_once_with(
            "1",
            "3",
            "f1.doc",
            shared_recovery.OrcaStatus.STAGED,
            None,
            self.db_queue_url,
        )

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.LOGGER")
    def test_task_update_status_for_file_exception(
            self,
            mock_LOGGER: MagicMock,
            mock_update_status_for_file: MagicMock,
            mock_get_configuration: MagicMock,  # todo: Indicates that test goes beyond `task`
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
            post_copy_request_to_queue.JOB_ID_KEY: "1",
            post_copy_request_to_queue.GRANULE_ID_KEY: "3",
            post_copy_request_to_queue.FILENAME_KEY: "f1.doc",
            post_copy_request_to_queue.RESTORE_DESTINATION_KEY: "s3://restore",
            post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: multipart_chunksize_mb,
            post_copy_request_to_queue.SOURCE_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.TARGET_KEY_KEY: "b21b84d653bb07b05b1e6b33684dc11b",
            post_copy_request_to_queue.SOURCE_BUCKET_KEY: "lambda-artifacts-deafc19498e3f2df",
        }
        backoff_args = [
            self.db_queue_url,
            self.recovery_queue_url,
            1,
            2,
            3,
        ]
        # calling the task function
        # calling the task function
        message = "Error sending message to db_queue_url for {record}"
        with self.assertRaises(Exception) as cm:
            task(record, *backoff_args)
        # Check the message from the exception
        self.assertEqual(str.format(message, record=new_data), cm.exception.args[0])
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(new_data))

    @patch("time.sleep")
    def test_exponential_delay_happy_path(self, mock_sleep: MagicMock):
        base_delay = random.randint(0, 10)
        exponential_backoff = random.randint(0, 10)
        random_addition = random.randint(0, 500)

        with patch("random.randint") as mock_randint:
            mock_randint.return_value = random_addition
            result = exponential_delay(base_delay, exponential_backoff)
        self.assertEqual(
            result,
            base_delay * exponential_backoff,
        )
        mock_randint.assert_called_once_with(0, 1000)
        mock_sleep.assert_called_once_with(base_delay + random_addition / 1000.0)

    @patch("time.sleep")
    def test_exponential_delay_non_integer_raises_error(self, mock_sleep: MagicMock):
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
