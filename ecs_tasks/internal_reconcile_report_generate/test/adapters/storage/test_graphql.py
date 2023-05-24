import copy
import unittest
import uuid
from unittest.mock import ANY, MagicMock, Mock, patch

from src.adapters.storage.graphql import GraphQL
from src.entities.aws import (
    AWSS3FileLocation,
    S3InventoryManifest,
    S3InventoryManifestMetadata,
)


class MyTestCase(unittest.TestCase):
    @patch("src.adapters.storage.graphql.GraphQL.perform_request")
    def test_create_job_happy_path(
        self,
        mock_perform_request: MagicMock,
    ):
        """
        Happy path for posting job status to GraphQL.
        """
        mock_graphql_endpoint = Mock()
        inventory_creation_timestamp = uuid.uuid4().__str__()
        report_source = uuid.uuid4().__str__()
        cursor = Mock()
        mock_perform_request.return_value = {
            "postInternalReconciliationJob": {
                "cursor": cursor
            }
        }

        result = GraphQL(mock_graphql_endpoint) \
            .create_job(inventory_creation_timestamp, report_source)

        mock_perform_request.assert_called_once_with(ANY, "postInternalReconciliationJob",
                                                     "InternalReconcileReportCreationRecord")
        self.assertEqual(cursor, result)

    @patch("src.adapters.storage.graphql.GraphQL.perform_request")
    def test_import_current_archive_list_for_reconciliation_job_happy_path(
        self,
        mock_perform_request: MagicMock,
    ):
        """
        Happy path for triggering archive import.
        """
        mock_graphql_endpoint = Mock()

        GraphQL(mock_graphql_endpoint).import_current_archive_list_for_reconciliation_job(
            S3InventoryManifest(
                source_bucket_name=uuid.uuid4().__str__(),
                manifest_creation_datetime=uuid.uuid4().__str__(),
                manifest_files=[AWSS3FileLocation(uuid.uuid4().__str__(), uuid.uuid4().__str__())],
                manifest_files_columns="col0, col1"
            ),
            S3InventoryManifestMetadata(
                report_bucket_region=uuid.uuid4().__str__(),
                report_bucket_name=uuid.uuid4().__str__(),
                manifest_key=uuid.uuid4().__str__(),
            ),
            uuid.uuid4().__str__(),
        )

        mock_perform_request.assert_called_once_with(
            ANY,
            "importCurrentArchiveListForReconciliationJob",
            None,
        )

    @patch("src.adapters.storage.graphql.GraphQL.perform_request")
    def test_perform_orca_reconcile_for_reconciliation_job_happy_path(
        self,
        mock_perform_request: MagicMock,
    ):
        """
        Happy path for triggering report generation.
        """
        mock_graphql_endpoint = Mock()
        report_cursor = uuid.uuid4().__str__()
        report_source = uuid.uuid4().__str__()
        cursor = Mock()
        mock_perform_request.return_value = {
            "postInternalReconciliationJob": {
                "cursor": cursor
            }
        }

        GraphQL(mock_graphql_endpoint) \
            .perform_orca_reconcile_for_reconciliation_job(report_source, report_cursor)

        mock_perform_request.assert_called_once_with(
            ANY,
            "performOrcaReconcileForReconciliationJob",
            None)

    @patch("src.adapters.storage.graphql.requests.post")
    def test_perform_request_happy_path(
        self,
        mock_post: MagicMock,
    ):
        """
        Happy path for sending/receiving from GraphQL.
        """
        mock_graphql_endpoint = Mock()
        mock_query = Mock()
        mock_query_name = Mock()
        expected_type = uuid.uuid4().__str__()
        mock_response = Mock()
        mock_response.status_code = 200
        returned_data = {
            mock_query_name: {
                "__typename": expected_type
            }
        }
        mock_response.json = Mock(return_value={
            "data": copy.copy(returned_data)
        })
        mock_post.return_value = mock_response

        result = GraphQL(mock_graphql_endpoint).perform_request(
            mock_query,
            mock_query_name,
            expected_type,
        )

        mock_post.assert_called_once_with(
            mock_graphql_endpoint, json={"query": mock_query}, headers={})
        mock_response.json.assert_called_once_with()
        self.assertEqual(returned_data, result)

    @patch("src.adapters.storage.graphql.requests.post")
    def test_perform_request_expected_empty_happy_path(
        self,
        mock_post: MagicMock,
    ):
        """
        Happy path for sending/receiving from GraphQL.
        """
        mock_graphql_endpoint = Mock()
        mock_query = Mock()
        mock_query_name = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        returned_data = {
            mock_query_name: None
        }
        mock_response.json = Mock(return_value={
            "data": copy.copy(returned_data)
        })
        mock_post.return_value = mock_response

        result = GraphQL(mock_graphql_endpoint).perform_request(
            mock_query,
            mock_query_name,
            None,
        )

        mock_post.assert_called_once_with(
            mock_graphql_endpoint, json={"query": mock_query}, headers={})
        mock_response.json.assert_called_once_with()
        self.assertEqual(returned_data, result)

    @patch("src.adapters.storage.graphql.requests.post")
    def test_perform_request_non_200_raises_error(
        self,
        mock_post: MagicMock,
    ):
        """
        If GraphQL communication fails, raise error.
        """
        mock_graphql_endpoint = Mock()
        mock_query = Mock()
        mock_query_name = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        returned_data = {
            mock_query_name: None
        }
        mock_response.json = Mock(return_value={
            "data": copy.copy(returned_data)
        })
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as cm:
            GraphQL(mock_graphql_endpoint).perform_request(
                mock_query,
                mock_query_name,
                None,
            )

        mock_post.assert_called_once_with(
            mock_graphql_endpoint, json={"query": mock_query}, headers={})
        self.assertEqual(
            f"Query failed to run with a {mock_response.status_code}.", str(cm.exception))

    @patch("src.adapters.storage.graphql.requests.post")
    def test_perform_request_errors_raises_error(
        self,
        mock_post: MagicMock,
    ):
        """
        If GraphQL returns errors, raise.
        """
        mock_graphql_endpoint = Mock()
        mock_query = Mock()
        mock_query_name = Mock()
        expected_type = uuid.uuid4().__str__()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_errors = Mock()
        mock_response.json = Mock(return_value={
            "errors": mock_errors
        })
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as cm:
            GraphQL(mock_graphql_endpoint).perform_request(
                mock_query,
                mock_query_name,
                expected_type,
            )
        self.assertEqual(
            f"Exceptions raised during GraphQL query: {mock_errors}", str(cm.exception))

        mock_post.assert_called_once_with(
            mock_graphql_endpoint, json={"query": mock_query}, headers={})
        mock_response.json.assert_called_once_with()

    @patch("src.adapters.storage.graphql.requests.post")
    def test_perform_request_mismatched_type_raises_error(
        self,
        mock_post: MagicMock,
    ):
        """
        If GraphQL return type is not expected, raise error.
        """
        mock_graphql_endpoint = Mock()
        mock_query = Mock()
        mock_query_name = Mock()
        expected_type = uuid.uuid4().__str__()
        returned_type = uuid.uuid4().__str__()
        mock_response = Mock()
        mock_response.status_code = 200
        returned_data = {
            mock_query_name: {
                "__typename": returned_type
            }
        }
        mock_response.json = Mock(return_value={
            "data": copy.copy(returned_data)
        })
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as cm:
            GraphQL(mock_graphql_endpoint).perform_request(
                mock_query,
                mock_query_name,
                expected_type,
            )
        self.assertEqual(f"Type '{returned_type}' not allowed. Expected '{expected_type}'. "
                         f"All data: '{str(returned_data)}'", str(cm.exception))

        mock_post.assert_called_once_with(
            mock_graphql_endpoint, json={"query": mock_query}, headers={})
        mock_response.json.assert_called_once_with()
