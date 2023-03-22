from dataclasses import dataclass
from typing import List


@dataclass
class AWSS3FileLocation:
    """
    Location of a file in AWS S3.

    Contains:
        bucket_name: Name of the bucket.
        key: Key to the file in the bucket.
    """
    bucket_name: str
    key: str


@dataclass
class S3InventoryManifestMetadata:
    """
    Contains:
        report_bucket_region: Region the report bucket resides in.
        report_bucket_name: Name of the report bucket.
        manifest_key: Key/path to the manifest within the report bucket.
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
        message_receipt: Receipt handle of the message in the queue.
        manifest_metadatas: List of manifest files stored in S3 for the report.
    """
    message_receipt: str
    manifest_metadatas: List[S3InventoryManifestMetadata]


@dataclass
class S3InventoryManifest:
    """
    Represents an AWS S3 Inventory Report manifest.

    Contains:
        source_bucket_name: Name of the bucket the report was generated for.
        manifest_creation_datetime: Milliseconds since epoch the report was generated.
        manifest_files: Locations of files that make up the report.
        manifest_files_columns: CSV string of column names in the report files.
    """
    source_bucket_name: str
    manifest_creation_datetime: float
    manifest_files: list[AWSS3FileLocation]
    manifest_files_columns: str
