"""
Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.
"""
import boto3
import json
from moto import mock_sqs
import shared_recovery
import unittest

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

    def test_post_entry_to_queue(self):
        """
        Test that sending a message to SQS queue using post_entry_to_queue() function returns the same expected message.
        """
        table_name = "unit_test_table"
        request_method = shared_recovery.RequestMethod.NEW
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"name": "unit_test"}
        body = json.dumps(new_data)
        # based on 'table_name + request_method.value + body', it should be 'unit_test_tablepost{"name": "unit_test"}
        MessageDeduplicationId = table_name + request_method.value + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }
        shared_recovery.post_entry_to_queue(
            table_name, new_data, request_method, db_queue_url
        )

        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        self.assertEqual(queue_contents[0].body, json.dumps(new_data))
        self.assertEqual(queue_contents[0].attributes['MessageDeduplicationId'], MessageDeduplicationId)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
        
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_optional_none(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        The optional variables are all set to None.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        last_update ='2020-07-17T17:36:38.494918'
        status_id = shared_recovery.OrcaStatus.PENDING
        request_method = shared_recovery.RequestMethod.NEW
        key_path= None
        restore_destination = None
        error_message = None
        request_time = None
        completion_time = None
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update, "status_id": status_id.value}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        response = shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,
            request_time,last_update,completion_time,request_method,db_queue_url
            )
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )
        self.assertEqual(queue_contents[0].body, json.dumps(new_data))
        self.assertEqual(queue_contents[0].attributes['MessageDeduplicationId'], MessageDeduplicationId)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_file_to_queue_no_null(self):
        """
        Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
        The optional variables are all set to non-null values.
        """
        table_name = 'orca_recoverfile'
        request_method = shared_recovery.RequestMethod.NEW
        job_id= '1234'
        granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
        filename= 'f1.doc'
        status_id = shared_recovery.OrcaStatus.SUCCESS
        request_method = shared_recovery.RequestMethod.NEW
        key_path= key_path= 's3://dev-usgs'
        restore_destination = 'dev-usgs-bucket'
        error_message = 'Access Denied'
        request_time = '2019-07-17T17:36:38.494918'
        last_update = '2020-07-17T17:36:38.494918'
        completion_time = '2019-07-18T17:36:38.494918'
        db_queue_url = self.queue.url
        #this is the expected message body that should be received
        new_data = {"job_id": job_id, "granule_id": granule_id, "filename": filename, "last_update": last_update, "status_id": status_id.value,
                    "key_path": key_path, "restore_destination": restore_destination, "error_message": error_message, 
                    "request_time": request_time, "completion_time": completion_time}
        body = json.dumps(new_data)
        MessageDeduplicationId = table_name + request_method.value + body
        MessageAttributes={
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

        shared_recovery.post_status_for_file_to_queue(
            job_id,granule_id,filename,key_path,restore_destination,status_id,error_message,request_time,last_update,completion_time,request_method,db_queue_url)
        #grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )

        self.assertEqual(queue_contents[0].body, json.dumps(new_data))
        self.assertEqual(queue_contents[0].attributes['MessageDeduplicationId'], MessageDeduplicationId)
        self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
        self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_all_null(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            The optional variables are all set to None.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.PENDING
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = None
            request_time = None
            completion_time = None
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id}
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
                request_time,completion_time,archive_destination,request_method,db_queue_url
                )
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )

            self.assertEqual(queue_contents[0].body, json.dumps(new_data))
            self.assertEqual(queue_contents[0].attributes['MessageDeduplicationId'], MessageDeduplicationId)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# ---------------------------------------------------------------------------------------------------------------------------------

    def test_post_status_for_job_to_queue_no_null(self):
            """
            Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
            The optional variables are all set to non-nullable values.
            """
            table_name = 'orca_recoveryjob'
            request_method = shared_recovery.RequestMethod.NEW
            job_id= '1234'
            granule_id= '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
            status_id = shared_recovery.OrcaStatus.SUCCESS
            request_method = shared_recovery.RequestMethod.NEW
            archive_destination = 'archive-destination'
            request_time = '2019-07-17T17:36:38.494918'
            completion_time = '2019-07-18T17:36:38.494918'
            db_queue_url = self.queue.url
            #this is the expected message body that should be received
            new_data = {"job_id": job_id, "granule_id": granule_id, "request_time": request_time, 
                        "completion_time": completion_time, "archive_destination": archive_destination }
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
                request_time,completion_time,archive_destination,request_method,db_queue_url
                )
            #grabbing queue contents after the message is sent
            queue_contents = self.queue.receive_messages(
                            MessageAttributeNames= ["All"]
                            )

            self.assertEqual(queue_contents[0].body, json.dumps(new_data))
            self.assertEqual(queue_contents[0].attributes['MessageDeduplicationId'], MessageDeduplicationId)
            self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
            self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

if __name__ == "__main":
    unittest.main()