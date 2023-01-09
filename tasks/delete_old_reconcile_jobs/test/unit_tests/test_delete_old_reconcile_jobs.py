"""
Name: test_delete_old_reconcile_jobs.py
Description:  Unit tests for test_delete_old_reconcile_jobs.py.
"""
import datetime
import os
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

import delete_old_reconcile_jobs


class TestDeleteOldReconcileJobs(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestDeleteOldReconcileJobs.
    """

    @patch("delete_old_reconcile_jobs.delete_jobs_older_than_x_days")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self,
        mock_get_user_connection: MagicMock,
        mock_delete_jobs_older_than_x_days: MagicMock,
    ):
        """
        Happy path that triggers the various DB tasks.
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)  # nosec
        db_connect_info = Mock()

        delete_old_reconcile_jobs.task(
            internal_reconciliation_expiration_days,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_delete_jobs_older_than_x_days.assert_called_once_with(
            internal_reconciliation_expiration_days,
            mock_get_user_connection.return_value,
        )

    @patch("delete_old_reconcile_jobs.delete_jobs_older_than_x_days_sql")
    @patch("delete_old_reconcile_jobs.delete_catalog_s3_objects_older_than_x_days_sql")
    @patch("delete_old_reconcile_jobs.delete_catalog_phantoms_older_than_x_days_sql")
    @patch("delete_old_reconcile_jobs.delete_catalog_orphans_older_than_x_days_sql")
    @patch("delete_old_reconcile_jobs.delete_catalog_mismatches_older_than_x_days_sql")
    def test_delete_jobs_older_than_x_days_happy_path(
        self,
        mock_delete_catalog_mismatches_older_than_x_days_sql: MagicMock,
        mock_delete_catalog_orphans_older_than_x_days_sql_sql: MagicMock,
        mock_delete_catalog_phantoms_older_than_x_days_sql_sql: MagicMock,
        mock_delete_catalog_s3_objects_older_than_x_days_sql_sql: MagicMock,
        mock_delete_jobs_older_than_x_days_sql_sql: MagicMock,
    ):
        """
        Happy path for deleting all jobs in a list
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)  # nosec
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        now = datetime.datetime.now(datetime.timezone.utc)
        delete_old_reconcile_jobs.delete_jobs_older_than_x_days(
            internal_reconciliation_expiration_days, mock_engine
        )

        mock_enter.__enter__.assert_called_once_with()

        mock_delete_catalog_mismatches_older_than_x_days_sql.assert_called_once_with()
        mock_delete_catalog_orphans_older_than_x_days_sql_sql.assert_called_once_with()
        mock_delete_catalog_orphans_older_than_x_days_sql_sql.assert_called_once_with()
        mock_delete_catalog_s3_objects_older_than_x_days_sql_sql.assert_called_once_with()
        mock_delete_jobs_older_than_x_days_sql_sql.assert_called_once_with()

        mock_execute.assert_has_calls(
            [
                call(
                    mock_delete_catalog_mismatches_older_than_x_days_sql.return_value,
                    [{"cutoff": unittest.mock.ANY}],
                ),
                call(
                    mock_delete_catalog_orphans_older_than_x_days_sql_sql.return_value,
                    [{"cutoff": unittest.mock.ANY}],
                ),
                call(
                    mock_delete_catalog_phantoms_older_than_x_days_sql_sql.return_value,
                    [{"cutoff": unittest.mock.ANY}],
                ),
                call(
                    mock_delete_catalog_s3_objects_older_than_x_days_sql_sql.return_value,
                    [{"cutoff": unittest.mock.ANY}],
                ),
                call(
                    mock_delete_jobs_older_than_x_days_sql_sql.return_value,
                    [{"cutoff": unittest.mock.ANY}],
                ),
            ]
        )
        execute_call_params = mock_execute.call_args[0][1]
        self.assertEqual([{"cutoff": unittest.mock.ANY}], execute_call_params)
        # Make sure that the datetime on the filter is x days ago, accounting for processing time.
        self.assertLessEqual(
            now - datetime.timedelta(days=internal_reconciliation_expiration_days),
            execute_call_params[0]["cutoff"],
        )
        self.assertGreaterEqual(
            datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=internal_reconciliation_expiration_days),
            execute_call_params[0]["cutoff"],
        )
        self.assertEqual(5, mock_execute.call_count)

        mock_exit.assert_called_once_with(None, None, None)

    @patch("delete_old_reconcile_jobs.LOGGER")
    @patch("delete_old_reconcile_jobs.delete_catalog_mismatches_older_than_x_days_sql")
    def test_delete_jobs_older_than_x_days_error_logged_and_raised(
        self,
        mock_delete_catalog_mismatches_older_than_x_days_sql: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)  # nosec
        expected_exception = Exception(uuid.uuid4().__str__())
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
            delete_old_reconcile_jobs.delete_jobs_older_than_x_days(
                internal_reconciliation_expiration_days, mock_engine
            )
        self.assertEqual(expected_exception, cm.exception)
        mock_enter.__enter__.assert_called_once_with()

        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while deleting jobs: {expected_exception}"
        )

    # noinspection PyPep8Naming
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("delete_old_reconcile_jobs.task")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_task: MagicMock,
        mock_get_configuration: MagicMock,
    ):
        """
        Happy path for handler assembling information to call Task.
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)  # nosec

        mock_context = Mock()
        event = Mock()

        with patch.dict(
            os.environ,
            {
                delete_old_reconcile_jobs.OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS: str(
                    internal_reconciliation_expiration_days
                )
            },
        ):
            delete_old_reconcile_jobs.handler(event, mock_context)

        mock_get_configuration.assert_called_once_with(
            os.environ["DB_CONNECT_INFO_SECRET_ARN"]
        )
        mock_task.assert_called_once_with(
            internal_reconciliation_expiration_days,
            mock_get_configuration.return_value,
        )
