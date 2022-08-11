import json
import time
import uuid
from unittest import TestCase

import boto3

import helpers


class TestNoGranules(TestCase):
    def test_no_granules_passes(self):
        """
        If no granules are provided, should not store anything in DB.
        """
        # Set up Orca API resources
        # ---
        my_session = helpers.create_session()

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
            stateMachineArn=helpers.orca_copy_to_glacier_step_function_arn,
            input=json.dumps(copy_to_glacier_input, indent=4),
        )

        step_function_results = helpers.get_state_machine_execution_results(
            execution_info["executionArn"]
        )

        self.assertEqual("SUCCEEDED", step_function_results["status"],
                         "Error occurred while starting step function.")
        self.assertEqual(expected_output, json.loads(step_function_results["output"]),
                         "Expected step function output not returned.")

        catalog_output = helpers.post_to_api(
            my_session,
            helpers.api_url + "/catalog/reconcile/",
            data=json.dumps(
                {
                    "pageIndex": 0,
                    "providerId": [provider_id],
                    "endTimestamp": int((time.time() + 5) * 1000),
                }
            ),
            headers={"Host": helpers.aws_api_name},
        )
        self.assertEqual(200, catalog_output.status_code,
                         "Error occurred while contacting API.")
        self.assertEqual({"granules": [], "anotherPage": False}, catalog_output.json(),
                         "Expected empty granule list not returned.")
