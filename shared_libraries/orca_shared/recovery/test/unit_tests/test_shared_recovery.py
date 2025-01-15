"""
Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.
"""

import json
import os
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock
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
        self.standard_queue = self.test_sqs.create_queue(QueueName="standard-queue")
        self.standard_queue_url = self.standard_queue.url
        self.fifo_queue = self.test_sqs.create_queue(
            QueueName="fifo-queue.fifo", Attributes={"FifoQueue": "true"}
        )
        self.fifo_queue_url = self.fifo_queue.url
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

    def test_post_entry_to_fifo_queue_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_entry_to_fifo_queue()
        function returns the same expected message.
        """
        new_data = {"name": "test"}
        for request_method in self.request_methods:
            # Run subtests
            with self.subTest(request_method=request_method):
                # Send values to the function
                shared_recovery.post_entry_to_fifo_queue(
                    new_data, request_method, self.fifo_queue_url
                )

                # grabbing queue contents after the message is sent
                queue_contents = self.fifo_queue.receive_messages(
                    MessageAttributeNames=["All"]
                )
                queue_output_body = json.loads(queue_contents[0].body)

                # Testing SQS body
                self.assertEqual(queue_output_body, new_data)
                self.assertEqual(
                    request_method.value,
                    queue_contents[0].message_attributes["RequestMethod"][
                        "StringValue"
                    ],
                )
                # Delete the message from the FIFO queue to show we have read it before looping
                self.fifo_queue.delete_messages(
                    Entries=[
                        {
                            "ReceiptHandle": queue_contents[0].receipt_handle,
                            "Id": queue_contents[0].message_id,
                        }
                    ]
                )
                # Verifies that request_method is set properly to new_job or update_file
                self.assertTrue(
                    request_method.value == "new_job"
                    or request_method.value == "update_file",
                    f"Incorrect Request Method: {request_method.value}",
                )

    @patch.dict(
        os.environ,
        {"AWS_REGION": "us-west-2"},
        clear=True,
    )
    def test_post_entry_to_standard_queue_happy_path(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_entry_to_standard_queue()
        function returns the same expected message.
        """
        new_data = {"name": "test"}

        shared_recovery.post_entry_to_standard_queue(new_data, self.standard_queue_url)

        # grabbing queue contents after the message is sent
        queue_contents = self.standard_queue.receive_messages(
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
        collection_id = uuid.uuid4().__str__()
        archive_destination = "s3://archive-bucket"

        file = {uuid.uuid4().__str__(): uuid.uuid4().__str__()}
        # Send values to the function
        shared_recovery.create_status_for_job(
            self.job_id,
            collection_id,
            self.granule_id,
            archive_destination,
            [file],
            self.fifo_queue_url,
        )

        # grabbing queue contents after the message is sent
        queue_contents = self.fifo_queue.receive_messages()
        queue_output_body = json.loads(queue_contents[0].body)

        # Testing required fields
        self.assertEqual(
            {
                shared_recovery.JOB_ID_KEY: self.job_id,
                shared_recovery.COLLECTION_ID_KEY: collection_id,
                shared_recovery.FILES_KEY: [file],
                shared_recovery.GRANULE_ID_KEY: self.granule_id,
                shared_recovery.REQUEST_TIME_KEY: mock.ANY,
                shared_recovery.ARCHIVE_DESTINATION_KEY: archive_destination,
            },
            queue_output_body,
        )

        # Get the request time
        new_request_time = datetime.fromisoformat(
            queue_output_body[shared_recovery.REQUEST_TIME_KEY]
        )
        self.assertEqual(timezone.utc, new_request_time.tzinfo)

    def test_update_status_for_file_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_status_for_file
        function returns the same expected message.
        """
        for status_id in self.statuses:
            # Setting other variables unique to this test
            collection_id = uuid.uuid4().__str__()
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
                    collection_id,
                    self.granule_id,
                    filename,
                    status_id,
                    error_message,
                    self.fifo_queue_url,
                )

                # grabbing queue contents after the message is sent
                queue_contents = self.fifo_queue.receive_messages()
                queue_output_body = json.loads(queue_contents[0].body)
                # Testing required fields
                self.assertEqual(
                    queue_output_body[shared_recovery.JOB_ID_KEY], self.job_id
                )
                self.assertEqual(
                    collection_id, queue_output_body[shared_recovery.COLLECTION_ID_KEY]
                )
                self.assertEqual(
                    self.granule_id, queue_output_body[shared_recovery.GRANULE_ID_KEY]
                )
                self.assertEqual(
                    status_id.value, queue_output_body[shared_recovery.STATUS_ID_KEY]
                )
                self.assertEqual(
                    filename, queue_output_body[shared_recovery.FILENAME_KEY]
                )
                self.assertNotIn(shared_recovery.REQUEST_TIME_KEY, queue_output_body)
                self.assertNotIn(
                    shared_recovery.RESTORE_DESTINATION_KEY, queue_output_body
                )
                self.assertNotIn(shared_recovery.KEY_PATH_KEY, queue_output_body)

                # Testing fields based on status_id
                completion_status = [
                    shared_recovery.OrcaStatus.SUCCESS,
                    shared_recovery.OrcaStatus.FAILED,
                ]

                if status_id in completion_status:
                    self.assertIn(
                        shared_recovery.COMPLETION_TIME_KEY, queue_output_body
                    )
                    new_completion_time = datetime.fromisoformat(
                        queue_output_body[shared_recovery.COMPLETION_TIME_KEY]
                    )
                    self.assertEqual(timezone.utc, new_completion_time.tzinfo)
                else:
                    self.assertNotIn(
                        shared_recovery.COMPLETION_TIME_KEY, queue_output_body
                    )
                if status_id == shared_recovery.OrcaStatus.FAILED:
                    self.assertEqual(
                        error_message,
                        queue_output_body[shared_recovery.ERROR_MESSAGE_KEY],
                    )
                else:
                    self.assertNotIn(
                        shared_recovery.ERROR_MESSAGE_KEY, queue_output_body
                    )
                # Delete the message from the FIFO queue to show we have read it before looping
                self.fifo_queue.delete_messages(
                    Entries=[
                        {
                            "ReceiptHandle": queue_contents[0].receipt_handle,
                            "Id": queue_contents[0].message_id,
                        }
                    ]
                )

    def test_update_status_for_file_error_message_empty_raises_error_message(self):
        """
        Tests that update_status_for_file will raise a ValueError
        if the error_message is either empty or None in case of status_id as FAILED.
        request_method is set as NEW since the logics only apply for it.
        """
        # setting status_id as FAILED since error_message only shows up for failed status.
        status_id = shared_recovery.OrcaStatus.FAILED

        for error_message in [None, ""]:
            # will pass if it raises a ValueError which is expected in this case
            with self.assertRaises(ValueError) as cm:
                shared_recovery.update_status_for_file(
                    uuid.uuid4().__str__(),
                    uuid.uuid4().__str__(),
                    uuid.uuid4().__str__(),
                    uuid.uuid4().__str__(),
                    status_id,
                    error_message,
                    uuid.uuid4().__str__(),
                )
            self.assertEqual("Error message is required.", str(cm.exception))
