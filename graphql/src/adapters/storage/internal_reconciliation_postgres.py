from sqlalchemy import text

from src.adapters.storage.internal_reconciliation_rdbms import \
    InternalReconciliationStorageAdapterRDBMS
from src.entities.common import DirectionEnum


class InternalReconciliationStorageAdapterPostgres(InternalReconciliationStorageAdapterRDBMS):

    def __init__(
        self,
        user_connection_uri: str,
        admin_connection_uri: str,
        s3_access_key: str,
        s3_secret_key: str,
    ):
        super(InternalReconciliationStorageAdapterPostgres, self).__init__(
            user_connection_uri,
            admin_connection_uri,
            s3_access_key,
            s3_secret_key
        )

    @staticmethod
    def create_job_sql() -> text:  # pragma: no cover
        return text(
            """
            INSERT INTO reconcile_job
                ("orca_archive_location", "inventory_creation_time",
                "status_id", "start_time", "last_update", "end_time",
                "error_message")
            VALUES
                (:orca_archive_location, :inventory_creation_time,
                :status_id, :start_time, :last_update, :end_time,
                :error_message)
            RETURNING
                id"""
        )

    @staticmethod
    def truncate_s3_partition_sql(partition_name: str) -> text:  # pragma: no cover
        # Quickly removes data from the partition
        return text(  # nosec
            f"""
            TRUNCATE TABLE orca.{partition_name}
            """
        )

    @staticmethod
    def create_temporary_table_sql(temporary_s3_column_list: str) -> text:  # pragma: no cover
        """
        Creates a temporary table to store inventory data.
        Args:
            temporary_s3_column_list: The list of columns that need to be created to store
            csv data.
                Be very careful to avoid injection.
        """
        return text(  # nosec
            f"""
                CREATE TEMPORARY TABLE s3_import(
                    {temporary_s3_column_list}
                )
                """
        )

    @staticmethod
    def trigger_csv_load_from_s3_sql() -> text:  # pragma: no cover
        """
        SQL for telling postgres where/how to copy in the s3 inventory data.
        """
        return text(
            """
            SELECT aws_s3.table_import_from_s3(
                's3_import',
                '',
                '(format csv, FORCE_NULL(size_in_bytes))',
                :report_bucket_name,
                :csv_key_path,
                :report_bucket_region,
                :s3_access_key,
                :s3_secret_key,
                ''
            )
            """
        )

    @staticmethod
    def translate_s3_import_to_partitioned_data_sql() -> text:  # pragma: no cover
        """
        SQL for translating between the temporary table and Orca table.
        """
        return text(
            """
            INSERT INTO orca.reconcile_s3_object (
                    job_id,
                    orca_archive_location,
                    key_path,
                    etag,
                    last_update,
                    size_in_bytes,
                    storage_class,
                    delete_marker)
                SELECT
                :job_id,
                orca_archive_location,
                key_path,
                CONCAT('"', etag, '"') as etag, /* copy_to_archive's AWS call presently
                    wraps this in quotes. Seems like a bug, but is shown on
                    https://boto3.amazonaws.com/v1/documentation/api/latest/
                    reference/services/s3.html#S3.Client.list_object_versions */
                last_update,
                COALESCE(size_in_bytes, 0),
                storage_class, delete_marker
                FROM s3_import
                WHERE is_latest = TRUE
            """  # nosec    # noqa
        )

    @staticmethod
    def get_phantom_page_sql(direction: DirectionEnum) -> text:  # pragma: no cover
        """
        SQL for retrieving a page of phantoms for a given job,
        ordered by collection_id, granule_id, then key_path.
        """
        if direction == DirectionEnum.previous:
            sign = "<"
            order = "DESC"
        else:
            sign = ">"
            order = "ASC"

        return text(  # nosec
            f"""
    SELECT
        job_id,
        collection_id,
        granule_id,
        filename,
        key_path,
        orca_etag,
        (EXTRACT(EPOCH FROM date_trunc('milliseconds', orca_last_update)
         AT TIME ZONE 'UTC') * 1000)::bigint as orca_last_update,
        orca_size as orca_size_in_bytes,
        storage_class.value AS orca_storage_class
        FROM reconcile_phantom_report
        INNER JOIN reconcile_job ON
        (
            reconcile_job.id = reconcile_phantom_report.job_id
        )
        INNER JOIN storage_class ON
        (
            orca_storage_class_id=storage_class.id
        )
        WHERE
            job_id = :job_id
            AND
                /* One check to see if no cursor is specified */
                (:cursor_collection_id is NULL
                OR
                    (collection_id {sign}= :cursor_collection_id
                    AND
                        (collection_id {sign} :cursor_collection_id
                        OR
                            (granule_id {sign}= :cursor_granule_id
                            AND
                                (granule_id {sign} :cursor_granule_id
                                OR
                                    (key_path {sign} :cursor_key_path)
                                )
                            )
                        )
                    )
                )
        ORDER BY
            collection_id {order},
            granule_id {order},
            key_path {order}
        LIMIT :limit"""
        )

    @staticmethod
    def get_mismatch_page_sql(direction: DirectionEnum) -> text:  # pragma: no cover
        """
        SQL for retrieving a page of mismatches for a given job,
        ordered by collection_id, granule_id, then key_path.
        """
        if direction == DirectionEnum.previous:
            sign = "<"
            order = "DESC"
        else:
            sign = ">"
            order = "ASC"

        return text(  # nosec
            f"""
SELECT
    job_id,
    collection_id,
    granule_id,
    filename,
    key_path,
    cumulus_archive_location,
    orca_etag,
    s3_etag,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', orca_last_update)
     AT TIME ZONE 'UTC') * 1000)::bigint as orca_last_update,
    (EXTRACT(EPOCH FROM date_trunc('milliseconds', s3_last_update)
     AT TIME ZONE 'UTC') * 1000)::bigint as s3_last_update,
    orca_size_in_bytes,
    s3_size_in_bytes,
    storage_class.value AS orca_storage_class,
    s3_storage_class,
    discrepancy_type,
    CASE
        WHEN (reconcile_job.inventory_creation_time <= orca_last_update)
            THEN 'Error may be due to race condition, and should be checked manually.'
        WHEN (reconcile_job.inventory_creation_time <= s3_last_update)
            THEN 'Error may be due to race condition, and should be checked manually.'
    END AS comment
    FROM reconcile_catalog_mismatch_report
    INNER JOIN reconcile_job ON
    (
        reconcile_job.id = reconcile_catalog_mismatch_report.job_id
    )
    INNER JOIN storage_class ON
    (
        orca_storage_class_id=storage_class.id
    )
    WHERE
        job_id = :job_id
        AND
            /* One check to see if no cursor is specified */
            (:cursor_collection_id is NULL
            OR
                (collection_id {sign}= :cursor_collection_id
                AND
                    (collection_id {sign} :cursor_collection_id
                    OR
                        (granule_id {sign}= :cursor_granule_id
                        AND
                            (granule_id {sign} :cursor_granule_id
                            OR
                                (key_path {sign} :cursor_key_path)
                            )
                        )
                    )
                )
            )
    ORDER BY
        collection_id {order},
        granule_id {order},
        key_path {order}
    LIMIT :limit"""
        )
