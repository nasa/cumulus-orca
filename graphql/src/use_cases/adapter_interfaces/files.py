import logging
from typing import Dict, Any

from src.entities.files import FileLocation


class InternalReconciliationFilesInterface:
    """
    Generic file-accessing class with methods that need to be implemented by storage adapter.
    """

    def get_file_body(
        self,
        file_location: FileLocation,
        report_bucket_region: str  # todo: bubble out to keep clean?
    ) -> str:
        """
        Opens the specified utf-8 file and returns the contents as a string.

        Args:
            file_location: Location of the file.
            report_bucket_region: The name of the region the report bucket resides in.

        Returns: The body of the file.
        """
        ...

    def setup_inventory_report_from_manifest(
        self,
        manifest: Dict,
        manifest_location: FileLocation,
        logger: logging.Logger,
    ) -> Any:
        """
        Performs any additional processing required for inventory reports,
        returning information required by future steps.

        Args:
            manifest: Manifest containing inventory report metadata.
            manifest_location: The original location of the manifest.
            logger: The logger to use.

        Returns: Information required by future steps.
        """
        ...
