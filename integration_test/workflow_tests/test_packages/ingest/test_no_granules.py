import json
import time
import uuid
from unittest import TestCase

import boto3

import helpers
from custom_logger import CustomLoggerAdapter

# Set the logger
logger = CustomLoggerAdapter.set_logger(__name__)


class TestNoGranules(TestCase):
    def test_no_granules_passes(self):
        self.maxDiff = None
        """
        If no granules are provided, should not store anything in DB.
        """
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()

            provider_id = uuid.uuid4().__str__()
            provider_name = uuid.uuid4().__str__()

            collection_name = uuid.uuid4().__str__()
            collection_version = uuid.uuid4().__str__()

            execution_id = uuid.uuid4().__str__()

            # note that this does not cover all available properties
            copy_to_archive_input = {
                "payload": {"granules": []},
                "meta": {
                    "collection": {
                        "name": collection_name,
                        "version": collection_version,
                    },
                    "provider": {
                        "id": provider_id,
                        "name": provider_name,
                    },
                },
                "cumulus_meta": {"execution_name": execution_id},
            }

            expected_output = {
                "granules": [], "copied_to_orca": []
            }

            execution_info = boto3.client("stepfunctions").start_execution(
                stateMachineArn=helpers.orca_copy_to_archive_step_function_arn,
                input=json.dumps(copy_to_archive_input, indent=4),
            )

            step_function_results = helpers.get_state_machine_execution_results(
                execution_info["executionArn"],
                maximum_duration_seconds=30,
            )

            self.assertEqual(
                "SUCCEEDED",
                step_function_results["status"],
                "Error occurred while starting step function.",
            )
            self.assertEqual(
                expected_output,
                json.loads(step_function_results["output"]),
                "Expected step function output not returned.",
            )

            # Let the catalog update
            time.sleep(10)
            catalog_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/catalog/reconcile/",
                data=json.dumps(
                    {
                        "pageIndex": 0,
                        "collectionId": [collection_name + "___" + collection_version],
                        "providerId": [provider_id],
                        "endTimestamp": int((time.time() + 5) * 1000),
                    }
                ),
                headers={"Host": helpers.aws_api_name},
            )
            self.assertEqual(
                200, catalog_output.status_code, f"Error occurred while contacting API: "
                                                 f"{catalog_output.content}"
            )
            self.assertEqual(
                {"granules": [], "anotherPage": False},
                catalog_output.json(),
                "Expected empty granule list not returned.",
            )
        except Exception as ex:
            logger.error(ex)
            raise
