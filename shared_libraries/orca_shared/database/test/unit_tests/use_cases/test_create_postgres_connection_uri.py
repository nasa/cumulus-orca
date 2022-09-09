import random
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

from orca_shared.database.entities import PostgresConnectionInfo
from orca_shared.database.use_cases import create_admin_uri, create_user_uri
from orca_shared.database.use_cases.create_postgres_connection_uri import (
    _create_connection_uri,
)


class TestCreatePostgresConnectionUri(unittest.TestCase):

    @patch("orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri")
    def test_create_user_uri_happy_path(
            self,
            mock_create_connection_uri: MagicMock
    ):
        """
        With no optional properties, return admin database uri.
        """
        user_database_name = uuid.uuid4().__str__()  # nosec
        user_username = uuid.uuid4().__str__()  # nosec
        user_password = uuid.uuid4().__str__()  # nosec
        host = uuid.uuid4().__str__()  # nosec
        port = random.randint(0, 99999).__str__()  # nosec
        logger = Mock()

        result = create_user_uri(PostgresConnectionInfo(
            admin_database_name=uuid.uuid4().__str__(),  # nosec
            admin_username=uuid.uuid4().__str__(),  # nosec
            admin_password=uuid.uuid4().__str__(),  # nosec
            user_username=user_username,  # nosec
            user_password=user_password,  # nosec
            user_database_name=user_database_name,  # nosec
            host=host,
            port=port
        ), logger=logger)
        mock_create_connection_uri.assert_called_once_with(logger=logger,
                                                           host=host,
                                                           port=port,
                                                           database=user_database_name,
                                                           username=user_username,
                                                           password=user_password)
        self.assertEqual(mock_create_connection_uri.return_value, result)

    @patch("orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri")
    def test_create_admin_uri_happy_path(
            self,
            mock_create_connection_uri: MagicMock
    ):
        """
        With no optional properties, return admin database uri.
        """
        admin_database_name = uuid.uuid4().__str__()  # nosec
        admin_username = uuid.uuid4().__str__()  # nosec
        admin_password = uuid.uuid4().__str__()  # nosec
        host = uuid.uuid4().__str__()  # nosec
        port = random.randint(0, 99999).__str__()  # nosec
        logger = Mock()

        result = create_admin_uri(PostgresConnectionInfo(
            admin_database_name=admin_database_name,
            admin_username=admin_username,
            admin_password=admin_password,
            user_username=uuid.uuid4().__str__(),  # nosec
            user_password=uuid.uuid4().__str__(),  # nosec
            user_database_name=uuid.uuid4().__str__(),  # nosec
            host=host,
            port=port
        ), logger=logger)
        mock_create_connection_uri.assert_called_once_with(logger=logger,
                                                           host=host,
                                                           port=port,
                                                           database=admin_database_name,
                                                           username=admin_username,
                                                           password=admin_password)
        self.assertEqual(mock_create_connection_uri.return_value, result)

    @patch("orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri")
    def test_create_admin_uri_overwrite_database(
            self,
            mock_create_connection_uri: MagicMock
    ):
        """
        If database name parameter added, use it.
        """
        admin_database_name = uuid.uuid4().__str__()  # nosec
        admin_username = uuid.uuid4().__str__()  # nosec
        admin_password = uuid.uuid4().__str__()  # nosec
        host = uuid.uuid4().__str__()  # nosec
        port = random.randint(0, 99999).__str__()  # nosec
        logger = Mock()

        result = create_admin_uri(PostgresConnectionInfo(
            admin_database_name=uuid.uuid4().__str__(),  # nosec
            admin_username=admin_username,
            admin_password=admin_password,
            user_username=uuid.uuid4().__str__(),  # nosec
            user_password=uuid.uuid4().__str__(),  # nosec
            user_database_name=uuid.uuid4().__str__(),  # nosec
            host=host,
            port=port
        ), logger=logger, database_name_overwrite=admin_database_name)
        mock_create_connection_uri.assert_called_once_with(logger=logger,
                                                           host=host,
                                                           port=port,
                                                           database=admin_database_name,
                                                           username=admin_username,
                                                           password=admin_password)
        self.assertEqual(mock_create_connection_uri.return_value, result)

    def test__create_connection_uri_happy_path(self):
        """
        Basic happy path.
        """
        logger = Mock()
        host = uuid.uuid4().__str__()  # nosec
        port = random.randint(0, 99999)  # nosec
        database_name = uuid.uuid4().__str__()  # nosec
        username = uuid.uuid4().__str__()  # nosec
        password = uuid.uuid4().__str__()  # nosec

        result = _create_connection_uri(logger=logger,
                                        host=host,
                                        port=port,
                                        database=database_name,
                                        username=username,
                                        password=password)

        self.assertEqual(f"postgresql://{username}:{password}@{host}:{port}/{database_name}",
                         result)
