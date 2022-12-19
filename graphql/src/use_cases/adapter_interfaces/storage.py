class StorageMetadataInterface:
    """
    Generic storage class with methods that need to be implemented by database adapter.
    """

    def get_schema_version(self, connection) -> int:
        """
        Queries the database version table and returns the latest version.

        Args:
            connection: Database connection object.

        Returns:
            Version number of the currently installed ORCA schema.
        """
        ...
