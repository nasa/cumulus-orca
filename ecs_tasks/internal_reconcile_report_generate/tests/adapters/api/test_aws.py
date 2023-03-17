import json
import unittest
import uuid
from unittest.mock import patch, Mock, MagicMock

from src.adapters.api.aws import AWS, MESSAGES_KEY


class TestAWS(unittest.TestCase):
    @patch("src.adapters.api.aws.boto3.client")
    def test_get_s3_manifest_event_from_sqs_happy_path(
        self,
        mock_boto3_client
    ):
        # noinspection GrazieInspection
        """
        Happy path for retrieving and parsing an s3 manifest event.
        """
        mock_s3_inventory_queue = Mock()
        receipt_handle = uuid.uuid4().__str__()
        region0 = uuid.uuid4().__str__()
        bucket0 = uuid.uuid4().__str__()
        key0 = uuid.uuid4().__str__()
        region1 = uuid.uuid4().__str__()
        bucket1 = uuid.uuid4().__str__()
        key1 = uuid.uuid4().__str__()

        mock_boto3_client.return_value.receive_message.return_value = {
            MESSAGES_KEY: [
                {
                    "ReceiptHandle": receipt_handle,
                    "Body": json.dumps({
                        "Records": [
                            {
                                "awsRegion": region0,
                                "s3": {
                                    "bucket": {
                                        "name": bucket0
                                    },
                                    "object": {
                                        "key": key0
                                    }
                                }
                            },
                            {
                                "awsRegion": region1,
                                "s3": {
                                    "bucket": {
                                        "name": bucket1
                                    },
                                    "object": {
                                        "key": key1
                                    }
                                }
                            },
                        ]
                    })
                }
            ]
        }

        result = AWS(mock_s3_inventory_queue).get_s3_manifest_event_from_sqs()

        mock_boto3_client.assert_called_once_with("sqs")
        mock_boto3_client.return_value.receive_message.assert_called_once_with(
            QueueUrl=mock_s3_inventory_queue,
            MaxNumberOfMessages=1,
        )
        self.assertEqual(receipt_handle, result.message_receipt)
        self.assertEqual(2, len(result.manifest_metadatas))
        self.assertEqual(region0, result.manifest_metadatas[0].report_bucket_region)
        self.assertEqual(bucket0, result.manifest_metadatas[0].report_bucket_name)
        self.assertEqual(key0, result.manifest_metadatas[0].manifest_key)
        self.assertEqual(region1, result.manifest_metadatas[1].report_bucket_region)
        self.assertEqual(bucket1, result.manifest_metadatas[1].report_bucket_name)
        self.assertEqual(key1, result.manifest_metadatas[1].manifest_key)

    @patch("src.adapters.api.aws.boto3.client")
    def test_get_s3_manifest_event_from_sqs_no_messages_raises_error(
        self,
        mock_boto3_client,
    ):
        # noinspection GrazieInspection
        """
        If no messages are present, raise error.
        """
        mock_s3_inventory_queue = Mock()

        mock_boto3_client.return_value.receive_message.return_value = {
        }

        with self.assertRaises(Exception) as cm:
            AWS(mock_s3_inventory_queue).get_s3_manifest_event_from_sqs()

        self.assertEqual("No messages in queue.", str(cm.exception))
        mock_boto3_client.assert_called_once_with("sqs")
        mock_boto3_client.return_value.receive_message.assert_called_once_with(
            QueueUrl=mock_s3_inventory_queue,
            MaxNumberOfMessages=1,
        )

    @patch("src.adapters.api.aws.boto3.client")
    def test_get_manifest_happy_path(
        self,
        mock_boto3_client: MagicMock,
    ):
        """
        Happy path for retrieving manifest from S3.
        """
        manifest_key_path = f"{uuid.uuid4().__str__()}/{uuid.uuid4().__str__()}/manifest.json"
        mock_report_bucket_name = Mock()
        mock_report_bucket_region = Mock()
        manifest_source_bucket = uuid.uuid4().__str__()
        manifest_file0_key = uuid.uuid4().__str__()
        manifest_file1_key = uuid.uuid4().__str__()
        column0 = uuid.uuid4().__str__()
        column1 = uuid.uuid4().__str__()
        column2 = uuid.uuid4().__str__()
        mock_body = Mock()
        mock_body.read = Mock(return_value=json.dumps({
            "sourceBucket": manifest_source_bucket,
            "creationTimestamp": 4986486464735,
            "files": [
                {
                    "key": manifest_file0_key
                },
                {
                    "key": manifest_file1_key
                }
            ],
            "fileSchema": f"{column0}, {column1}, {column2}"
        }).encode("utf-8"))
        mock_boto3_client.return_value.get_object.return_value = {"Body": mock_body}

        aws = AWS(Mock())

        result = aws.get_manifest(
            manifest_key_path,
            mock_report_bucket_name,
            mock_report_bucket_region,
            Mock(),
        )

        self.assertEqual(4986486464, result.manifest_creation_datetime)
        self.assertEqual(manifest_source_bucket, result.source_bucket_name)
        self.assertEqual(2, len(result.manifest_files))
        self.assertEqual(manifest_file0_key, result.manifest_files[0].key)
        self.assertEqual(mock_report_bucket_name, result.manifest_files[0].bucket_name)
        self.assertEqual(manifest_file1_key, result.manifest_files[1].key)
        self.assertEqual(mock_report_bucket_name, result.manifest_files[1].bucket_name)
        self.assertEqual(3, len(result.manifest_files_columns))
        self.assertEqual([column0, column1, column2], result.manifest_files_columns)

        mock_boto3_client.assert_called_once_with("s3", region_name=mock_report_bucket_region)
        mock_boto3_client.return_value.get_object.assert_called_once_with(
            Bucket=mock_report_bucket_name,
            Key=manifest_key_path,
        )

    @patch("src.adapters.api.aws.boto3.resource")
    def test_add_metadata_to_gzip_happy_path(
        self,
        mock_boto3_resource: MagicMock
    ):
        """
        Happy path for adding missing metadata to AWS Inventory csv.gz files.
        """
        mock_s3_object = mock_boto3_resource.return_value.Object.return_value
        mock_s3_object.content_encoding = None
        mock_report_bucket_name = Mock()
        mock_gzip_key_path = Mock()
        aws = AWS(Mock())

        aws.add_metadata_to_gzip(
            mock_report_bucket_name, mock_gzip_key_path
        )

        mock_boto3_resource.assert_called_once_with("s3")
        mock_boto3_resource.return_value.Object.assert_called_once_with(
            mock_report_bucket_name, mock_gzip_key_path
        )
        mock_s3_object.copy_from.assert_called_once_with(
            CopySource={"Bucket": mock_report_bucket_name, "Key": mock_gzip_key_path},
            Metadata=mock_s3_object.metadata,
            MetadataDirective="REPLACE",
            ContentEncoding="gzip",
        )

    @patch("src.adapters.api.aws.boto3.resource")
    def test_add_metadata_to_gzip_already_present_does_not_copy(
        self,
        mock_boto3_resource: MagicMock
    ):
        """
        If metadata is already present, do not add.
        """
        mock_s3_object = mock_boto3_resource.return_value.Object.return_value
        mock_s3_object.content_encoding = Mock()
        mock_report_bucket_name = Mock()
        mock_gzip_key_path = Mock()
        aws = AWS(Mock())

        aws.add_metadata_to_gzip(
            mock_report_bucket_name, mock_gzip_key_path
        )

        mock_boto3_resource.assert_called_once_with("s3")
        mock_boto3_resource.return_value.Object.assert_called_once_with(
            mock_report_bucket_name, mock_gzip_key_path
        )
        mock_s3_object.copy_from.assert_not_called()

    @patch("src.adapters.api.aws.boto3.client")
    def test_remove_job_from_queue_happy_path(
        self,
        mock_boto3_client
    ):
        """
        Happy path for removing an item from a queue.
        """
        internal_report_queue_url = Mock()
        message_receipt_handle = Mock()
        aws = AWS(internal_report_queue_url)

        aws.remove_job_from_queue(
            message_receipt_handle,
            Mock(),
        )

        mock_boto3_client.assert_called_once_with("sqs")
        mock_boto3_client.return_value.delete_message.assert_called_once_with(
            QueueUrl=internal_report_queue_url,
            ReceiptHandle=message_receipt_handle,
        )
