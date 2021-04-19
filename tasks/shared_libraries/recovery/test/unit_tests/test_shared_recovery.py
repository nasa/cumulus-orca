"""
Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.
"""
import boto3
import json
from moto import mock_sqs
import shared_recovery
import unittest
from datetime import datetime, timezone

class TestSharedRecoveryLibraries(unittest.TestCase):
    """
    Unit tests for the shared_recover library used by ORCA Recovery Lambdas.
    """

    # Create the mock for unit tests
    mock_sqs = mock_sqs()
    test_sqs = None
    queue = None
    db_queue_url = None
    MessageGroupId = None

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs")
        self.queue = self.test_sqs.create_queue(QueueName="unit-test-queue")
        self.db_queue_url = self.queue.url
        self.MessageGroupId = "request_files"

    def tearDown(self):
        """
        Perform teardown for the tests
        """
        self.mock_sqs.stop()
        
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_new_pending(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        This is for testing the case when request_method is NEW, ORCA status is PENDING.
        The new_data in this case should return request_time, key_path and restore_destination in addition to other values.
        Completion_time and error_message should not exist in the response received from SQS body.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        status_id = shared_recovery.OrcaStatus.PENDING
        key_path= key_path= 's3://dev-orca'
        restore_destination = 'restore-bucket'
        error_message = 'Access denied'
        request_time = datetime.now(timezone.utc).isoformat()
        last_update = datetime.now(timezone.utc).isoformat()
        completion_time = datetime.now(timezone.utc).isoformat()
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, 
                    "last_update": last_update, "status_id": status_id.value,"request_time": request_time, 
                    "key_path": key_path, "restore_destination": restore_destination}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value  + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,request_method,db_queue_url)
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        queue_output_body = json.loads(queue_contents[0].body)

        self.assertEqual(len(queue_output_body), len(new_data))
        self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
        self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
        self.assertEqual(queue_output_body["filename"], new_data["filename"])
        self.assertIn("last_update", queue_output_body)
        self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
        self.assertIn("request_time", queue_output_body) 
        self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
        self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
        self.assertNotIn(completion_time, queue_output_body)
        self.assertNotIn(error_message, queue_output_body)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_new_staged(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        This is for testing the case when request_method is NEW, ORCA status is STAGED.
        The new_data in this case should return request_time, key_path and restore_destination in addition to other values.
        Completion_time and error_message should not exist in the response received from SQS body.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        status_id = shared_recovery.OrcaStatus.STAGED
        key_path= key_path= 's3://dev-orca'
        restore_destination = 'restore-bucket'
        error_message = 'Access denied'
        request_time = datetime.now(timezone.utc).isoformat()
        last_update = datetime.now(timezone.utc).isoformat()
        completion_time = datetime.now(timezone.utc).isoformat()
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update, 
                    "status_id": status_id.value,"request_time": request_time, "key_path": key_path, 
                    "restore_destination": restore_destination}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value  + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,request_method,db_queue_url)
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        queue_output_body = json.loads(queue_contents[0].body)

        self.assertEqual(len(queue_output_body), len(new_data))
        self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
        self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
        self.assertEqual(queue_output_body["filename"], new_data["filename"])
        self.assertIn("last_update", queue_output_body)
        self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
        self.assertIn("request_time", queue_output_body) 
        self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
        self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
        self.assertNotIn(completion_time, queue_output_body)
        self.assertNotIn(error_message, queue_output_body)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_new_success(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        This is for testing the case when request_method is NEW, ORCA status is SUCCESS.
        The new_data should return request_time, key_path and restore_destination, completion_time in addition to other values.
        Error_message should not exist in the response received from SQS body.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        status_id = shared_recovery.OrcaStatus.SUCCESS
        key_path= key_path= 's3://dev-orca'
        restore_destination = 'restore-bucket'
        error_message = 'Access denied'
        request_time = datetime.now(timezone.utc).isoformat()
        last_update = datetime.now(timezone.utc).isoformat()
        completion_time = datetime.now(timezone.utc).isoformat()
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update, 
                    "status_id": status_id.value,"request_time": request_time, "key_path": key_path, 
                    "restore_destination": restore_destination, "completion_time": completion_time}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value  + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,request_method,db_queue_url)
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        queue_output_body = json.loads(queue_contents[0].body)
        self.assertEqual(len(queue_output_body), len(new_data))
        self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
        self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
        self.assertEqual(queue_output_body["filename"], new_data["filename"])
        self.assertIn("last_update", queue_output_body)
        self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
        self.assertIn("request_time", queue_output_body)
        self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
        self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
        self.assertIn("completion_time", queue_output_body)
        self.assertNotIn(error_message, queue_output_body)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_new_failed(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        This is for testing the case when request_method is NEW, ORCA status is FAILED.
        The new_data in this case should return request_time, key_path and restore_destination, completion_time, error_message in addition to other values.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        status_id = shared_recovery.OrcaStatus.FAILED
        key_path= key_path= 's3://dev-orca'
        restore_destination = 'restore-bucket'
        error_message = 'Access denied'
        request_time = datetime.now(timezone.utc).isoformat()
        last_update = datetime.now(timezone.utc).isoformat()
        completion_time = datetime.now(timezone.utc).isoformat()
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update, 
                    "status_id": status_id.value,"request_time": request_time, "key_path": key_path, 
                    "restore_destination": restore_destination, "completion_time": completion_time,
                    "error_message": error_message}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value  + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,request_method,db_queue_url)
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        queue_output_body = json.loads(queue_contents[0].body)

        self.assertEqual(len(queue_output_body), len(new_data))
        self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
        self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
        self.assertEqual(queue_output_body["filename"], new_data["filename"])
        self.assertIn("last_update", queue_output_body)
        self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
        self.assertIn("request_time", queue_output_body)
        self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
        self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
        self.assertIn("completion_time", queue_output_body)
        self.assertEqual(error_message, queue_output_body["error_message"])
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_new_pending(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            This is for testing the case when request_method is NEW, ORCA status is PENDING.
            The new_data in this case should return request_time, archive_destination in addition to other values.
            Completion_time should not exist in the response received from SQS body.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.PENDING
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = 'archive-bucket'
            request_time = datetime.now(timezone.utc).isoformat()
            completion_time = datetime.now(timezone.utc).isoformat()
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id, "status_id": status_id.value, 
                        "request_time": request_time, "archive_destination": archive_destination}
            body = json.dumps(new_data)
            MessageDeduplicationId = table_name + request_method.value + body
            MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

            shared_recovery.post_status_for_job_to_queue(job_id,granule_id,status_id,archive_destination,request_method,db_queue_url)
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
            queue_output_body = json.loads(queue_contents[0].body)

            self.assertEqual(len(queue_output_body), len(new_data))
            self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
            self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
            self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
            self.assertIn("request_time", queue_output_body)
            self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
            self.assertNotIn("completion_time", queue_output_body)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_new_staged(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            This is for testing the case when request_method is NEW, ORCA status is STAGED.
            The new_data in this case should return request_time, archive_destination in addition to other values.
            Completion_time should not exist in the response received from SQS body.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.STAGED
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = 'archive-bucket'
            request_time = datetime.now(timezone.utc).isoformat()
            completion_time = datetime.now(timezone.utc).isoformat()
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id, "status_id": status_id.value, 
                        "request_time": request_time, "archive_destination": archive_destination}
            body = json.dumps(new_data)
            MessageDeduplicationId = table_name + request_method.value + body
            MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

            shared_recovery.post_status_for_job_to_queue(
                job_id,granule_id,status_id,
               archive_destination,request_method,db_queue_url
                )
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
            queue_output_body = json.loads(queue_contents[0].body)

            self.assertEqual(len(queue_output_body), len(new_data))
            self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
            self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
            self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
            self.assertIn("request_time", queue_output_body)
            self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
            self.assertNotIn("completion_time", queue_output_body)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_new_success(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            This is for testing the case when request_method is NEW, ORCA status is SUCCESS.
            The new_data in this case should return request_time, archive_destination, completion_time in addition to other values.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.SUCCESS
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = 'archive-bucket'
            request_time = datetime.now(timezone.utc).isoformat()
            completion_time = datetime.now(timezone.utc).isoformat()
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id, "status_id": status_id.value, "request_time": request_time,
                        "archive_destination": archive_destination, "completion_time": completion_time}
            body = json.dumps(new_data)
            MessageDeduplicationId = table_name + request_method.value + body
            MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

            shared_recovery.post_status_for_job_to_queue(
                job_id,granule_id,status_id,
               archive_destination,request_method,db_queue_url
                )
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
            queue_output_body = json.loads(queue_contents[0].body)

            self.assertEqual(len(queue_output_body), len(new_data))
            self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
            self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
            self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
            self.assertIn("request_time", queue_output_body)
            self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
            self.assertIn("completion_time", queue_output_body)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_new_failed(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            This is for testing the case when request_method is NEW, ORCA status is FAILED.
            The new_data in this case should return request_time, archive_destination, completion_time in addition to other values.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.FAILED
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = 'archive-bucket'
            request_time = datetime.now(timezone.utc).isoformat()
            completion_time = datetime.now(timezone.utc).isoformat()
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id, "status_id": status_id.value, "request_time": request_time,
                        "archive_destination": archive_destination, "completion_time": completion_time}
            body = json.dumps(new_data)
            MessageDeduplicationId = table_name + request_method.value + body
            MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

            shared_recovery.post_status_for_job_to_queue(
                job_id,granule_id,status_id,
               archive_destination,request_method,db_queue_url
                )
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
            queue_output_body = json.loads(queue_contents[0].body)

            self.assertEqual(len(queue_output_body), len(new_data))
            self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
            self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
            self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
            self.assertIn("request_time", queue_output_body)
            self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
            self.assertIn("completion_time", queue_output_body)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

if __name__ == "__main":
    unittest.main()