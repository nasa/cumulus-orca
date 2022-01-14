"""
Name: test_post_copy_request_to_queue.py
Description: unit tests for post_copy_request_to_queue.py
"""
import copy
import random
import time
import uuid
from unittest import TestCase, mock
import os
from unittest.mock import patch, MagicMock, Mock, call

# noinspection PyPackageRequirements
import boto3

# noinspection PyPackageRequirements
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
        time.sleep = Mock()

    def tearDown(self):
        """
        Perform tear down actions
        """
        if self.mock_sqs.mocks_active:
            self.mock_sqs.stop()

    def setUpQueues(self):
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.status_update_queue = self.test_sqs.create_queue(QueueName=uuid.uuid4().__str__())
        self.recovery_queue = self.test_sqs.create_queue(
            QueueName=uuid.uuid4().__str__()
        )
        self.status_update_queue_url = self.status_update_queue.url
        self.recovery_queue_url = self.recovery_queue.url

    @patch("post_copy_request_to_queue.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()
        event = {
            "Records": [
                {"s3": {"object": {"key": key_path}, "bucket": {"name": bucket_name}}}
            ]
        }

        db_queue_url = uuid.uuid4().__str__()
        recovery_queue_url = uuid.uuid4().__str__()
        max_retries = random.randint(1, 100)
        retry_sleep_secs = random.randint(0, 100)
        retry_backoff = random.randint(0, 100)

        with patch.dict(
            os.environ,
            {
                post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY: db_queue_url,
                post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: recovery_queue_url,
                post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: str(max_retries),
                post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: str(
                    retry_sleep_secs
                ),
                post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: str(
                    retry_backoff
                ),
            },
            clear=True,
        ):
            handler(event, None)
        mock_task.assert_called_once_with(
            key_path,
            bucket_name,
            db_queue_url,
            recovery_queue_url,
            max_retries,
            retry_sleep_secs,
            retry_backoff,
        )

    @patch("post_copy_request_to_queue.task")
    def test_handler_multiple_records_raises_error(
        self,
        mock_task: MagicMock,
    ):
        """
        Code can currently only handle one record per invocation.
        """
        event = {
            "Records": [
                {
                    "s3": {
                        "object": {"key": uuid.uuid4().__str__()},
                        "bucket": {"name": uuid.uuid4().__str__()},
                    }
                },
                {
                    "s3": {
                        "object": {"key": uuid.uuid4().__str__()},
                        "bucket": {"name": uuid.uuid4().__str__()},
                    }
                },
            ]
        }

        with self.assertRaises(ValueError) as cm:
            with patch.dict(
                os.environ,
                {
                    post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY: uuid.uuid4().__str__(),
                    post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: uuid.uuid4().__str__(),
                    post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: str(
                        random.randint(0, 100)
                    ),
                    post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: str(
                        random.randint(0, 100)
                    ),
                    post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: str(
                        random.randint(0, 100)
                    ),
                },
                clear=True,
            ):
                handler(event, None)
        self.assertEqual("Must be passed a single record. Was 2", str(cm.exception))
        mock_task.assert_not_called()

    @patch.dict(
        os.environ,
        {
            post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
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
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()
        event = {
            "Records": [
                {"s3": {"object": {"key": key_path}, "bucket": {"name": bucket_name}}}
            ]
        }

        env_names = [
            post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY,
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
                    self.assertRaises(
                        Exception,
                        handler,
                        event,
                        context=None,
                    )
                    # Reset the value
                    os.environ[name] = good_value

    @patch.dict(
        os.environ,
        {
            post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/dbqueue",
            post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: "https://us-west-2.queue.amazonaws.com/123456789012/recoveryqueue",
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
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()
        event = {
            "Records": [
                {"s3": {"object": {"key": key_path}, "bucket": {"name": bucket_name}}}
            ]
        }

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
                            handler(
                                event,
                                context=None,
                            )
                        message = f"{name} must be set to an integer."
                        self.assertEqual(str(cm.exception), message)

    @patch("post_copy_request_to_queue.task")
    def test_handler_missing_record_properties_causes_error(self, mock_task: MagicMock):
        bad_events = [
            {
                "event": {
                    "Records": [
                        {
                            "s3": {
                                "object": {},
                                "bucket": {"name": uuid.uuid4().__str__()},
                            }
                        }
                    ]
                },
                "key": "key",
            },
            {
                "event": {
                    "Records": [
                        {
                            "s3": {
                                "object": {"key": uuid.uuid4().__str__()},
                                "bucket": {},
                            }
                        }
                    ]
                },
                "key": "name",
            },
        ]

        db_queue_url = uuid.uuid4().__str__()
        recovery_queue_url = uuid.uuid4().__str__()
        max_retries = random.randint(1, 100)
        retry_sleep_secs = random.randint(0, 100)
        retry_backoff = random.randint(0, 100)

        with patch.dict(
            os.environ,
            {
                post_copy_request_to_queue.OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY: db_queue_url,
                post_copy_request_to_queue.OS_ENVIRON_RECOVERY_QUEUE_URL_KEY: recovery_queue_url,
                post_copy_request_to_queue.OS_ENVIRON_MAX_RETRIES_KEY: str(max_retries),
                post_copy_request_to_queue.OS_ENVIRON_RETRY_SLEEP_SECS_KEY: str(
                    retry_sleep_secs
                ),
                post_copy_request_to_queue.OS_ENVIRON_RETRY_BACKOFF_KEY: str(
                    retry_backoff
                ),
            },
            clear=True,
        ):
            for bad_event in bad_events:
                with self.subTest(bad_event=bad_event):
                    with self.assertRaises(KeyError) as cm:
                        handler(bad_event["event"], None)
                    self.assertEqual(f"'{bad_event['key']}'", str(cm.exception))
                    mock_task.assert_not_called()

    @patch("post_copy_request_to_queue.query_db")
    @patch("post_copy_request_to_queue.shared_recovery.post_entry_to_standard_queue")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    def test_task_happy_path(
        self,
        mock_update_status_for_file: MagicMock,
        mock_post_entry_to_standard_queue: MagicMock,
        mock_query_db: MagicMock,
    ):
        """
        happy path. Mocks db_connect_info,single_query,
        post_entry_to_queue and update_status_for_file.
        """
        self.setUpQueues()
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        restore_destination = uuid.uuid4().__str__()
        multipart_chunksize_mb = random.randint(1, 10000)
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        row =           {
                post_copy_request_to_queue.JOB_ID_KEY: job_id,
                post_copy_request_to_queue.GRANULE_ID_KEY: granule_id,
                post_copy_request_to_queue.FILENAME_KEY: filename,
                post_copy_request_to_queue.RESTORE_DESTINATION_KEY: restore_destination,
                post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: str(
                    multipart_chunksize_mb
                ),
                post_copy_request_to_queue.SOURCE_KEY_KEY: key_path,
                post_copy_request_to_queue.TARGET_KEY_KEY: key_path,
                post_copy_request_to_queue.SOURCE_BUCKET_KEY: bucket_name,
            }
        mock_query_db.return_value = [row]

        environment_args = [
            self.status_update_queue_url,
            self.recovery_queue_url,
            1,
            2,
            3,
        ]

        # calling the task function
        task(key_path, bucket_name, *environment_args)

        mock_query_db.assert_called_once_with(key_path, bucket_name)
        mock_update_status_for_file.assert_called_once_with(
            job_id,
            granule_id,
            filename,
            shared_recovery.OrcaStatus.STAGED,
            None,
            self.status_update_queue_url,
        )
        mock_post_entry_to_standard_queue.assert_called_once_with(

            row,
            self.recovery_queue_url,
        )

    @patch("post_copy_request_to_queue.exponential_delay")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.shared_recovery.post_entry_to_standard_queue")
    @patch("post_copy_request_to_queue.query_db")
    @patch("post_copy_request_to_queue.LOGGER")
    def test_task_post_entry_to_queue_exception(
        self,
        mock_LOGGER: MagicMock,
        mock_query_db: MagicMock,
        mock_post_entry_to_standard_queue: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_exponential_delay: MagicMock,
    ):
        """
        mocks post_entry_to_standard_queue to raise an exception.
        """
        self.setUpQueues()
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        restore_destination = uuid.uuid4().__str__()
        multipart_chunksize_mb = random.randint(1, 10000)
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        mock_post_entry_to_standard_queue.side_effect = Exception

        row = {
            post_copy_request_to_queue.JOB_ID_KEY: job_id,
            post_copy_request_to_queue.GRANULE_ID_KEY: granule_id,
            post_copy_request_to_queue.FILENAME_KEY: filename,
            post_copy_request_to_queue.RESTORE_DESTINATION_KEY: restore_destination,
            post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: str(
                multipart_chunksize_mb
            ),
            post_copy_request_to_queue.SOURCE_KEY_KEY: key_path,
            post_copy_request_to_queue.TARGET_KEY_KEY: key_path,
            post_copy_request_to_queue.SOURCE_BUCKET_KEY: bucket_name,
        }
        mock_query_db.return_value = [copy.deepcopy(row)]
        max_retries = random.randint(2, 100)
        environment_args = [
            self.status_update_queue_url,
            self.recovery_queue_url,
            max_retries,
            2,
            3,
        ]
        # calling the task function
        message = "Error sending message to recovery_queue_url for {new_data}"
        with self.assertRaises(Exception) as cm:
            task(key_path, bucket_name, *environment_args)
            # Check the message from the exception
        self.assertEqual(str.format(message, new_data=row), cm.exception.args[0])
        mock_query_db.assert_called_once_with(key_path, bucket_name)
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(row))
        mock_update_status_for_file.assert_called_once_with(
            job_id,
            granule_id,
            filename,
            shared_recovery.OrcaStatus.STAGED,
            None,
            self.status_update_queue_url,
        )
        mock_post_entry_to_standard_queue.assert_has_calls(
            [
                call(
                    row,
                    self.recovery_queue_url,
                )
            ]
            * (max_retries + 1)
        )
        self.assertEqual(max_retries + 1, mock_post_entry_to_standard_queue.call_count)
        self.assertEqual(
            max_retries, mock_exponential_delay.call_count
        )  # Should not sleep on final attempt.

    @patch("post_copy_request_to_queue.exponential_delay")
    @patch("post_copy_request_to_queue.shared_recovery.update_status_for_file")
    @patch("post_copy_request_to_queue.query_db")
    @patch("post_copy_request_to_queue.LOGGER")
    def test_task_update_status_for_file_exception(
        self,
        mock_LOGGER: MagicMock,
        mock_query_db: MagicMock,
        mock_update_status_for_file: MagicMock,
        mock_exponential_delay: MagicMock,
    ):
        """
        mocks update_status_for_file to raise an exception.
        """
        self.setUpQueues()
        job_id = uuid.uuid4().__str__()
        granule_id = uuid.uuid4().__str__()
        filename = uuid.uuid4().__str__()
        restore_destination = uuid.uuid4().__str__()
        multipart_chunksize_mb = random.randint(1, 10000)
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        # set the mock_update_status_for_file to Exception
        mock_update_status_for_file.side_effect = Exception

        row = {
            post_copy_request_to_queue.JOB_ID_KEY: job_id,
            post_copy_request_to_queue.GRANULE_ID_KEY: granule_id,
            post_copy_request_to_queue.FILENAME_KEY: filename,
            post_copy_request_to_queue.RESTORE_DESTINATION_KEY: restore_destination,
            post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: str(
                multipart_chunksize_mb
            ),
            post_copy_request_to_queue.SOURCE_KEY_KEY: key_path,
            post_copy_request_to_queue.TARGET_KEY_KEY: key_path,
            post_copy_request_to_queue.SOURCE_BUCKET_KEY: bucket_name,
        }
        mock_query_db.return_value = [copy.deepcopy(row)]
        max_retries = random.randint(2, 100)
        environment_args = [
            self.status_update_queue_url,
            self.recovery_queue_url,
            max_retries,
            2,
            3,
        ]
        # calling the task function
        # calling the task function
        message = "Error sending message to status_update_queue_url for {row}"
        with self.assertRaises(Exception) as cm:
            task(key_path, bucket_name, *environment_args)
        # Check the message from the exception
        self.assertEqual(str.format(message, row=row), cm.exception.args[0])
        # verify the logging captured matches the expected message
        mock_LOGGER.critical.assert_called_once_with(message, new_data=str(row))
        mock_update_status_for_file.assert_has_calls(
            [
                call(
                    job_id,
                    granule_id,
                    filename,
                    shared_recovery.OrcaStatus.STAGED,
                    None,
                    self.status_update_queue_url,
                )
            ]
            * (max_retries + 1)
        )
        self.assertEqual(max_retries + 1, mock_update_status_for_file.call_count)
        self.assertEqual(
            max_retries, mock_exponential_delay.call_count
        )  # Should not sleep on final attempt.

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

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.get_metadata_sql")
    def test_query_db_happy_path(
        self,
        mock_get_metadata_sql: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        Happy path
        """
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        job_id0 = uuid.uuid4().__str__()
        granule_id0 = uuid.uuid4().__str__()
        filename0 = uuid.uuid4().__str__()
        restore_destination0 = uuid.uuid4().__str__()
        multipart_chunksize_mb0 = random.randint(0, 1000)
        job_id1 = uuid.uuid4().__str__()
        granule_id1 = uuid.uuid4().__str__()
        filename1 = uuid.uuid4().__str__()
        restore_destination1 = uuid.uuid4().__str__()
        multipart_chunksize_mb1 = random.randint(0, 1000)

        mock_execute = Mock(
            return_value=[
                (
                    job_id0,
                    granule_id0,
                    filename0,
                    restore_destination0,
                    str(multipart_chunksize_mb0),
                ),
                (
                    job_id1,
                    granule_id1,
                    filename1,
                    restore_destination1,
                    str(multipart_chunksize_mb1),
                ),
            ]
        )
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine

        result = post_copy_request_to_queue.query_db(key_path, bucket_name)

        mock_get_configuration.assert_called_once_with()
        mock_get_user_connection.assert_called_once_with(
            mock_get_configuration.return_value
        )
        mock_get_metadata_sql.assert_called_once_with(key_path)
        mock_execute.assert_called_once_with(mock_get_metadata_sql.return_value)
        self.assertEqual(
            [
                {
                    post_copy_request_to_queue.JOB_ID_KEY: job_id0,
                    post_copy_request_to_queue.GRANULE_ID_KEY: granule_id0,
                    post_copy_request_to_queue.FILENAME_KEY: filename0,
                    post_copy_request_to_queue.RESTORE_DESTINATION_KEY: restore_destination0,
                    post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: str(
                        multipart_chunksize_mb0
                    ),
                    post_copy_request_to_queue.SOURCE_KEY_KEY: key_path,
                    post_copy_request_to_queue.TARGET_KEY_KEY: key_path,
                    post_copy_request_to_queue.SOURCE_BUCKET_KEY: bucket_name,
                },
                {
                    post_copy_request_to_queue.JOB_ID_KEY: job_id1,
                    post_copy_request_to_queue.GRANULE_ID_KEY: granule_id1,
                    post_copy_request_to_queue.FILENAME_KEY: filename1,
                    post_copy_request_to_queue.RESTORE_DESTINATION_KEY: restore_destination1,
                    post_copy_request_to_queue.MULTIPART_CHUNKSIZE_MB_KEY: str(
                        multipart_chunksize_mb1
                    ),
                    post_copy_request_to_queue.SOURCE_KEY_KEY: key_path,
                    post_copy_request_to_queue.TARGET_KEY_KEY: key_path,
                    post_copy_request_to_queue.SOURCE_BUCKET_KEY: bucket_name,
                },
            ],
            result,
        )

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.get_metadata_sql")
    def test_query_db_no_records_causes_exception(
        self,
        mock_get_metadata_sql: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If 0 records are found, should raise an exception.
        """
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        mock_execute = Mock(return_value=[])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine

        with self.assertRaises(Exception) as cm:
            post_copy_request_to_queue.query_db(key_path, bucket_name)

        self.assertEqual(
            f"Unable to retrieve {key_path} metadata. Exception 'No metadata found for {key_path}' encountered.",
            str(cm.exception),
        )
        mock_get_configuration.assert_called_once_with()
        mock_get_user_connection.assert_called_once_with(
            mock_get_configuration.return_value
        )
        mock_get_metadata_sql.assert_called_once_with(key_path)
        mock_execute.assert_called_once_with(mock_get_metadata_sql.return_value)

    @patch("post_copy_request_to_queue.shared_db.get_user_connection")
    @patch("post_copy_request_to_queue.shared_db.get_configuration")
    @patch("post_copy_request_to_queue.get_metadata_sql")
    def test_query_db_exceptions_bubble_up(
        self,
        mock_get_metadata_sql: MagicMock,
        mock_get_configuration: MagicMock,
        mock_get_user_connection: MagicMock,
    ):
        """
        If an exception occurred, an exception should be raised. Will not be the same exception.
        """
        key_path = uuid.uuid4().__str__()
        bucket_name = uuid.uuid4().__str__()

        error_string = "blah"
        mock_execute = Mock(side_effect=Exception(error_string))
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)
        mock_get_user_connection.return_value = mock_engine

        with self.assertRaises(Exception) as cm:
            post_copy_request_to_queue.query_db(key_path, bucket_name)

        self.assertEqual(
            f"Unable to retrieve {key_path} metadata. Exception '{error_string}' encountered.",
            str(cm.exception),
        )
        mock_get_configuration.assert_called_once_with()
        mock_get_user_connection.assert_called_once_with(
            mock_get_configuration.return_value
        )
        mock_get_metadata_sql.assert_called_once_with(key_path)
        mock_execute.assert_called_once_with(mock_get_metadata_sql.return_value)

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