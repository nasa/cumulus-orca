import json
import logging
import os
from typing import Optional

import boto3

from src.entities.aws import (
    AWSS3FileLocation,
    AWSSQSInventoryReportMessage,
    S3InventoryManifest,
    S3InventoryManifestMetadata,
)
from src.use_cases.helpers import retry_error

MESSAGES_KEY = "Messages"


class AWS:
    def __init__(
        self,
        s3_inventory_queue: str,
    ):
        self.s3_inventory_queue = s3_inventory_queue

    def get_s3_manifest_event_from_sqs(
        self
    ) -> Optional[AWSSQSInventoryReportMessage]:
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

        if MESSAGES_KEY not in sqs_response.keys():
            return None

        if len(sqs_response[MESSAGES_KEY]) > 1:
            raise Exception("More than one message retrieved. Check `receive_message` call.")

        message = sqs_response[MESSAGES_KEY][0]
        message_receipt_handle = message["ReceiptHandle"]

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

    # noinspection PyMethodMayBeStatic
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
            manifest_creation_datetime=int(manifest["creationTimestamp"]) / 1000,
            manifest_files=[
                AWSS3FileLocation(key=f["key"], bucket_name=report_bucket_name)
                for f in manifest["files"]
            ],
            manifest_files_columns=manifest["fileSchema"].replace(" ", "").split(","),
        )

    # noinspection PyMethodMayBeStatic
    def add_metadata_to_gzip(self, file_location: AWSS3FileLocation) -> None:
        """
        AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
        Must add manually.
        Args:
            file_location: Location of the file in S3
        """
        s3 = boto3.resource("s3")
        s3_object = s3.Object(file_location.bucket_name, file_location.key)
        # Only add if needed.
        if s3_object.content_encoding is None:
            s3_object.copy_from(
                CopySource={"Bucket": file_location.bucket_name, "Key": file_location.key},
                Metadata=s3_object.metadata,
                MetadataDirective="REPLACE",
                ContentEncoding="gzip",
            )

    @retry_error()
    def remove_job_from_queue(
        self,
        message_receipt_handle: str,
        logger: logging.Logger,
    ):
        """
        Removes the completed job from the queue, preventing it from going to the dead-letter
        queue.

        Args:
            message_receipt_handle: The ReceiptHandle for the event in the queue.
            logger: The logger to use.
        """
        aws_client_sqs = boto3.client("sqs")
        logger.debug(
            f"Deleting message '{message_receipt_handle}' from queue '"
            f"{self.s3_inventory_queue}'")
        # Remove message from the queue we are listening to.
        aws_client_sqs.delete_message(
            QueueUrl=self.s3_inventory_queue,
            ReceiptHandle=message_receipt_handle,
        )
