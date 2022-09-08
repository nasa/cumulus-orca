"""
Name: test_perform_orca_reconcile.py
Description:  Unit tests for test_perform_orca_reconcile.py.
"""
import copy
import os
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from orca_shared.reconciliation import OrcaStatus

import perform_orca_reconcile


class TestPerformOrcaReconcile(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPerformOrcaReconcile.
    """

    @patch("perform_orca_reconcile.remove_job_from_queue")
    @patch("perform_orca_reconcile.update_job")
    @patch("perform_orca_reconcile.generate_reports")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self,
        mock_get_user_connection: MagicMock,
        mock_generate_reports: MagicMock,
        mock_update_job: MagicMock,
        mock_remove_job_from_queue: MagicMock,
    ):
        """
        Happy path that triggers the various DB tasks.
        """
        db_connect_info = Mock()
        mock_orca_archive_location = Mock()
        mock_job_id = Mock()
        internal_report_queue_url = Mock()
        message_receipt_handle = Mock()

        result = perform_orca_reconcile.task(
            mock_job_id,
            mock_orca_archive_location,
            internal_report_queue_url,
            message_receipt_handle,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_generate_reports.assert_called_once_with(
            mock_job_id,
            mock_orca_archive_location,
            mock_get_user_connection.return_value,
        )
        mock_update_job.assert_has_calls(
            [
                call(
                    mock_job_id,
                    OrcaStatus.GENERATING_REPORTS,
                    None,
                    mock_get_user_connection.return_value,
                ),
                call(
                    mock_job_id,
                    OrcaStatus.SUCCESS,
                    None,
                    mock_get_user_connection.return_value,
                ),
            ]
        )
        mock_remove_job_from_queue.assert_called_once_with(
            internal_report_queue_url, message_receipt_handle
        )

        self.assertEqual(
            {
                perform_orca_reconcile.OUTPUT_JOB_ID_KEY: mock_job_id,
            },
            result,
        )

    @patch("perform_orca_reconcile.remove_job_from_queue")
    @patch("perform_orca_reconcile.LOGGER")
    @patch("perform_orca_reconcile.update_job")
    @patch("perform_orca_reconcile.generate_reports")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_error_posted_as_status_update(
        self,
        mock_get_user_connection: MagicMock,
        mock_generate_reports: MagicMock,
        mock_update_job: MagicMock,
        mock_logger: MagicMock,
        mock_remove_job_from_queue: MagicMock,
    ):
        """
        Errors should be written to status entries.
        """
        expected_exception = Exception(uuid.uuid4().__str__())
        mock_generate_reports.side_effect = expected_exception

        db_connect_info = Mock()
        mock_orca_archive_location = Mock()
        mock_job_id = Mock()
        internal_report_queue_url = Mock()
        message_receipt_handle = Mock()

        with self.assertRaises(Exception) as cm:
            perform_orca_reconcile.task(
                mock_job_id,
                mock_orca_archive_location,
                internal_report_queue_url,
                message_receipt_handle,
                db_connect_info,
            )
        self.assertEqual(expected_exception, cm.exception)

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_generate_reports.assert_called_once_with(
            mock_job_id,
            mock_orca_archive_location,
            mock_get_user_connection.return_value,
        )
        mock_update_job.assert_has_calls(
            [
                call(
                    mock_job_id,
                    OrcaStatus.GENERATING_REPORTS,
                    None,
                    mock_get_user_connection.return_value,
                ),
                call(
                    mock_job_id,
                    OrcaStatus.ERROR,
                    str(expected_exception),
                    mock_get_user_connection.return_value,
                ),
            ]
        )
        mock_remove_job_from_queue.assert_not_called()
        mock_logger.error.assert_called_once_with(
            f"Encountered a fatal error: {expected_exception}"
        )

    @patch("perform_orca_reconcile.generate_mismatch_reports_sql")
    @patch("perform_orca_reconcile.generate_orphan_reports_sql")
    @patch("perform_orca_reconcile.generate_phantom_reports_sql")
    def test_generate_reports_happy_path(
        self,
        mock_generate_phantom_reports_sql: MagicMock,
        mock_generate_orphan_reports_sql: MagicMock,
        mock_generate_mismatch_reports_sql: MagicMock,
    ):
        """
        Happy path for generating reports in postgres
        """
        mock_job_id = Mock()
        mock_orca_archive_location = Mock()
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        perform_orca_reconcile.generate_reports(
            mock_job_id, mock_orca_archive_location, mock_engine
        )

        mock_enter.__enter__.assert_called_once_with()

        mock_generate_phantom_reports_sql.assert_called_once_with()
        mock_execute.assert_has_calls(
            [
                call(
                    mock_generate_phantom_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
                call(
                    mock_generate_orphan_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
                call(
                    mock_generate_mismatch_reports_sql.return_value,
                    [
                        {
                            "job_id": mock_job_id,
                            "orca_archive_location": mock_orca_archive_location,
                        }
                    ],
                ),
            ]
        )
        self.assertEqual(3, mock_execute.call_count)

        mock_generate_orphan_reports_sql.assert_called_once_with()

        mock_generate_mismatch_reports_sql.assert_called_once_with()

        mock_exit.assert_called_once_with(None, None, None)

    @patch("perform_orca_reconcile.LOGGER")
    @patch("perform_orca_reconcile.generate_mismatch_reports_sql")
    @patch("perform_orca_reconcile.generate_orphan_reports_sql")
    @patch("perform_orca_reconcile.generate_phantom_reports_sql")
    def test_generate_reports_error_logged_and_raised(
        self,
        mock_generate_phantom_reports_sql: MagicMock,
        mock_generate_orphan_reports_sql: MagicMock,
        mock_generate_mismatch_reports_sql: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())
        mock_job_id = Mock()
        mock_orca_archive_location = Mock()
        mock_execute = Mock(side_effect=expected_exception)
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        with self.assertRaises(Exception) as cm:
            perform_orca_reconcile.generate_reports(
                mock_job_id, mock_orca_archive_location, mock_engine
            )
        self.assertEqual(expected_exception, cm.exception)
        mock_enter.__enter__.assert_called_once_with()

        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while generating reports for job {mock_job_id}: {expected_exception}"
        )

    @patch("boto3.client")
    def test_remove_job_from_queue_happy_path(self, mock_client: MagicMock):
        """
        Happy path for removing the completed item from the queue.
        """
        internal_report_queue_url = Mock()
        message_receipt_handle = Mock()

        perform_orca_reconcile.remove_job_from_queue(
            internal_report_queue_url, message_receipt_handle
        )

        mock_client.assert_called_once_with("sqs")
        mock_client.return_value.delete_message.assert_called_once_with(
            QueueUrl=internal_report_queue_url,
            ReceiptHandle=message_receipt_handle,
        )

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("perform_orca_reconcile.LOGGER")
    @patch("perform_orca_reconcile.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_task: MagicMock,
        mock_LOGGER: MagicMock,
        mock_get_configuration: MagicMock,
    ):
        """
        Happy path for handler assembling information to call Task.
        """
        job_id = random.randint(0, 1000)  # nosec
        orca_archive_location = uuid.uuid4().__str__()
        message_receipt_handle = uuid.uuid4().__str__()

        expected_result = {
            perform_orca_reconcile.OUTPUT_JOB_ID_KEY: random.randint(0, 1000),  # nosec
        }
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        event = {
            perform_orca_reconcile.INPUT_EVENT_KEY: {
                perform_orca_reconcile.EVENT_JOB_ID_KEY: job_id,
                perform_orca_reconcile.EVENT_ORCA_ARCHIVE_LOCATION_KEY: orca_archive_location,
                perform_orca_reconcile.EVENT_MESSAGE_RECEIPT_HANDLE_KEY: message_receipt_handle,
            }
        }

        internal_report_queue_url = uuid.uuid4().__str__()
        with patch.dict(
            os.environ,
            {
                perform_orca_reconcile.OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY:
                    internal_report_queue_url
            },
        ):
            result = perform_orca_reconcile.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_configuration.assert_called_once_with(
            os.environ["DB_CONNECT_INFO_SECRET_ARN"]
        )
        mock_task.assert_called_once_with(
            job_id,
            orca_archive_location,
            internal_report_queue_url,
            message_receipt_handle,
            mock_get_configuration.return_value,
        )
        self.assertEqual(expected_result, result)

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("perform_orca_reconcile.LOGGER")
    @patch("perform_orca_reconcile.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_rejects_bad_input(
        self,
        mock_task: MagicMock,
        mock_LOGGER: MagicMock,
        mock_get_configuration: MagicMock,
    ):
        """
        Violating input.json schema should raise an error.
        """
        job_id = random.randint(0, 1000)  # nosec
        message_receipt_handle = uuid.uuid4().__str__()

        expected_result = {
            perform_orca_reconcile.OUTPUT_JOB_ID_KEY: random.randint(0, 1000),  # nosec
        }
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        event = {
            perform_orca_reconcile.INPUT_EVENT_KEY: {
                perform_orca_reconcile.EVENT_JOB_ID_KEY: job_id,
                perform_orca_reconcile.EVENT_MESSAGE_RECEIPT_HANDLE_KEY: message_receipt_handle,
            }
        }

        internal_report_queue_url = uuid.uuid4().__str__()
        with patch.dict(
            os.environ,
            {
                perform_orca_reconcile.OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY:
                    internal_report_queue_url
            },
        ):
            with self.assertRaises(Exception) as cm:
                perform_orca_reconcile.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_task.assert_not_called()
        self.assertEqual(
            f"data.event must contain ['{perform_orca_reconcile.EVENT_JOB_ID_KEY}', "
            f"'{perform_orca_reconcile.EVENT_ORCA_ARCHIVE_LOCATION_KEY}', "
            f"'{perform_orca_reconcile.EVENT_MESSAGE_RECEIPT_HANDLE_KEY}'] properties",
            str(cm.exception),
        )

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("perform_orca_reconcile.LOGGER")
    @patch("perform_orca_reconcile.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_rejects_bad_output(
        self,
        mock_task: MagicMock,
        mock_LOGGER: MagicMock,
        mock_get_configuration: MagicMock,
    ):
        """
        Violating output.json schema should raise an error.
        """
        job_id = random.randint(0, 1000)  # nosec
        orca_archive_location = uuid.uuid4().__str__()
        message_receipt_handle = uuid.uuid4().__str__()

        expected_result = {
            perform_orca_reconcile.OUTPUT_JOB_ID_KEY: str(
                random.randint(0, 1000)  # nosec
            ),
        }
        mock_task.return_value = copy.deepcopy(expected_result)

        mock_context = Mock()
        event = {
            perform_orca_reconcile.INPUT_EVENT_KEY: {
                perform_orca_reconcile.EVENT_JOB_ID_KEY: job_id,
                perform_orca_reconcile.EVENT_ORCA_ARCHIVE_LOCATION_KEY: orca_archive_location,
                perform_orca_reconcile.EVENT_MESSAGE_RECEIPT_HANDLE_KEY: message_receipt_handle,
            }
        }

        internal_report_queue_url = uuid.uuid4().__str__()
        with patch.dict(
            os.environ,
            {
                perform_orca_reconcile.OS_ENVIRON_INTERNAL_REPORT_QUEUE_URL_KEY:
                    internal_report_queue_url
            },
        ):
            with self.assertRaises(Exception) as cm:
                perform_orca_reconcile.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_configuration.assert_called_once_with(
            os.environ["DB_CONNECT_INFO_SECRET_ARN"]
        )
        mock_task.assert_called_once_with(
            job_id,
            orca_archive_location,
            internal_report_queue_url,
            message_receipt_handle,
            mock_get_configuration.return_value,
        )
        self.assertEqual(
            f"data.{perform_orca_reconcile.EVENT_JOB_ID_KEY} must be integer",
            str(cm.exception),
        )

    # copied from shared_db.py
    @patch("time.sleep")
    def test_retry_operational_error_happy_path(self, mock_sleep: MagicMock):
        expected_result = Mock()

        @perform_orca_reconcile.retry_error(3)
        def dummy_call():
            return expected_result

        result = dummy_call()

        self.assertEqual(expected_result, result)
        mock_sleep.assert_not_called()

    # copied from shared_db.py
    @patch("time.sleep")
    def test_retry_error_error_retries_and_raises(self, mock_sleep: MagicMock):
        """
        If the error raised is an OperationalError, it should retry up to the maximum allowed.
        """
        max_retries = 16
        # I have not tested that the below is a perfect recreation of an AdminShutdown error.
        expected_error = Exception()

        @perform_orca_reconcile.retry_error(max_retries)
        def dummy_call():
            raise expected_error

        try:
            dummy_call()
        except Exception as caught_error:
            self.assertEqual(expected_error, caught_error)
            self.assertEqual(max_retries, mock_sleep.call_count)
            return
        self.fail("Error not raised.")
