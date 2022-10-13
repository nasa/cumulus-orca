import unittest
from unittest.mock import patch, MagicMock, Mock, call

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases.validation import validate_config


class TestCreatePostgresConnectionUri(unittest.TestCase):

    @patch("orca_shared.database.use_cases.validation._validate_password")
    @patch("orca_shared.database.use_cases.validation.validate_postgres_name")
    def test_validate_config_happy_path(
            self,
            mock_validate_postgres_name: MagicMock,
            mock_validate_password: MagicMock,
    ):
        admin_database_name = Mock()
        admin_username = Mock()
        admin_password = Mock()
        user_username = Mock()
        user_password = Mock()
        user_database_name = Mock()
        host = Mock()
        port = Mock()
        config = PostgresConnectionInfo(
            admin_database_name=admin_database_name,
            admin_username=admin_username,
            admin_password=admin_password,
            user_username=user_username,
            user_password=user_password,
            user_database_name=user_database_name,
            host=host,
            port=port,
        )
        logger = Mock()
        validate_config(config, logger)
        mock_validate_postgres_name.assert_has_calls([
            call(user_username, "User username", logger),
            call(admin_username, "Admin username", logger),
            call(user_database_name, "User database name", logger),
            call(admin_database_name, "Admin database name", logger),
        ])
        self.assertEqual(4, mock_validate_postgres_name.call_count)

        mock_validate_password.assert_called_once_with(user_password, "User", logger)
