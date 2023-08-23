import json
import unittest

# Set the logger
from unittest import mock

import helpers
from custom_logger import CustomLoggerAdapter
from helpers import read_recovery_request_record
from test_packages.ingest.test_multiple_granules_happy_path import \
    recovery_request_record_happy_path_filename

logger = CustomLoggerAdapter.set_logger(__name__)


class TestRecoveryValidationHappyPath(unittest.TestCase):
    def test_recovery_validation_happy_path(self):
        self.maxDiff = None
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()

            recovery_request_record = \
                read_recovery_request_record(recovery_request_record_happy_path_filename)

            job_status_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/recovery/jobs/",
                data=json.dumps(
                    {
                        "asyncOperationId": recovery_request_record.async_operation_id
                    }
                ),
                headers={"Host": helpers.aws_api_name},
            )
            self.assertEqual(
                200, job_status_output.status_code,
                f"Error occurred while contacting job status API: {job_status_output.content}"
            )
            expected_output = {
                "asyncOperationId": "91e2bb79-577b-4cc4-8a24-8f0161252742",
                "jobStatusTotals": {
                    "pending": 0, "staged": 0, "error": 0,
                    "success": len(recovery_request_record.granules)
                },
                "granules": [{
                    "collectionId": granule.collection_id,
                    "granuleId": granule.granule_id,
                    "status": "success"  # todo: Could adapt this to allow for errored files.
                } for granule in recovery_request_record.granules],
            }
            job_status_output_json = job_status_output.json()
            self.assertEqual(
                expected_output,
                job_status_output_json,
                "Expected job status not returned.",
            )

            for granule in recovery_request_record.granules:
                granule_status_output = helpers.post_to_api(
                    my_session,
                    helpers.api_url + "/recovery/granules/",
                    data=json.dumps(
                        {
                            "asyncOperationId": recovery_request_record.async_operation_id,
                            "collectionId": granule.collection_id,
                            "granuleId": granule.granule_id,
                        }
                    ),
                    headers={"Host": helpers.aws_api_name},
                )
                self.assertEqual(
                    200, granule_status_output.status_code,
                    f"Error occurred while contacting granule status API: "
                    f"{granule_status_output.content}"
                )

                expected_output = {
                    "collectionId": granule.collection_id,
                    "granuleId": granule.granule_id,
                    "asyncOperationId": recovery_request_record.async_operation_id,
                    "requestTime": mock.ANY, "completionTime": mock.ANY,
                    "files": [{
                        "fileName": file.file_name,
                        "restoreDestination": file.target_bucket_name,
                        "status": "success",
                    } for file in granule.files],
                }
                granule_status_output_json = granule_status_output.json()
                self.assertEqual(
                    expected_output,
                    granule_status_output_json,
                    "Expected granule status not returned.",
                )
        except Exception as ex:
            logger.error(ex)
            raise
