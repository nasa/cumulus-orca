"""
Name: migrate_db.py

Description: Migrates the current ORCA schema version to the latest version.
"""
from typing import Dict

from migrations.migrate_versions_1_to_2.migrate import migrate_versions_1_to_2
from migrations.migrate_versions_2_to_3.migrate import migrate_versions_2_to_3
from migrations.migrate_versions_3_to_4.migrate import migrate_versions_3_to_4

def perform_migration(current_schema_version: int, config: Dict[str, str]) -> None:
    """
    Performs a migration of the ORCA database. Determines the order and
    migrations to run.

    Args:
        current_schema_version (int): Current version of the ORCA schema
        config (Dict): Dictionary containing database connection information

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
        migrate_versions_3_to_4(config, True)
        current_schema_version = 4