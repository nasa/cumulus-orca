"""
Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.
"""
import random

import boto3
import json
from moto import mock_sqs
import shared_recovery
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import os


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
        {
            "AWS_REGION": "us-west-2"
        },
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
            # Setting the message attribute values to what we expect.
            # noinspection PyPep8Naming
            MessageAttributes = {
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                }
            }

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

                # Testing Message attribute information
                self.assertEqual(
                    queue_contents[0].attributes["MessageGroupId"], self.MessageGroupId
                )
                self.assertEqual(
                    queue_contents[0].message_attributes, MessageAttributes
                )

                # Testing SQS body
                self.assertEqual(queue_output_body, new_data)

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2"
        },
        clear=True,
    )
    def test_create_status_for_job_no_errors(self):
        """
        *Happy Path*
        Tests that messages are correctly constructed by function and sent to
        the queue based on RequestMethod and Status values.
        """
        # Setting the message attribute values to what we expect.
        # noinspection PyPep8Naming
        MessageAttributes = {
            "RequestMethod": {
                "DataType": "String",
                "StringValue": shared_recovery.RequestMethod.NEW_JOB.value,
            }
        }

        # Setting other variables unique to this test
        archive_destination = "s3://archive-bucket"

        # Run subtests
        with self.subTest(request_method=shared_recovery.RequestMethod.NEW_JOB):
            # Send values to the function
            shared_recovery.create_status_for_job(
                self.job_id,
                self.granule_id,
                archive_destination,
                [],
                self.db_queue_url
            )

            # grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                MessageAttributeNames=["All"]
            )
            queue_output_body = json.loads(queue_contents[0].body)

            # Testing Message attribute information
            self.assertEqual(
                queue_contents[0].attributes["MessageGroupId"],
                self.MessageGroupId,
            )
            self.assertEqual(
                queue_contents[0].message_attributes, MessageAttributes
            )

            # Testing required fields
            self.assertEqual(queue_output_body["job_id"], self.job_id)
            self.assertEqual(queue_output_body["granule_id"], self.granule_id)

            # Testing optional fields
            self.assertIn("request_time", queue_output_body)
            # Get the request time
            new_request_time = datetime.fromisoformat(
                queue_output_body["request_time"]
            )
            self.assertEqual(new_request_time.tzinfo, timezone.utc)
            self.assertEqual(
                queue_output_body["archive_destination"],
                archive_destination,
            )

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2"
        },
        clear=True,
    )
    def test_update_status_for_file_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_status_for_file
        function returns the same expected message.
        """
        for status_id in self.statuses:
            # Setting the message attribute values to what we expect.
            # noinspection PyPep8Naming
            MessageAttributes = {
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": shared_recovery.RequestMethod.UPDATE_FILE.value,
                }
            }

            # Setting other variables unique to this test
            error_message = "Access denied"
            filename = "f1.doc"

            # Run subtests
            with self.subTest(request_method=shared_recovery.RequestMethod.UPDATE_FILE, status_id=status_id):

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
                queue_contents = self.queue.receive_messages(
                    MessageAttributeNames=["All"]
                )
                queue_output_body = json.loads(queue_contents[0].body)

                # Testing Message attribute information
                self.assertEqual(
                    queue_contents[0].attributes["MessageGroupId"],
                    self.MessageGroupId,
                )
                self.assertEqual(
                    queue_contents[0].message_attributes, MessageAttributes
                )

                # Testing required fields
                self.assertEqual(queue_output_body["job_id"], self.job_id)
                self.assertEqual(queue_output_body["granule_id"], self.granule_id)
                self.assertEqual(queue_output_body["status_id"], status_id.value)
                self.assertEqual(queue_output_body["filename"], filename)
                self.assertNotIn("request_time", queue_output_body)
                self.assertNotIn("restore_destination", queue_output_body)
                self.assertNotIn("key_path", queue_output_body)

                # Testing fields based on status_id
                completion_status = [
                    shared_recovery.OrcaStatus.SUCCESS,
                    shared_recovery.OrcaStatus.FAILED,
                ]

                if status_id in completion_status:
                    self.assertIn("completion_time", queue_output_body)
                    new_completion_time = datetime.fromisoformat(
                        queue_output_body["completion_time"]
                    )
                    self.assertEqual(new_completion_time.tzinfo, timezone.utc)
                else:
                    self.assertNotIn("completion_time", queue_output_body)
                if status_id == shared_recovery.OrcaStatus.FAILED:
                    self.assertEqual(
                        queue_output_body["error_message"], error_message
                    )
                else:
                    self.assertNotIn("error_message", queue_output_body)

    # Other non-happy tests go here for things that should raise exceptions
    def test_create_status_for_job_raise_errors(self):
        """
        Tests that create_status_for_job will raise an exception if the archive_destination is either None or empty.
        request_method is set as NEW since the logics only apply for it.
        """
        request_method = shared_recovery.RequestMethod.NEW_JOB

        for archive_destination in [None, ""]:
            for status_id in self.statuses:
                # Run subtests
                with self.subTest(
                        status_id=status_id, archive_destination=archive_destination
                ):
                    # will pass if it raises an exception which is expected in this case
                    self.assertRaises(
                        Exception,
                        shared_recovery.create_status_for_job,
                        self.job_id,
                        self.granule_id,
                        status_id,
                        archive_destination,
                        request_method.value,
                        self.db_queue_url,
                        random.uniform(0, 1000)
                    )

    def test_update_status_for_file_raise_errors_restore_destination(self):
        """
        Tests that update_status_for_file will raise an exception if the restore_destination is either None or empty.
        request_method is set as NEW since the logics only apply for it.
        """
        filename = "f1.doc"
        request_method = shared_recovery.RequestMethod.NEW_JOB
        error_message = "error"
        key_path = "path/"

        for restore_destination in [None, ""]:
            for status_id in self.statuses:
                # Run subtests
                with self.subTest(
                        restore_destination=restore_destination, status_id=status_id
                ):
                    # will pass if it raises an exception which is expected in this case
                    self.assertRaises(
                        Exception,
                        shared_recovery.update_status_for_file,
                        self.job_id,
                        self.granule_id,
                        filename,
                        key_path,
                        restore_destination,
                        status_id,
                        error_message,
                        request_method.value,
                        self.db_queue_url,
                    )

    def test_update_status_for_file_raise_errors_key_path(self):
        """
        Tests that the function update_status_for_file will raise an exception if the key_path is either None or empty.
        request_method is set as NEW since the logics only apply for it.
        """
        filename = "f1.doc"
        request_method = shared_recovery.RequestMethod.NEW_JOB
        error_message = "error"
        restore_destination = "s3://restore-bucket"

        for key_path in [None, ""]:
            for status_id in self.statuses:
                # Run subtests
                with self.subTest(key_path=key_path, status_id=status_id):
                    # will pass if it raises an exception which is expected in this case
                    self.assertRaises(
                        Exception,
                        shared_recovery.update_status_for_file,
                        self.job_id,
                        self.granule_id,
                        filename,
                        key_path,
                        restore_destination,
                        status_id,
                        error_message,
                        request_method.value,
                        self.db_queue_url,
                    )

    def test_update_status_for_file_raise_errors_error_message(self):
        """
        Tests that update_status_for_file will raise an exception
        if the error_message is either empty or None in case of status_id as FAILED.
        request_method is set as NEW since the logics only apply for it.
        """
        filename = "f1.doc"
        request_method = shared_recovery.RequestMethod.NEW_JOB
        restore_destination = "s3://restore-bucket"
        key_path = "path/"
        # setting status_id as FAILED since error_message only shows up for failed status.
        status_id = shared_recovery.OrcaStatus.FAILED

        for error_message in [None, ""]:
            # will pass if it raises an exception which is expected in this case
            self.assertRaises(
                Exception,
                shared_recovery.update_status_for_file,
                self.job_id,
                self.granule_id,
                filename,
                key_path,
                restore_destination,
                status_id,
                error_message,
                request_method.value,
                self.db_queue_url,
            )
