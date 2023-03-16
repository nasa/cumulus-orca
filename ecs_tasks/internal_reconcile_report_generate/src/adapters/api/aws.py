import json
import logging
import os
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timezone

import boto3

from src.use_cases.helpers import retry_error

MESSAGES_KEY = "Messages"

# todo: remove this
test_message = {'Messages': [{'MessageId': '08e0c88d-f43a-4dbd-a1ab-ec0bab5fb209',
                              'ReceiptHandle':
                                  'AQEBqEhnr56xz+9DO6JmWhPq7rzOyOecqcXQZVq+XBLoBgqXF2S2SW2xVmNJ47HW1AFFH8mOPXTHYsaRyg/Fy0GWtd+4EGux4RIbdyP+YCnr3HMljQ2Gd3XMrlmjl/TWXM9jRbuKKch5/zOBKvWXskGsxSDtdfmIY9uDvu9D2E8CyhE0SQKeCvReWWgArVpwlQsgYqdye+n7B19Ce/rE91PkZOSfOzUB5vemTPMb5PCjPidz3s59EaS58Y0/YBn2t8zo6Vh4PBvocvk2VOSGVJ0c5d2NexGC0KvjD/R61SuALShUKMem/G2L6d55g2IYJptLfQiWo6/DrgNqmIDylpZpldEICOpIpi23GIZ7Wh9wFZITwPacS4+NhV5ICf0e/5ADQp2RUdWBHHHAYqFI4hPsB7Q1P0wm8sVRdNzLSsjMbEM=',
                              'MD5OfBody': '43885e5f79802c6e936dd989961c3fdf',
                              'Body': '{"Records":[{"eventVersion":"2.1",'
                                      '"eventSource":"aws:s3","awsRegion":"us-west-2",'
                                      '"eventTime":"2023-03-10T17:59:10.878Z",'
                                      '"eventName":"ObjectCreated:Put","userIdentity":{'
                                      '"principalId":"AWS:AROAII6QBJF3CVCYZA6A4:i-08d7456b6989c0141"},"requestParameters":{"sourceIPAddress":"10.0.22.174"},"responseElements":{"x-amz-request-id":"XKNW9RNZ9M2KR1Y3","x-amz-id-2":"skGc4l20jZedrF99lhWsPuyxbfbPZduQ2FH2cRnQQW5B61ZbmvfCiNh+g8wYgPgCD7pFdk4/Fm3cIEeNtIDLAI8nriEZGqZ4"},"s3":{"s3SchemaVersion":"1.0","configurationId":"tf-s3-queue-20230227220547938400000001","bucket":{"name":"doctest-orca-reports","ownerIdentity":{"principalId":"A2GTTZHTE1ZT9T"},"arn":"arn:aws:s3:::doctest-orca-reports"},"object":{"key":"doctest-orca-primary/doctest-orca-primary-inventory/2023-03-10T01-00Z/manifest.json","size":527,"eTag":"ad964ff38ccf704d133061db0edcce80","sequencer":"00640B6FEECD600660"}}}]}'}],
                'ResponseMetadata': {'RequestId': 'e4499aa0-41a9-5f8a-ad56-c625e4e3cc27',
                                     'HTTPStatusCode': 200, 'HTTPHeaders': {
                        'x-amzn-requestid': 'e4499aa0-41a9-5f8a-ad56-c625e4e3cc27',
                        'date': 'Fri, 10 Mar 2023 21:37:14 GMT', 'content-type': 'text/xml',
                        'content-length': '2170'}, 'RetryAttempts': 0}}


@dataclass
class AWSS3FileLocation:
    bucket_name: str
    key: str


@dataclass
class S3InventoryManifestMetadata:
    """
    Contains:
        report_bucket_region: The region the report bucket resides in.
        report_bucket_name: The name of the report bucket.
        manifest_key: The key/path to the manifest within the report bucket.
        message_receipt: The receipt handle of the message in the queue.
    """
    report_bucket_region: str
    report_bucket_name: str
    manifest_key: str


@dataclass
class AWSSQSInventoryReportMessage:
    """
    Represents a single SQS message.
    AWS may or may not send multiple report manifests in one message.

    Contains:
        message_receipt: The receipt handle of the message in the queue.
        manifest_metadatas: The list of manifest files stored in S3 for the report.
    """
    message_receipt: str
    manifest_metadatas: List[S3InventoryManifestMetadata]


@dataclass
class S3InventoryManifest:
    source_bucket_name: str
    manifest_creation_datetime: float
    manifest_files: list[AWSS3FileLocation]
    manifest_files_columns: str


class AWS:
    def __init__(
        self,
        s3_inventory_queue: str,
    ):
        self.s3_inventory_queue = s3_inventory_queue

    def get_s3_manifest_event_from_sqs(
        self
    ) -> AWSSQSInventoryReportMessage:
        """
        Gets a message from the queue and formats it into the format for internal reconciliation.

        Returns:
            A AWSSQSInventoryReportMessage consisting of the relevant data.
        """
        aws_client_sqs = boto3.client("sqs")
        sqs_response = aws_client_sqs.receive_message(
            QueueUrl=self.s3_inventory_queue,
            MaxNumberOfMessages=1,
        )

        # todo: Remove this debug line:
        sqs_response = test_message

        if MESSAGES_KEY not in sqs_response.keys():
            raise Exception("No messages in queue.")

        if len(sqs_response[MESSAGES_KEY]) > 1:
            raise Exception("More than one message retrieved. Check `receive_message` call.")

        message = sqs_response[MESSAGES_KEY][0]
        message_receipt_handle = message["ReceiptHandle"]  # todo: delete message from queue

        body = json.loads(message["Body"])
        records = body["Records"]
        formatted_messages = []
        for record in records:
            # Unsure if AWS ever sends multiple records, but data structure supports it.
            formatted_messages.append(S3InventoryManifestMetadata(
                report_bucket_region=record["awsRegion"],
                report_bucket_name=record["s3"]["bucket"]["name"],
                manifest_key=record["s3"]["object"]["key"],
            ))

        return AWSSQSInventoryReportMessage(
            message_receipt=message_receipt_handle,
            manifest_metadatas=formatted_messages
        )

    def get_manifest(
        self,
        manifest_key_path: str,
        report_bucket_name: str,
        report_bucket_region: str,
        logger: logging.Logger,
    ) -> S3InventoryManifest:
        """

        Args:
            manifest_key_path: The full path within the s3 bucket to the manifest.
            report_bucket_name: The name of the bucket the manifest is located in.
            report_bucket_region: The name of the region the report bucket resides in.
            logger: The logger to use.

        Returns: The key of the csv specified in the manifest.
        """
        # Filter out non-manifest files. Should be done prior to this.
        filename = os.path.basename(manifest_key_path)

        if filename != "manifest.json":
            logger.error(f"Illegal file '{filename}'. Must be 'manifest.json'")
            raise Exception(f"Illegal file '{filename}'. Must be 'manifest.json'")

        s3_client = boto3.client("s3", region_name=report_bucket_region)
        file_object = s3_client.get_object(Bucket=report_bucket_name, Key=manifest_key_path)
        file_data = file_object["Body"].read()
        file_str = file_data.decode("utf-8")
        manifest = json.loads(file_str)
        return S3InventoryManifest(
            source_bucket_name=manifest["sourceBucket"],
            manifest_creation_datetime=
            int(manifest["creationTimestamp"]) / 1000,
            manifest_files=[
                AWSS3FileLocation(key=f["key"], bucket_name=report_bucket_name)
                for f in manifest["files"]
            ],
            manifest_files_columns=manifest["fileSchema"].replace(" ", "").split(","),
        )

    def add_metadata_to_gzip(self, report_bucket_name: str, gzip_key_path: str) -> None:
        """
        AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
        Must add manually.
        Args:
            report_bucket_name: The name of the bucket the csv is located in.
            gzip_key_path: The path within the bucket to the gzip file that needs metadata updated.
        """
        s3 = boto3.resource("s3")
        s3_object = s3.Object(report_bucket_name, gzip_key_path)
        # Only add if needed.
        if s3_object.content_encoding is None:
            s3_object.copy_from(
                CopySource={"Bucket": report_bucket_name, "Key": gzip_key_path},
                Metadata=s3_object.metadata,
                MetadataDirective="REPLACE",
                ContentEncoding="gzip",
            )

    @retry_error()
    def remove_job_from_queue(
        self,
        report_queue_url: str,
        message_receipt_handle: str,
        logger: logging.Logger,
    ):
        """
        Removes the completed job from the queue, preventing it from going to the dead-letter
        queue.

        Args:
            report_queue_url: The url of the queue containing the message.
            message_receipt_handle: The ReceiptHandle for the event in the queue.
            logger: The logger to use.
        """
        aws_client_sqs = boto3.client("sqs")
        logger.debug(
            f"Deleting message '{message_receipt_handle}' from queue '"
            f"{report_queue_url}'")
        # Remove message from the queue we are listening to.
        aws_client_sqs.delete_message(
            QueueUrl=report_queue_url,
            ReceiptHandle=message_receipt_handle,
        )
