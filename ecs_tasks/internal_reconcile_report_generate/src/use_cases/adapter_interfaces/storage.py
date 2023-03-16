from src.entities.aws import S3InventoryManifest, S3InventoryManifestMetadata


class StorageInterface:
    """
    Generic storage class with methods that need to be implemented by database adapter.
    """
    def create_job(
        self,
        inventory_creation_timestamp: float,
        report_source: str,
    ) -> str:
        """
        Creates a job status entry.

        Args:
            inventory_creation_timestamp: Seconds since epoch that the inventory was created.
            report_source: The region covered by the report.

        Returns: The cursor to the reconciliation job.
        """
        ...

    def import_current_archive_list_for_reconciliation_job(
        self,
        inventory_manifest: S3InventoryManifest,
        inventory_manifest_metadata: S3InventoryManifestMetadata,
        report_cursor: str,
    ) -> None:
        """
        Pulls the inventory report into the database.

        Args:
            inventory_manifest: Contains information about the inventory report.
            inventory_manifest_metadata: Extra information about the inventory report.
            report_cursor: The cursor to the reconciliation job.
        """
        ...

    def perform_orca_reconcile_for_reconciliation_job(
        self,
        report_source: str,
        report_cursor: str,
    ) -> None:
        """
        Checks the pulled-in inventory report against the database's expectations.

        Args:
            report_source: The region covered by the report.
            report_cursor: The cursor to the reconciliation job.
        """
        ...
