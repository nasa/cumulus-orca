import json
import os
import time
import unittest
import uuid
from unittest import TestCase

import boto3
from requests import Session

import helpers
import testtools


class TestIngestWorkflows(TestCase):
    API_LOCAL_HOST = "127.0.0.1"
    API_LOCAL_PORT = "8000"

    storage_bucket_name: str = None
    aws_region: str = None
    orca_copy_to_glacier_step_function_arn: str = None

    MY_SESSION: Session = None
    AWS_API_NAME: str = None
    API_URL: str = None

    def setUp(self) -> None:
        print("Running setUp for tests.")

        # Pull from environ
        # ---
        TestIngestWorkflows.storage_bucket_name = os.environ[
            "bamboo_STORAGE_BUCKET_NAME"
        ]
        TestIngestWorkflows.aws_region = os.environ["bamboo_AWS_DEFAULT_REGION"]
        orca_api_deployment_invoke_url = os.environ["orca_API_DEPLOYMENT_INVOKE_URL"]
        TestIngestWorkflows.orca_copy_to_glacier_step_function_arn = os.environ[
            "orca_COPY_TO_GLACIER_STEP_FUNCTION_ARN"
        ]

        # Set up Orca API resources
        # ---
        TestIngestWorkflows.AWS_API_NAME = orca_api_deployment_invoke_url.replace(
            "https://", ""
        )
        TestIngestWorkflows.API_URL = f"https://{TestIngestWorkflows.AWS_API_NAME}:{TestIngestWorkflows.API_LOCAL_PORT}/orca"
        TestIngestWorkflows.MY_SESSION = Session()
        TestIngestWorkflows.MY_SESSION.mount(
            TestIngestWorkflows.API_URL,
            helpers.DNSResolverHTTPSAdapter(
                TestIngestWorkflows.AWS_API_NAME, TestIngestWorkflows.API_LOCAL_HOST
            ),
        )

    def test_catalog_provider_does_not_exist_returns_empty_granules_list(self):
        """
        Presently, we do not raise an error if the providerId is not present in our catalog.
        """
        catalog_output = helpers.post_to_api(
            TestIngestWorkflows.MY_SESSION,
            TestIngestWorkflows.API_URL + "/catalog/reconcile/",
            data=json.dumps(
                {
                    "pageIndex": 0,
                    "providerId": [uuid.uuid4().__str__()],
                    "endTimestamp": int((time.time() + 5) * 1000),
                }
            ),
            headers={"Host": TestIngestWorkflows.AWS_API_NAME},
        )
        self.assertEqual(200, catalog_output.status_code)
        self.assertEqual({"granules": [], "anotherPage": False}, catalog_output.json())

    def test_ingest_no_granules_passes(self):
        """
        If no granules are provided, should not store anything in DB.
        """
        provider_id = uuid.uuid4().__str__()
        provider_name = uuid.uuid4().__str__()

        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()

        execution_id = uuid.uuid4().__str__()

        # note that this does not cover all available properties
        copy_to_glacier_input = {
            "payload": {"granules": []},
            "meta": {
                "collection": {"name": collection_name, "version": collection_version},
                "provider": {
                    "id": provider_id,
                    "name": provider_name,
                },
            },
            "cumulus_meta": {"execution_name": execution_id},
        }

        expected_output = {
            "payload": {"granules": [], "copied_to_glacier": []},
            "meta": {
                "collection": {"name": collection_name, "version": collection_version},
                "provider": {"id": provider_id, "name": provider_name},
            },
            "cumulus_meta": {"execution_name": execution_id},
            "task_config": {
                "excludeFileTypes": "{$.meta.collection.meta.excludeFileTypes}",
                "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
                "providerId": "{$.meta.provider.id}",
                "providerName": "{$.meta.provider.name}",
                "executionId": "{$.cumulus_meta.execution_name}",
                "collectionShortname": "{$.meta.collection.name}",
                "collectionVersion": "{$.meta.collection.version}",
                "orcaDefaultBucketOverride": "{$.meta.collection.meta.orcaDefaultBucketOverride}",
                "orcaDefaultStorageClassOverride": "{$.meta.collection.meta.orcaDefaultStorageClassOverride}",
            },
            "exception": "None",
        }

        execution_info = boto3.client("stepfunctions").start_execution(
            stateMachineArn=TestIngestWorkflows.orca_copy_to_glacier_step_function_arn,
            input=json.dumps(copy_to_glacier_input, indent=4),
        )

        step_function_results = helpers.get_state_machine_execution_results(
            execution_info["executionArn"]
        )

        self.assertEqual("SUCCEEDED", step_function_results["status"])
        self.assertEqual(expected_output, json.loads(step_function_results["output"]))

        catalog_output = helpers.post_to_api(
            TestIngestWorkflows.MY_SESSION,
            TestIngestWorkflows.API_URL + "/catalog/reconcile/",
            data=json.dumps(
                {
                    "pageIndex": 0,
                    "providerId": [provider_id],
                    "endTimestamp": int((time.time() + 5) * 1000),
                }
            ),
            headers={"Host": TestIngestWorkflows.AWS_API_NAME},
        )
        self.assertEqual(200, catalog_output.status_code)
        self.assertEqual({"granules": [], "anotherPage": False}, catalog_output.json())
