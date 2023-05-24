import json
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from src.adapters.webserver.application import get_application


class TestApplication(unittest.TestCase):

    @patch("src.adapters.webserver.application.create_fastapi_app")
    @patch("src.adapters.webserver.application.AdaptersStorage")
    @patch("src.adapters.webserver.application.InternalReconciliationStorageAdapterPostgres")
    @patch("src.adapters.webserver.application.StorageAdapterPostgres")
    @patch("src.adapters.webserver.application.UUIDWordGeneration")
    @patch("src.adapters.webserver.application.create_postgres_connection_uri")
    @patch("src.adapters.webserver.application.PostgresConnectionInfo")
    @patch("src.adapters.webserver.application.validate_config")
    @patch("src.adapters.webserver.application.JsonLoggerProvider")
    def test_get_application_happy_path(
        self,
        mock_basic_logger_provider: MagicMock,
        mock_validate_config: MagicMock,
        mock_postgres_connection_info: MagicMock,
        mock_create_postgres_connection_uri: MagicMock,
        mock_uuid_word_generation: MagicMock,
        mock_storage_adapter_postgres: MagicMock,
        mock_internal_reconciliation_storage_adapter_postgres: MagicMock,
        mock_adapters_storage: MagicMock,
        mock_create_fastapi_app: MagicMock,
    ):
        """
        Should set up adapters and application based on given settings.
        """
        mock_admin_database = uuid.uuid4().__str__()
        mock_admin_username = uuid.uuid4().__str__()
        mock_admin_password = uuid.uuid4().__str__()
        mock_user_database = uuid.uuid4().__str__()
        mock_user_username = uuid.uuid4().__str__()
        mock_user_password = uuid.uuid4().__str__()
        mock_host = uuid.uuid4().__str__()
        mock_port = uuid.uuid4().__str__()
        mock_s3_access_key = uuid.uuid4().__str__()
        mock_s3_secret_key = uuid.uuid4().__str__()

        mock_uvicorn_settings = Mock()
        mock_uvicorn_settings.DB_CONNECT_INFO = json.dumps({
            "admin_database": mock_admin_database,
            "admin_username": mock_admin_username,
            "admin_password": mock_admin_password,
            "user_database": mock_user_database,
            "user_username": mock_user_username,
            "user_password": mock_user_password,
            "host": mock_host,
            "port": mock_port,
        })
        mock_uvicorn_settings.S3_ACCESS_CREDENTIALS = json.dumps({
            "s3_access_key": mock_s3_access_key,
            "s3_secret_key": mock_s3_secret_key,
        })

        result = get_application(mock_uvicorn_settings)

        mock_basic_logger_provider.assert_called_once_with()
        mock_basic_logger_provider.return_value.get_logger.assert_called_once_with("Setup")
        mock_logger = mock_basic_logger_provider.return_value.get_logger.return_value

        mock_postgres_connection_info.assert_called_once_with(
            admin_database_name=mock_admin_database,
            admin_username=mock_admin_username,
            admin_password=mock_admin_password,
            user_username=mock_user_username,
            user_password=mock_user_password,
            user_database_name=mock_user_database,
            host=mock_host,
            port=mock_port,
        )
        mock_validate_config.assert_called_once_with(
            mock_postgres_connection_info.return_value,
            mock_logger,
        )
        mock_create_postgres_connection_uri.create_user_uri.assert_called_once_with(
            mock_postgres_connection_info.return_value,
            mock_logger,
        )
        mock_create_postgres_connection_uri.create_admin_uri.assert_called_once_with(
            mock_postgres_connection_info.return_value,
            mock_logger,
            mock_postgres_connection_info.return_value.user_database_name,
        )
        mock_uuid_word_generation.assert_called_once_with()
        mock_storage_adapter_postgres.assert_called_once_with(
            mock_create_postgres_connection_uri.create_user_uri.return_value)
        mock_internal_reconciliation_storage_adapter_postgres.assert_called_once_with(
            mock_create_postgres_connection_uri.create_user_uri.return_value,
            mock_create_postgres_connection_uri.create_admin_uri.return_value,
            mock_s3_access_key,
            mock_s3_secret_key,
        )
        mock_adapters_storage.assert_called_once_with(
            mock_uuid_word_generation.return_value,
            mock_storage_adapter_postgres.return_value,
            mock_internal_reconciliation_storage_adapter_postgres.return_value,
            mock_basic_logger_provider.return_value,
        )
        mock_create_fastapi_app.assert_called_once_with(
            mock_uvicorn_settings, mock_adapters_storage.return_value)

        self.assertEqual(mock_create_fastapi_app.return_value, result)
