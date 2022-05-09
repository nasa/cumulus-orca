"""
Name: test_delete_old_reconcile_jobs.py
Description:  Unit tests for test_delete_old_reconcile_jobs.py.
"""
import copy
import os
import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, call, patch

from orca_shared.reconciliation import OrcaStatus

import delete_old_reconcile_jobs


class TestPerformOrcaReconcile(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestPerformOrcaReconcile.
    """

    @patch("delete_old_reconcile_jobs.delete_jobs")
    @patch("delete_old_reconcile_jobs.get_jobs_older_than_x_days")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self,
        mock_get_user_connection: MagicMock,
        mock_get_jobs_older_than_x_days: MagicMock,
        mock_delete_jobs: MagicMock,
    ):
        """
        Happy path that triggers the various DB tasks.
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)
        db_connect_info = Mock()

        mock_get_jobs_older_than_x_days.return_value = [Mock(), Mock()]

        delete_old_reconcile_jobs.task(
            internal_reconciliation_expiration_days,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_jobs_older_than_x_days.assert_called_once_with(
            internal_reconciliation_expiration_days,
            mock_get_user_connection.return_value,
        )
        mock_delete_jobs.assert_called_once_with(
            mock_get_jobs_older_than_x_days.return_value,
            mock_get_user_connection.return_value
        )

    @patch("delete_old_reconcile_jobs.delete_jobs")
    @patch("delete_old_reconcile_jobs.get_jobs_older_than_x_days")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_no_jobs_found_does_not_delete(
            self,
            mock_get_user_connection: MagicMock,
            mock_get_jobs_older_than_x_days: MagicMock,
            mock_delete_jobs: MagicMock,
    ):
        """
        If there are no jobs to delete, don't waste time calling the DB function
        """
        internal_reconciliation_expiration_days = random.randint(1, 300)
        db_connect_info = Mock()

        mock_get_jobs_older_than_x_days.return_value = None

        delete_old_reconcile_jobs.task(
            internal_reconciliation_expiration_days,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_get_jobs_older_than_x_days.assert_called_once_with(
            internal_reconciliation_expiration_days,
            mock_get_user_connection.return_value,
        )
        mock_delete_jobs.assert_not_called(
        )

    @patch("delete_old_reconcile_jobs.get_jobs_sql")
    def test_get_jobs_older_than_x_days_happy_path(
        self,
        mock_get_jobs_sql: MagicMock,
    ):
        """
        Happy path for getting jobs older than x days
        """
        ids = [random.randint(0, 9999), random.randint(0, 9999)]
        internal_reconciliation_expiration_days = random.randint(1, 300)
        mock_sql_result = Mock()
        mock_sql_result.fetchone = Mock(return_value=[copy.deepcopy(ids)])
        mock_execute = Mock()
        mock_execute.return_value = mock_sql_result
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = delete_old_reconcile_jobs.get_jobs_older_than_x_days(
            internal_reconciliation_expiration_days, mock_engine
        )

        mock_enter.__enter__.assert_called_once_with()

        mock_get_jobs_sql.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_jobs_sql.return_value,
            [
                {
                    "internal_reconciliation_expiration_days": internal_reconciliation_expiration_days
                }
            ],
        )

        mock_sql_result.fetchone.assert_called_once_with()

        mock_exit.assert_called_once_with(None, None, None)

        self.assertEqual(ids, result)

    @patch("delete_old_reconcile_jobs.LOGGER")
    @patch("delete_old_reconcile_jobs.get_jobs_sql")
    def test_get_jobs_older_than_x_days_error_logged_and_raised(
        self,
        mock_get_jobs_sql: MagicMock,
        mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        expected_exception = Exception(uuid.uuid4().__str__())
        internal_reconciliation_expiration_days = random.randint(1, 300)
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
            delete_old_reconcile_jobs.get_jobs_older_than_x_days(
                internal_reconciliation_expiration_days, mock_engine
            )
        self.assertEqual(expected_exception, cm.exception)
        mock_enter.__enter__.assert_called_once_with()

        mock_exit.assert_called_once_with(
            Exception, expected_exception, unittest.mock.ANY
        )
        mock_logger.error.assert_called_once_with(
            f"Error while getting jobs: {expected_exception}"
        )

    @patch("delete_old_reconcile_jobs.delete_jobs_sql")
    def test_delete_jobs_happy_path(
            self,
            mock_delete_jobs_sql: MagicMock,
    ):
        """
        Happy path for deleting all jobs in a list
        """
        ids = [random.randint(0, 9999), random.randint(0, 9999)]
        mock_execute = Mock()
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        delete_old_reconcile_jobs.delete_jobs(
            ids, mock_engine
        )

        mock_enter.__enter__.assert_called_once_with()

        mock_delete_jobs_sql.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_delete_jobs_sql.return_value,
            [
                {"job_ids_to_delete": ids}
            ],
        )

        mock_exit.assert_called_once_with(None, None, None)

    @patch("delete_old_reconcile_jobs.LOGGER")
    @patch("delete_old_reconcile_jobs.delete_jobs_sql")
    def test_get_jobs_older_than_x_days_error_logged_and_raised(
            self,
            mock_delete_jobs_sql: MagicMock,
            mock_logger: MagicMock,
    ):
        """
        Exceptions from Postgres should bubble up.
        """
        ids = [random.randint(0, 9999), random.randint(0, 9999)]
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
            delete_old_reconcile_jobs.delete_jobs(
                ids,
                mock_engine
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
    @patch("delete_old_reconcile_jobs.LOGGER")
    @patch("delete_old_reconcile_jobs.task")
    @patch.dict(
        os.environ,
        {
            "DB_CONNECT_INFO_SECRET_ARN": "test"
        },
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
        internal_reconciliation_expiration_days = random.randint(1, 300)

        mock_context = Mock()
        event = Mock()

        with patch.dict(
            os.environ,
            {
                delete_old_reconcile_jobs.OS_ENVIRON_INTERNAL_RECONCILIATION_EXPIRATION_DAYS: str(internal_reconciliation_expiration_days)
            },
        ):
            delete_old_reconcile_jobs.handler(event, mock_context)

        mock_LOGGER.setMetadata.assert_called_once_with(event, mock_context)
        mock_get_configuration.assert_called_once_with(os.environ["DB_CONNECT_INFO_SECRET_ARN"])
        mock_task.assert_called_once_with(
            internal_reconciliation_expiration_days,
            mock_get_configuration.return_value,
        )
