import json
from datetime import datetime
from typing import Dict, Optional, Any, List

import requests

from src.adapters.api.aws import S3InventoryManifest, S3InventoryManifestMetadata


class GraphQL:
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
        print(query)
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
        print(query)
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
