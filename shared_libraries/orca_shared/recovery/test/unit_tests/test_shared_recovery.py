"""
Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.
"""
import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import boto3
from moto import mock_sqs

from orca_shared.recovery import shared_recovery


class TestSharedRecoveryLibraries(unittest.TestCase):
    """
    Unit tests for the shared_recovery library used by ORCA Recovery Lambdas.
    """

    # Create the mock for unit tests
    mock_sqs = mock_sqs()

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.queue = self.test_sqs.create_queue(QueueName="unit-test-queue")
        self.db_queue_url = self.queue.url
        self.request_methods = [
            shared_recovery.RequestMethod.NEW_JOB,
            shared_recovery.RequestMethod.UPDATE_FILE,
        ]
        self.statuses = [
            shared_recovery.OrcaStatus.PENDING,
            shared_recovery.OrcaStatus.STAGED,
            shared_recovery.OrcaStatus.SUCCESS,
            shared_recovery.OrcaStatus.FAILED,
        ]
        self.job_id = "1234"
        self.granule_id = "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250"
        self.MessageGroupId = "request_files"

    def tearDown(self):
        """
        Perform teardown for the tests
        """
        self.mock_sqs.stop()

    @patch.dict(
        os.environ,
        {"AWS_REGION": "us-west-2"},
        clear=True,
    )
    def test_post_entry_to_queue_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_entry_to_queue()
        function returns the same expected message.
        """
        new_data = {"name": "test"}
        for request_method in self.request_methods:
            # Run subtests
            with self.subTest(request_method=request_method):
                # Send values to the function
                shared_recovery.post_entry_to_queue(
                    new_data, request_method, self.db_queue_url
                )

                # grabbing queue contents after the message is sent
                queue_contents = self.queue.receive_messages(
                    MessageAttributeNames=["All"]
                )
                queue_output_body = json.loads(queue_contents[0].body)

                # Testing SQS body
                self.assertEqual(queue_output_body, new_data)

    @patch.dict(
        os.environ,
        {"AWS_REGION": "us-west-2"},
        clear=True,
    )
    def test_create_status_for_job_no_errors(self):
        """
        *Happy Path*
        Tests that messages are correctly constructed by function and sent to
        the queue based on RequestMethod and Status values.
        """
        # Setting other variables unique to this test
        archive_destination = "s3://archive-bucket"

        # Run subtests
        with self.subTest(request_method=shared_recovery.RequestMethod.NEW_JOB):
            # Send values to the function
            shared_recovery.create_status_for_job(
                self.job_id, self.granule_id, archive_destination, [], self.db_queue_url
            )

            # grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages()
            queue_output_body = json.loads(queue_contents[0].body)

            # Testing required fields
            self.assertEqual(queue_output_body[shared_recovery.JOB_ID_KEY], self.job_id)
            self.assertEqual(queue_output_body[shared_recovery.GRANULE_ID_KEY], self.granule_id)

            # Testing optional fields
            self.assertIn(shared_recovery.REQUEST_TIME_KEY, queue_output_body)
            # Get the request time
            new_request_time = datetime.fromisoformat(queue_output_body[shared_recovery.REQUEST_TIME_KEY])
            self.assertEqual(new_request_time.tzinfo, timezone.utc)
            self.assertEqual(
                queue_output_body[shared_recovery.ARCHIVE_DESTINATION_KEY],
                archive_destination,
            )

    @patch.dict(
        os.environ,
        {"AWS_REGION": "us-west-2"},
        clear=True,
    )
    def test_update_status_for_file_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_status_for_file
        function returns the same expected message.
        """
        for status_id in self.statuses:
            # Setting other variables unique to this test
            error_message = "Access denied"
            filename = "f1.doc"

            # Run subtests
            with self.subTest(
                request_method=shared_recovery.RequestMethod.UPDATE_FILE,
                status_id=status_id,
            ):

                # Send values to the function
                shared_recovery.update_status_for_file(
                    self.job_id,
                    self.granule_id,
                    filename,
                    status_id,
                    error_message,
                    self.db_queue_url,
                )

                # grabbing queue contents after the message is sent
                queue_contents = self.queue.receive_messages()
                queue_output_body = json.loads(queue_contents[0].body)

                # Testing required fields
                self.assertEqual(queue_output_body[shared_recovery.JOB_ID_KEY], self.job_id)
                self.assertEqual(queue_output_body[shared_recovery.GRANULE_ID_KEY], self.granule_id)
                self.assertEqual(queue_output_body[shared_recovery.STATUS_ID_KEY], status_id.value)
                self.assertEqual(queue_output_body[shared_recovery.FILENAME_KEY], filename)
                self.assertNotIn(shared_recovery.REQUEST_TIME_KEY, queue_output_body)
                self.assertNotIn(shared_recovery.RESTORE_DESTINATION_KEY, queue_output_body)
                self.assertNotIn(shared_recovery.KEY_PATH_KEY, queue_output_body)

                # Testing fields based on status_id
                completion_status = [
                    shared_recovery.OrcaStatus.SUCCESS,
                    shared_recovery.OrcaStatus.FAILED,
                ]

                if status_id in completion_status:
                    self.assertIn(shared_recovery.COMPLETION_TIME_KEY, queue_output_body)
                    new_completion_time = datetime.fromisoformat(
                        queue_output_body[shared_recovery.COMPLETION_TIME_KEY]
                    )
                    self.assertEqual(new_completion_time.tzinfo, timezone.utc)
                else:
                    self.assertNotIn(shared_recovery.COMPLETION_TIME_KEY, queue_output_body)
                if status_id == shared_recovery.OrcaStatus.FAILED:
                    self.assertEqual(queue_output_body[shared_recovery.ERROR_MESSAGE_KEY], error_message)
                else:
                    self.assertNotIn(shared_recovery.ERROR_MESSAGE_KEY, queue_output_body)

    def test_update_status_for_file_raise_errors_error_message(self):
        """
        Tests that update_status_for_file will raise a ValueError
        if the error_message is either empty or None in case of status_id as FAILED.
        request_method is set as NEW since the logics only apply for it.
        """
        filename = "f1.doc"
        # setting status_id as FAILED since error_message only shows up for failed status.
        status_id = shared_recovery.OrcaStatus.FAILED

        for error_message in [None, ""]:
            # will pass if it raises a ValueError which is expected in this case
            self.assertRaises(
                ValueError,
                shared_recovery.update_status_for_file,
                self.job_id,
                self.granule_id,
                filename,
                status_id,
                error_message,
                self.db_queue_url,
            )
