"""
Name: test_orca_catalog_reporting.py

Description:  Unit tests for orca_catalog_reporting.py.
"""
import os
import random
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

import orca_catalog_reporting


class TestOrcaCatalogReportingUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    @patch("orca_catalog_reporting.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_happy_path(
        self,
        mock_setMetadata: MagicMock,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Basic path with all information present.
        Should call task.
        """
        page_index = random.randint(0, 999)  # nosec
        provider_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        collection_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        granule_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        start_timestamp = random.randint(0, 628021800000)  # nosec
        end_timestamp = random.randint(0, 628021800000)  # nosec

        event = {
            "pageIndex": page_index,
            "providerId": provider_id,
            "collectionId": collection_id,
            "granuleId": granule_id,
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
        }
        context = Mock()
        mock_task.return_value = {
            "anotherPage": False,
            "granules": [
                {
                    "providerId": uuid.uuid4().__str__(),
                    "collectionId": uuid.uuid4().__str__(),
                    "id": uuid.uuid4().__str__(),
                    "createdAt": random.randint(0, 628021800000),  # nosec
                    "executionId": uuid.uuid4().__str__(),
                    "ingestDate": random.randint(0, 628021800000),  # nosec
                    "lastUpdate": random.randint(0, 628021800000),  # nosec
                    "files": [
                        {
                            "name": uuid.uuid4().__str__(),
                            "cumulusArchiveLocation": uuid.uuid4().__str__(),
                            "orcaArchiveLocation": uuid.uuid4().__str__(),
                            "keyPath": uuid.uuid4().__str__(),
                            "sizeBytes": random.randint(0, 999),  # nosec
                            "hash": uuid.uuid4().__str__(),
                            "hashType": uuid.uuid4().__str__(),
                            "storageClass": uuid.uuid4().__str__(),
                            "version": uuid.uuid4().__str__(),
                        }
                    ],
                }
            ],
        }

        result = orca_catalog_reporting.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
            mock_get_configuration.return_value,
        )
        self.assertEqual(mock_task.return_value, result)

    @patch("orca_catalog_reporting.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_properties_uses_default(
        self,
        mock_setMetadata: MagicMock,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
    ):
        """
        Most properties default to null.
        """
        page_index = random.randint(0, 999)  # nosec
        end_timestamp = random.randint(0, 628021800000)  # nosec

        event = {"pageIndex": page_index, "endTimestamp": end_timestamp}
        context = Mock()
        mock_task.return_value = {"anotherPage": False, "granules": []}

        result = orca_catalog_reporting.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_task.assert_called_once_with(
            None,
            None,
            None,
            None,
            end_timestamp,
            page_index,
            mock_get_configuration.return_value,
        )
        self.assertEqual(mock_task.return_value, result)

    @patch("orca_catalog_reporting.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_missing_page_index_returns_error(
        self,
        mock_setMetadata: MagicMock,
        mock_get_configuration: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        page_index should be required by schema.
        """
        provider_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        collection_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        granule_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        start_timestamp = random.randint(0, 628021800000)  # nosec
        end_timestamp = random.randint(0, 628021800000)  # nosec

        event = {
            "pageIndex": None,
            "providerId": provider_id,
            "collectionId": collection_id,
            "granuleId": granule_id,
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
        }
        context = Mock()
        result = orca_catalog_reporting.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            "data.pageIndex must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("orca_catalog_reporting.create_http_error_dict")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_missing_end_timestamp_returns_error(
        self,
        mock_setMetadata: MagicMock,
        mock_get_configuration: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        end_timestamp should be required by schema.
        """
        page_index = random.randint(0, 999)  # nosec
        provider_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        collection_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        granule_id = [uuid.uuid4().__str__(), uuid.uuid4().__str__()]
        start_timestamp = random.randint(0, 628021800000)  # nosec

        event = {
            "pageIndex": page_index,
            "providerId": provider_id,
            "collectionId": collection_id,
            "granuleId": granule_id,
            "startTimestamp": start_timestamp,
        }
        context = Mock()
        result = orca_catalog_reporting.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "BadRequest",
            HTTPStatus.BAD_REQUEST,
            context.aws_request_id,
            "data must contain ['pageIndex', 'endTimestamp'] properties",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("orca_catalog_reporting.create_http_error_dict")
    @patch("orca_catalog_reporting.task")
    @patch("orca_shared.database.shared_db.get_configuration")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    @patch.dict(
        os.environ,
        {"DB_CONNECT_INFO_SECRET_ARN": "test"},
        clear=True,
    )
    def test_handler_bad_output_raises_error(
        self,
        mock_setMetadata: MagicMock,
        mock_get_configuration: MagicMock,
        mock_task: MagicMock,
        mock_create_http_error_dict: MagicMock,
    ):
        """
        Output validity should be checked, and return an error code if invalid.
        """
        event = {
            "pageIndex": random.randint(0, 999),  # nosec
            "providerId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
            "collectionId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
            "granuleId": [uuid.uuid4().__str__(), uuid.uuid4().__str__()],
            "startTimestamp": random.randint(0, 628021800000),  # nosec
            "endTimestamp": random.randint(0, 628021800000),  # nosec
        }
        context = Mock()
        mock_task.return_value = {
            "anotherPage": False,
            "granules": [
                {
                    "providerId": uuid.uuid4().__str__(),
                    "collectionId": uuid.uuid4().__str__(),
                    "id": uuid.uuid4().__str__(),
                    "createdAt": 628021800000,
                    "executionId": uuid.uuid4().__str__(),
                    "ingestDate": 628021800000,
                    "lastUpdate": "2021-10-08T16:24:07.605323Z",
                    "files": [
                        {
                            "name": uuid.uuid4().__str__(),
                            "cumulusArchiveLocation": uuid.uuid4().__str__(),
                            "orcaArchiveLocation": uuid.uuid4().__str__(),
                            "keyPath": uuid.uuid4().__str__(),
                            "sizeBytes": random.randint(0, 999),  # nosec
                            "hash": uuid.uuid4().__str__(),
                            "hashType": uuid.uuid4().__str__(),
                            "storageClass": uuid.uuid4().__str__(),
                            "version": uuid.uuid4().__str__(),
                        }
                    ],
                }
            ],
        }

        result = orca_catalog_reporting.handler(event, context)
        mock_create_http_error_dict.assert_called_once_with(
            "InternalServerError",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            context.aws_request_id,
            "data.granules[0].lastUpdate must be integer",
        )
        self.assertEqual(mock_create_http_error_dict.return_value, result)

    @patch("orca_catalog_reporting.query_db")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_happy_path(
        self, mock_get_user_connection: MagicMock, mock_query_db: MagicMock
    ):
        """
        Task should call query_db, and send granules back.
        """
        provider_id = Mock()
        collection_id = Mock()
        granule_id = Mock()
        start_timestamp = Mock()
        end_timestamp = Mock()
        page_index = Mock()
        db_connect_info = Mock()

        granules = []
        for i in range(orca_catalog_reporting.PAGE_SIZE):
            granules.append(Mock)
        mock_query_db.return_value = granules

        result = orca_catalog_reporting.task(
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_query_db.assert_called_once_with(
            mock_get_user_connection.return_value,
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
        )
        self.assertEqual({"anotherPage": False, "granules": granules}, result)

    @patch("orca_catalog_reporting.query_db")
    @patch("orca_shared.database.shared_db.get_user_connection")
    def test_task_another_page(
        self, mock_get_user_connection: MagicMock, mock_query_db: MagicMock
    ):
        """
        Task should call query_db, and send granules back.
        If there are more granules than PAGE_SIZE, limit them and set "anotherPage" to True
        """
        provider_id = Mock()
        collection_id = Mock()
        granule_id = Mock()
        start_timestamp = Mock()
        end_timestamp = Mock()
        page_index = Mock()
        db_connect_info = Mock()

        granules = []
        for i in range(orca_catalog_reporting.PAGE_SIZE + 1):
            granules.append(Mock)
        mock_query_db.return_value = granules

        result = orca_catalog_reporting.task(
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
            db_connect_info,
        )

        mock_get_user_connection.assert_called_once_with(db_connect_info)
        mock_query_db.assert_called_once_with(
            mock_get_user_connection.return_value,
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
        )
        self.assertEqual(
            {
                "anotherPage": True,
                "granules": granules[0 : orca_catalog_reporting.PAGE_SIZE],
            },
            result,
        )

    @patch("orca_catalog_reporting.get_catalog_sql")
    def test_query_db_happy_path(self, mock_get_catalog_sql: MagicMock):
        """
        Should query the db, then format the returned data.
        """
        provider_id = Mock()
        collection_id = Mock()
        granule_id = Mock()
        start_timestamp = Mock()
        end_timestamp = Mock()
        page_index = Mock()

        returned_provider_id = Mock()
        returned_collection_id = Mock()
        returned_granule_id = Mock()
        returned_created_at = random.randint(0, 628021800000)  # nosec
        returned_execution_id = Mock()
        returned_ingest_time = random.randint(0, 628021800000)  # nosec
        returned_last_update = random.randint(0, 628021800000)  # nosec
        returned_files = Mock()

        returned_row0 = {
            "provider_id": returned_provider_id,
            "collection_id": returned_collection_id,
            "cumulus_granule_id": returned_granule_id,
            "cumulus_create_time": returned_created_at,
            "execution_id": returned_execution_id,
            "ingest_time": returned_ingest_time,
            "last_update": returned_last_update,
            "files": returned_files,
        }
        mock_execute = Mock(return_value=[returned_row0])
        mock_connection = Mock()
        mock_connection.execute = mock_execute
        mock_exit = Mock(return_value=False)
        mock_enter = Mock()
        mock_enter.__enter__ = Mock(return_value=mock_connection)
        mock_enter.__exit__ = mock_exit
        mock_engine = Mock()
        mock_engine.begin = Mock(return_value=mock_enter)

        result = orca_catalog_reporting.query_db(
            mock_engine,
            provider_id,
            collection_id,
            granule_id,
            start_timestamp,
            end_timestamp,
            page_index,
        )

        mock_enter.__enter__.assert_called_once_with()
        mock_execute.assert_called_once_with(
            mock_get_catalog_sql.return_value,
            [
                {
                    "provider_id": provider_id,
                    "collection_id": collection_id,
                    "granule_id": granule_id,
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp,
                    "page_index": page_index,
                    "page_size": orca_catalog_reporting.PAGE_SIZE,
                }
            ],
        )
        mock_exit.assert_called_once_with(None, None, None)
        mock_get_catalog_sql.assert_called_once_with()
        self.assertEqual(
            [
                {
                    "providerId": returned_provider_id,
                    "collectionId": returned_collection_id,
                    "id": returned_granule_id,
                    "createdAt": returned_created_at,
                    "executionId": returned_execution_id,
                    "ingestDate": returned_ingest_time,
                    "lastUpdate": returned_last_update,
                    "files": returned_files,
                }
            ],
            result,
        )

    @patch("cumulus_logger.CumulusLogger.error")
    def test_create_http_error_dict_happy_path(self, mock_error: MagicMock):
        error_type = uuid.uuid4().__str__()
        http_status_code = random.randint(0, 9999)  # nosec
        request_id = uuid.uuid4().__str__()
        message = uuid.uuid4().__str__()

        result = orca_catalog_reporting.create_http_error_dict(
            error_type, http_status_code, request_id, message
        )

        self.assertEqual(
            {
                "errorType": error_type,
                "httpStatus": http_status_code,
                "requestId": request_id,
                "message": message,
            },
            result,
        )

        mock_error.assert_called_once_with(message)
