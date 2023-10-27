"""
Name: migrate_db.py

Description: Migrates the current ORCA schema version to the latest version.
"""
from typing import List

from orca_shared.database.entities import PostgresConnectionInfo

from migrations.migrate_versions_1_to_2.migrate import migrate_versions_1_to_2
from migrations.migrate_versions_2_to_3.migrate import migrate_versions_2_to_3
from migrations.migrate_versions_3_to_4.migrate import migrate_versions_3_to_4
from migrations.migrate_versions_4_to_5.migrate import migrate_versions_4_to_5
from migrations.migrate_versions_5_to_6.migrate import migrate_versions_5_to_6
from migrations.migrate_versions_6_to_7.migrate import migrate_versions_6_to_7


def perform_migration(
    current_schema_version: int, config: PostgresConnectionInfo, orca_buckets: List[str]
) -> None:
    """
    Performs a migration of the ORCA database. Determines the order and
    migrations to run.

    Args:
        current_schema_version: Current version of the ORCA schema
        config: Database connection information
        orca_buckets: List of ORCA bucket names used to create partition tables for v5.

    Returns:
        None
    """
    # Determine migrations to run based on current_schema_version and
    # update the versions table based on the latest_schema_version.

    if current_schema_version == 1:
        # Run migrations from version 1 to version 2
        migrate_versions_1_to_2(config, False)
        current_schema_version = 2

    if current_schema_version == 2:
        # Run migrations from version 2 to version 3
        migrate_versions_2_to_3(config, False)
        current_schema_version = 3

    if current_schema_version == 3:
        # Run migrations from version 3 to version 4
        migrate_versions_3_to_4(config, False)
        current_schema_version = 4

    if current_schema_version == 4:
        # Run migrations from version 4 to version 5
        migrate_versions_4_to_5(config, False, orca_buckets)
        current_schema_version = 5

    if current_schema_version == 5:
        # Run migrations from version 5 to version 6
        migrate_versions_5_to_6(config, False)
        current_schema_version = 6

    if current_schema_version == 6:
        # Run migrations from version 6 to version 7
        migrate_versions_6_to_7(config, True)
        current_schema_version = 7
