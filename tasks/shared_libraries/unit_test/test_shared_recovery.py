import boto3
from moto import mock_sqs
import shared_recovery

@mock_sqs
def test_post_entry_to_queue():
    "Test the write_message method with a valid message"
    sqs = boto3.client('sqs')
    queue = sqs.create_queue(QueueName='uni-test-queue.fifo')
    print(queue)
    table_name = "rizbi"
    new_data = {"name": "Rizbi" }
    request_method = 'post'
    db_queue_url = queue["QueueUrl"]
    print(db_queue_url)


    shared_recovery.post_entry_to_queue(table_name, new_data, request_method, db_queue_url)
    # # ---------------test---------------------------------------------
    # skype_message = 'Testing with a valid message'
    # channel = 'test'
    # expected_message = str({'msg':f'{skype_message}', 'channel':channel})
    # shared_recovery.post_entry_to_queue()
    # sqs_messages = queue.receive_messages()
test_post_entry_to_queue()