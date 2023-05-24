import json
from typing import Any, Optional

import requests

from src.adapters.api.aws import S3InventoryManifest, S3InventoryManifestMetadata
from src.use_cases.adapter_interfaces.storage import StorageInterface


class GraphQL(StorageInterface):
    def __init__(
        self,
        graphql_endpoint: str,
    ):
        self.graphql_endpoint = graphql_endpoint

    def create_job(
        self,
        inventory_creation_timestamp: float,
        report_source: str,
    ) -> str:
        """
        Creates a job status entry.

        Args:
            inventory_creation_timestamp: Seconds since epoch that the inventory was created.
            report_source: The region covered by the report.

        Returns: The cursor to the reconciliation job.
        """
        query_name = "postInternalReconciliationJob"
        expected_type = "InternalReconcileReportCreationRecord"
        query = f"""
mutation {{
  {query_name}(
    creationTimestamp: {inventory_creation_timestamp}
    reportSource: "{report_source}"
  ) {{
    ... on {expected_type} {{
      __typename
      cursor
    }}
    ... on InternalServerErrorGraphqlType {{
      __typename
      exceptionMessage
      message
      stackTrace
    }}
    ... on ErrorGraphqlTypeInterface {{
      __typename
      message
    }}
  }}
}}"""
        result = self.perform_request(
            query,
            query_name,
            expected_type,
        )
        return result["postInternalReconciliationJob"]["cursor"]

    def import_current_archive_list_for_reconciliation_job(
        self,
        inventory_manifest: S3InventoryManifest,
        inventory_manifest_metadata: S3InventoryManifestMetadata,
        report_cursor: str,
    ) -> None:
        """
        Pulls the inventory report into the database.

        Args:
            inventory_manifest: Contains information about the inventory report.
            inventory_manifest_metadata: Extra information about the inventory report.
            report_cursor: The cursor to the reconciliation job.
        """
        query_name = "importCurrentArchiveListForReconciliationJob"
        expected_type = None
        # GraphQL does not support standard json. See csvFileLocations
        # todo: Check for security/character issues with csvFileLocations
        query = f"""
    mutation {{
      {query_name}(
        reportSource: "{inventory_manifest.source_bucket_name}"
        reportCursor: "{report_cursor}"
        columnsInCsv: {json.dumps(inventory_manifest.manifest_files_columns)}
        csvFileLocations: [{{{"}, {".join([
            f'bucketName: "{f.bucket_name}", key: "{f.key}"'
            for f in inventory_manifest.manifest_files
        ])
        }}}]
        reportBucketRegion: "{inventory_manifest_metadata.report_bucket_region}"
      ) {{
        ... on InternalServerErrorGraphqlType {{
          __typename
          exceptionMessage
          message
          stackTrace
        }}
        ... on ErrorGraphqlTypeInterface {{
          __typename
          message
        }}
      }}
    }}"""
        self.perform_request(
            query,
            query_name,
            expected_type,
        )

    def perform_orca_reconcile_for_reconciliation_job(
        self,
        report_source: str,
        report_cursor: str,
    ) -> None:
        """
        Checks the pulled-in inventory report against the database's expectations.

        Args:
            report_source: The region covered by the report.
            report_cursor: The cursor to the reconciliation job.
        """
        query_name = "performOrcaReconcileForReconciliationJob"
        expected_type = None
        query = f"""
    mutation {{
      {query_name}(
        reportSource: "{report_source}"
        reportCursor: "{report_cursor}"
      ) {{
        ... on InternalServerErrorGraphqlType {{
          __typename
          exceptionMessage
          message
          stackTrace
        }}
        ... on ErrorGraphqlTypeInterface {{
          __typename
          message
        }}
      }}
    }}"""
        print(query)
        self.perform_request(
            query,
            query_name,
            expected_type,
        )

    def perform_request(
        self,
        query: str,
        query_name: str,
        expected_type: Optional[str],
    ) -> Optional[dict[str, Any]]:
        """
        Helper for communicating with GraphQL

        Args:
            query: The query to perform.
            query_name: The name of the query. Used for results validity checks.
            expected_type: The expected type to be returned. All other types rejected.
        Returns:
            The data returned by GraphQL.

        Raises:
            Exception if GraphQL returned a non-200 status id
            or returned types outside expected_type.
        """
        r = requests.post(self.graphql_endpoint, json={"query": query}, headers={})
        if r.status_code != 200:
            raise Exception(f"Query failed to run with a {r.status_code}.")

        result = r.json()
        errors = result.get("errors", None)
        if errors is not None:
            raise Exception(f"Exceptions raised during GraphQL query: {errors}")

        data = result.get("data", None)

        # Identify when data contains an unexpected data type. May indicate error.
        returned_type = None
        if data[query_name] is not None:
            returned_type = data[query_name]["__typename"]
        if expected_type != returned_type:
            raise TypeError(f"Type '{returned_type}' not allowed. Expected '{expected_type}'. "
                            f"All data: '{str(data)}'")

        return result.get("data", None)
