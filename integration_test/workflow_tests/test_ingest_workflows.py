import json
import os
import time
import uuid
from unittest import TestCase

import boto3

import helpers


class TestIngestWorkflows(TestCase):
    storage_bucket_name = None
    aws_region = None
    orca_api_deployment_invoke_url = None
    orca_copy_to_glacier_step_function_arn = None

    def setUp(self) -> None:
        os.environ["bamboo_STORAGE_BUCKET_NAME"] = "todo"
        os.environ["bamboo_AWS_DEFAULT_REGION"] = "us-west-2"
        os.environ["orca_API_DEPLOYMENT_INVOKE_URL"] = "https://s2jmh2r60k.execute-api.us-west-2.amazonaws.com/orca"  # todo: check format for this compared to tf output
        os.environ[
            "orca_COPY_TO_GLACIER_STEP_FUNCTION_ARN"
        ] = "arn:aws:states:us-west-2:236859827343:stateMachine:doctest-OrcaCopyToGlacierWorkflow"

        TestIngestWorkflows.storage_bucket_name = os.environ[
            "bamboo_STORAGE_BUCKET_NAME"
        ]
        TestIngestWorkflows.aws_region = os.environ["bamboo_AWS_DEFAULT_REGION"]
        TestIngestWorkflows.orca_api_deployment_invoke_url = os.environ[
            "orca_API_DEPLOYMENT_INVOKE_URL"
        ]
        TestIngestWorkflows.orca_copy_to_glacier_step_function_arn = os.environ[
            "orca_COPY_TO_GLACIER_STEP_FUNCTION_ARN"
        ]

    def test_ingest_no_granules_passes(self):
        # todo: remember to check all these properties
        provider_id = uuid.uuid4().__str__()
        provider_name = uuid.uuid4().__str__()

        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()

        execution_id = uuid.uuid4().__str__()

        # todo: remove the fluff, and use copy_to_glacier_input as needed
        expected_output = {
            "payload": {"granules": [], "copied_to_glacier": []},
            "meta": {
                "collection": {
                    "name": collection_name,
                    "version": collection_version
                },
                "provider": {
                    "id": provider_id,
                    "name": provider_name
                }
            },
            "cumulus_meta": {
                "execution_name": execution_id
            },
            "task_config": {
                "excludeFileTypes": "{$.meta.collection.meta.excludeFileTypes}",
                "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
                "providerId": "{$.meta.provider.id}", "providerName": "{$.meta.provider.name}",
                "executionId": "{$.cumulus_meta.execution_name}",
                "collectionShortname": "{$.meta.collection.name}",
                "collectionVersion": "{$.meta.collection.version}",
                "orcaDefaultBucketOverride": "{$.meta.collection.meta.orcaDefaultBucketOverride}",
                "orcaDefaultStorageClassOverride": "{$.meta.collection.meta.orcaDefaultStorageClassOverride}"
            },
            "exception": "None"}

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
            "cumulus_meta": {
                "execution_name": execution_id
            }
        }

        execution_info = boto3.client("stepfunctions").start_execution(
            stateMachineArn=TestIngestWorkflows.orca_copy_to_glacier_step_function_arn,
            input=json.dumps(copy_to_glacier_input, indent=4),
        )

        print(f"Step function execution info: {execution_info}")

        step_function_results = helpers.get_state_machine_execution_results(execution_info["executionArn"])
        print(f"Step function results: {step_function_results}")
        print(f"Step function output: {step_function_results['output']}")

        self.assertEqual("SUCCEEDED", step_function_results["status"])
        self.assertEqual(expected_output, json.loads(step_function_results["output"]))

        catalog_output = helpers.post_to_api(TestIngestWorkflows.orca_api_deployment_invoke_url + "/catalog/reconcile/", {
            "pageIndex": 0,
            "providerId": [provider_id],
            "endTimestamp": int((time.time() + 5) * 1000)  # todo: untested
        })

        # todo: Make sure catalog_output is empty
