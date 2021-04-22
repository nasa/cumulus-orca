# """
# Name: test_shared_recovery.py
# Description: Unit tests for shared_recovery.py shared library.
# """
# import boto3
# import json
# from moto import mock_sqs
# import shared_recovery
# import unittest
# from datetime import datetime, timezone

# class TestSharedRecoveryLibraries(unittest.TestCase):
#     """
#     Unit tests for the shared_recover library used by ORCA Recovery Lambdas.
#     """

#     # Create the mock for unit tests
#     mock_sqs = mock_sqs()
#     test_sqs = None
#     queue = None
#     db_queue_url = None
#     MessageGroupId = None
#     job_id = None
#     granule_id = None
#     filename = None
#     key_path = None
#     restore_destination = None
#     error_message = None
#     archive_destination = None

#     def setUp(self):
#         """
#         Perform initial setup for the tests.
#         """
#         self.mock_sqs.start()
#         self.test_sqs = boto3.resource("sqs")
#         self.queue = self.test_sqs.create_queue(QueueName="unit-test-queue")
#         self.db_queue_url = self.queue.url
#         self.MessageGroupId = 'request_files'
#         self.job_id = '1234'
#         self.granule_id = '6c8d0c8b-4f9a-4d87-ab7c-480b185a0250'
#         self.filename = 'f1.doc'
#         self.key_path = 's3://dev-orca'
#         self.restore_destination = 'restore-bucket'
#         self.error_message = 'Access denied'
#         self.archive_destination = 'archive-bucket'

#     def tearDown(self):
#         """
#         Perform teardown for the tests
#         """
#         self.mock_sqs.stop()
        
# # ---------------------------------------------------------------------------------------------------------------------------------
#                                 # unit tests for request method as NEW 
# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_file_to_queue_new_pending(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is PENDING.
#         The new_data in this case should return request_time, key_path and restore_destination in addition to other values.
#         Completion_time and error_message should not exist in the response received from SQS body.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.PENDING
#         #this is the expected message body that should be received. 
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value, 
#                     "key_path": self.key_path, "restore_destination": self.restore_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
#         self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_file_to_queue_new_staged(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is STAGED.
#         The new_data in this case should return request_time, key_path and restore_destination in addition to other values.
#         Completion_time and error_message should not exist in the response received from SQS body.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.STAGED
#         #this is the expected message body that should be received.
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value, "key_path": self.key_path, 
#                     "restore_destination": self.restore_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
#         self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_file_to_queue_new_success(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is SUCCESS.
#         The new_data should return request_time, key_path and restore_destination, completion_time in addition to other values.
#         Error_message should not exist in the response received from SQS body.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.SUCCESS
#         #this is the expected message body that should be received.
#         #the request_time, last_update, completion_time are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value,"key_path": self.key_path, 
#                     "restore_destination": self.restore_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id, self.granule_id, self.filename, self.key_path, self.restore_destination,status_id, self.error_message,request_method, self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo, datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
#         self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_file_to_queue_new_failed(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is FAILED.
#         The new_data in this case should return request_time, key_path and restore_destination, completion_time, error_message in addition to other values.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.FAILED
#         #this is the expected message body that should be received. 
#         #the request_time, last_update , completion_time are not shown in new_data.        
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value, "key_path": self.key_path, 
#                     "restore_destination": self.restore_destination,
#                     "error_message": self.error_message}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo, datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["key_path"], new_data["key_path"])
#         self.assertEqual(queue_output_body["restore_destination"], new_data["restore_destination"])
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(self.error_message, queue_output_body["error_message"])
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_job_to_queue_new_pending(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is PENDING.
#         The new_data in this case should return request_time, archive_destination in addition to other values.
#         Completion_time should not exist in the response received from SQS body.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.PENDING
#         #this is the expected message body that should be received.
#         #the request_time is not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value, 
#                     "archive_destination": self.archive_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(self.job_id,self.granule_id,status_id,self.archive_destination,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
        
#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_job_to_queue_new_staged(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is STAGED.
#         The new_data in this case should return request_time, archive_destination in addition to other values.
#         Completion_time should not exist in the response received from SQS body.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.STAGED
#         #this is the expected message body that should be received.
#         #the request_time is not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value, 
#                         "archive_destination": self.archive_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,
#             self.archive_destination,request_method,self.db_queue_url
#             )
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_job_to_queue_new_success(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is SUCCESS.
#         The new_data in this case should return request_time, archive_destination, completion_time in addition to other values.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.SUCCESS
#         #this is the expected message body that should be received. 
#         #the request_time, completion_time are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value,
#                     "archive_destination": self.archive_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,
#             self.archive_destination,request_method,self.db_queue_url
#             )
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------

#     def test_post_status_for_job_to_queue_new_failed(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is FAILED.
#         The new_data in this case should return request_time, archive_destination, completion_time in addition to other values.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.NEW
#         status_id = shared_recovery.OrcaStatus.FAILED
#         #this is the expected message body that should be received. 
#         #the request_time, completion_time are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value,
#                     "archive_destination": self.archive_destination}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,
#             self.archive_destination,request_method,self.db_queue_url
#             )
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_request_time = datetime.fromisoformat(queue_output_body["request_time"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertIn("request_time", queue_output_body)
#         self.assertEqual(new_request_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["archive_destination"], new_data["archive_destination"])
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# # ---------------------------------------------------------------------------------------------------------------------------------
#                                 # unit tests for request method as UPDATE 
# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_job_to_queue_update_pending(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is PENDING.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.PENDING
#         #this is the expected message body that should be received. 
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,request_method,self.db_queue_url)            
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_job_to_queue_update_staged(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is STAGED.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.STAGED
#         #this is the expected message body that should be received. 
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,self.archive_destination,request_method,self.db_queue_url)            
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)


# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_job_to_queue_update_success(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is SUCCESS.
#         The queue output will include completion_time in addition to other parameters.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.SUCCESS
#         #this is the expected message body that should be received. 
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,self.archive_destination,request_method,self.db_queue_url)            
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)
# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_job_to_queue_update_failed(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_job_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is FAILED.
#         The queue output will include completion_time in addition to other parameters.
#         """
#         table_name = 'orca_recoveryjob'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.FAILED
#         #this is the expected message body that should be received. 
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value + body
#         MessageAttributes={
#             "RequestMethod": {
#                 "DataType": "String",
#                 "StringValue": request_method.value,
#             },
#             "TableName": {"DataType": "String", "StringValue": table_name},
#         }

#         shared_recovery.post_status_for_job_to_queue(
#             self.job_id,self.granule_id,status_id,self.archive_destination,request_method,self.db_queue_url)            
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                         MessageAttributeNames= ["All"]
#                         )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])
        
#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertIn("completion_time", queue_output_body)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_file_to_queue_update_pending(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is PENDING.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.PENDING
#         #this is the expected message body that should be received. 
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("key_path", queue_output_body)
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)


# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_file_to_queue_update_staged(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is STAGED.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.STAGED
#         #this is the expected message body that should be received. 
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("key_path", queue_output_body)
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertNotIn("completion_time", queue_output_body)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)


# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_file_to_queue_update_success(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is UPDATE, ORCA status is SUCCESS.
#         The queue output will include completion_time in addition to other parameters.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.SUCCESS
#         #this is the expected message body that should be received. 
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])

#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("key_path", queue_output_body)
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertNotIn("error_message", queue_output_body)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# # ---------------------------------------------------------------------------------------------------------------------------------
#     def test_post_status_for_file_to_queue_update_failed(self):
#         """
#         Test that sending a message to SQS queue using post_status_for_file_to_queue() function returns the same expected message.
#         This is for testing the case when request_method is NEW, ORCA status is PENDING.
#         The queue output will include completion_time, error_message in addition to other parameters.
#         """
#         table_name = 'orca_recoverfile'
#         request_method = shared_recovery.RequestMethod.UPDATE
#         status_id = shared_recovery.OrcaStatus.FAILED
#         #this is the expected message body that should be received. 
#         #the request_time, last_update are not shown in new_data.
#         new_data = {"job_id": self.job_id, "granule_id": self.granule_id, "filename": self.filename, 
#                     "status_id": status_id.value}
#         body = json.dumps(new_data)
#         MessageDeduplicationId = table_name + request_method.value  + body
#         MessageAttributes={
#                 "RequestMethod": {
#                     "DataType": "String",
#                     "StringValue": request_method.value,
#                 },
#                 "TableName": {"DataType": "String", "StringValue": table_name},
#             }

#         shared_recovery.post_status_for_file_to_queue(
#             self.job_id,self.granule_id,self.filename,self.key_path,self.restore_destination,status_id,self.error_message,request_method,self.db_queue_url)
#         #grabbing queue contents after the message is sent
#         queue_contents = self.queue.receive_messages(
#                             MessageAttributeNames= ["All"]
#                             )
#         queue_output_body = json.loads(queue_contents[0].body)
#         new_last_update = datetime.fromisoformat(queue_output_body["last_update"])
#         new_completion_time = datetime.fromisoformat(queue_output_body["completion_time"])
        
#         self.assertEqual(queue_output_body["job_id"], new_data["job_id"])
#         self.assertEqual(queue_output_body["granule_id"], new_data["granule_id"])
#         self.assertEqual(queue_output_body["filename"], new_data["filename"])
#         self.assertIn("last_update", queue_output_body)
#         self.assertEqual(new_last_update.tzinfo,datetime.now(timezone.utc).tzinfo)
#         self.assertEqual(queue_output_body["status_id"], new_data["status_id"])
#         self.assertNotIn("key_path", queue_output_body)
#         self.assertNotIn("archive_destination", queue_output_body)
#         self.assertNotIn("request_time", queue_output_body)
#         self.assertIn("completion_time", queue_output_body)
#         self.assertEqual(new_completion_time.tzinfo, timezone.utc)
#         self.assertEqual(queue_output_body["error_message"], self.error_message)
#         self.assertEqual(queue_contents[0].attributes['MessageGroupId'], self.MessageGroupId)
#         self.assertEqual(queue_contents[0].message_attributes, MessageAttributes)

# if __name__ == "__main":
#     unittest.main()


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

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs")
        self.queue = self.test_sqs.create_queue(QueueName="unit-test-queue")
        self.db_queue_url = self.queue.url
        self.request_methods = [
            shared_recovery.RequestMethod.NEW,
            shared_recovery.RequestMethod.UPDATE,
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

    def test_post_entry_to_queue_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_entry_to_queue()
        function returns the same expected message.
        """
        table_name = "test"
        new_data = {"name": "test"}
        for request_method in self.request_methods:
            # Setting the message attribute values to what we expect.
            MessageAttributes = {
                "RequestMethod": {
                    "DataType": "String",
                    "StringValue": request_method.value,
                },
                "TableName": {"DataType": "String", "StringValue": table_name},
            }

            # Run subtests
            with self.subTest(request_method=request_method):

                # Send values to the function
                shared_recovery.post_entry_to_queue(
                    table_name,
                    new_data,
                    request_method,
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
                    self.MessageGroupId
                )
                self.assertEqual(
                    queue_contents[0].message_attributes, MessageAttributes
                )

                # Testing SQS body
                self.assertEqual(queue_output_body, new_data)

    def test_post_status_for_job_to_queue_no_errors(self):
        """
        *Happy Path*
        Tests that messages are correctly constructed by function and sent to
        the queue based on RequestMethod and Status values.
        """
        table_name = "orca_recoveryjob"
        for request_method in self.request_methods:
            for status_id in self.statuses:
                # Setting the message attribute values to what we expect.
                MessageAttributes = {
                    "RequestMethod": {
                        "DataType": "String",
                        "StringValue": request_method.value,
                    },
                    "TableName": {"DataType": "String", "StringValue": table_name},
                }

                # Setting other variables unique to this test
                archive_destination = "s3://archive-bucket"

                # Run subtests
                with self.subTest(request_method=request_method, status_id=status_id):

                    # Send values to the function
                    shared_recovery.post_status_for_job_to_queue(
                        self.job_id,
                        self.granule_id,
                        status_id,
                        archive_destination,
                        request_method,
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
                    self.assertEqual(queue_output_body["status_id"], status_id.value)

                    # Testing fields based on request_method
                    if request_method == shared_recovery.RequestMethod.NEW:
                        self.assertIn("request_time", queue_output_body)
                        # Get the request time
                        new_request_time = datetime.fromisoformat(
                            queue_output_body["request_time"]
                        )
                        self.assertEqual(new_request_time.tzinfo, timezone.utc)
                        self.assertEqual(
                            queue_output_body["archive_destination"],
                            archive_destination
                        )
                    else:
                        self.assertNotIn("request_time", queue_output_body)
                        self.assertNotIn("archive_destination", queue_output_body)

                    # Testing fields based on status_id
                    completion_status = [
                        shared_recovery.OrcaStatus.SUCCESS,
                        shared_recovery.OrcaStatus.FAILED
                    ]

                    if status_id in completion_status:
                        self.assertIn("completion_time", queue_output_body)
                        new_completion_time = datetime.fromisoformat(
                            queue_output_body["completion_time"]
                        )
                        self.assertEqual(new_completion_time.tzinfo, timezone.utc)
                    else:
                        self.assertNotIn("completion_time", queue_output_body)

    def test_post_status_for_file_to_queue_no_errors(self):
        """
        *Happy Path*
        Test that sending a message to SQS queue using post_status_for_file
        function returns the same expected message.
        """
        table_name = "orca_recoverfile"
        for request_method in self.request_methods:
            for status_id in self.statuses:
                # Setting the message attribute values to what we expect.
                MessageAttributes = {
                    "RequestMethod": {
                        "DataType": "String",
                        "StringValue": request_method.value,
                    },
                    "TableName": {"DataType": "String", "StringValue": table_name},
                }

                # Setting other variables unique to this test
                key_path = "/s3/dev"
                restore_destination = "s3://restore-bucket"
                error_message = "Access denied"
                filename = "f1.doc"

                # Run subtests
                with self.subTest(request_method=request_method, status_id=status_id):

                    # Send values to the function
                    shared_recovery.post_status_for_file_to_queue(
                        self.job_id,
                        self.granule_id,
                        filename,
                        key_path,
                        restore_destination,
                        status_id,
                        error_message,
                        request_method,
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
                    self.assertEqual(queue_output_body["status_id"], status_id.value)
                    self.assertEqual(queue_output_body["filename"], filename)

                    # Testing fields based on request_method
                    if request_method == shared_recovery.RequestMethod.NEW:
                        self.assertIn("request_time", queue_output_body)
                        # Get the request time
                        new_request_time = datetime.fromisoformat(
                            queue_output_body["request_time"]
                        )
                        self.assertEqual(new_request_time.tzinfo, timezone.utc)
                        self.assertEqual(
                            queue_output_body["key_path"],
                            key_path
                        )
                        self.assertEqual(
                            queue_output_body["restore_destination"],
                            restore_destination
                        )
                    else:
                        self.assertNotIn("request_time", queue_output_body)
                        self.assertNotIn("restore_destination", queue_output_body)
                        self.assertNotIn("key_path", queue_output_body)

                    # Testing fields based on status_id
                    completion_status = [
                        shared_recovery.OrcaStatus.SUCCESS,
                        shared_recovery.OrcaStatus.FAILED
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
                            queue_output_body["error_message"],
                            error_message
                        )
                    else:
                        self.assertNotIn("error_message", queue_output_body)

    # Other non-happy tests go here for things that should raise exceptions
