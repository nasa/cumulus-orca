import dataclasses
import json
import logging
from typing import Dict, Any, List

import boto3
import pydantic
# noinspection PyPackageRequirements
import strawberry

from src.entities.files import FileLocation
from src.use_cases.adapter_interfaces.files import InternalReconciliationFilesInterface

MANIFEST_FILES_KEY = "files"
FILES_KEY_KEY = "key"


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class AWSS3FileLocation(pydantic.BaseModel, FileLocation):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    bucket_name: str
    key: str

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self, bucket_name: str, key: str):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(bucket_name=bucket_name, key=key)


class InternalReconciliationS3(InternalReconciliationFilesInterface):
    def __init__(self):
        pass

    def get_file_body(
        self,
        file_location: AWSS3FileLocation,
        report_bucket_region: str
    ) -> str:
        """
        Opens the specified utf-8 file and returns the contents as a string.

        Args:
            file_location: Location of the file.
            report_bucket_region: The name of the region the report bucket resides in.

        Returns: The body of the file.
        """
        s3_client = boto3.client("s3", region_name=report_bucket_region)
        file_object = s3_client.get_object(Bucket=file_location.bucket_name, Key=file_location.key)
        file_data = file_object["Body"].read()
        file_str = file_data.decode("utf-8")
        return file_str

    def setup_inventory_report_from_manifest(
        self,
        manifest: Dict,
        manifest_location: AWSS3FileLocation,
        logger: logging.Logger,
    ) -> List[str]:
        """
        Performs any additional processing required for inventory reports,
        returning information required by future steps.

        Args:
            manifest: Manifest containing inventory report metadata.
            manifest_location: The original location of the manifest.
            logger: The logger to use.

        Returns: Information required by future steps.
        """
        csv_key_paths = [file[FILES_KEY_KEY] for file in manifest[MANIFEST_FILES_KEY]]

        for csv_key_path in csv_key_paths:
            if not csv_key_path.endswith(".csv.gz"):
                raise Exception(f"Cannot handle file extension on '{csv_key_path}'")
            # Set the required metadata
            self.add_metadata_to_gzip(
                AWSS3FileLocation(manifest_location.bucket_name, csv_key_path)
            )
        return csv_key_paths

    @staticmethod
    def add_metadata_to_gzip(
        file_location: AWSS3FileLocation,
    ) -> None:
        """
        AWS does not add proper metadata to gzip files, which breaks aws_s3.table_import_from_s3
        Must add manually.
        Args:
            file_location: Location of the file.
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
