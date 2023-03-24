import typing
import uuid
from typing import Annotated

# noinspection PyPackageRequirements
import strawberry

# noinspection PyPackageRequirements
from orca_shared.reconciliation import OrcaStatus
from strawberry import argument, field, type

from src.adapters.graphql.adapters import AdaptersStorage
from src.adapters.graphql.dataTypes.common import int8
from src.adapters.graphql.dataTypes.internal_reconcile_report import (
    CreateInternalReconciliationJobStrawberryResponse,
    ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse,
    UpdateInternalReconciliationJobStrawberryResponse,
)
from src.adapters.graphql.resolvers.internal_reconcile_report import (
    create_job,
    get_current_archive_list,
    perform_orca_reconcile,
    update_job,
)
from src.adapters.storage.internal_reconciliation_s3 import AWSS3FileLocation
from src.entities.internal_reconcile_report import ReconciliationStatus


@type
class Mutations:
    # Set in schemas.py,
    # can't use constructor due to Strawberry not accepting constructed classes.
    adapters_storage: strawberry.Private[AdaptersStorage]

    @field(
        description="""Creates a status entry for the internal reconciliation job.""")
    def post_internal_reconciliation_job(
        self,
        report_source: Annotated[
            str,
            argument(
                description="""The region covered by the report."""
            )
        ],
        creation_timestamp: Annotated[
            float,
            argument(
                description="""Seconds since UTC origin that the report was created."""
            )
        ],
    ) -> CreateInternalReconciliationJobStrawberryResponse:
        result = create_job(
            report_source,
            creation_timestamp,
            Mutations.adapters_storage.storage_internal_reconciliation,
            Mutations.adapters_storage.logger_provider.get_logger(
                uuid.uuid4().__str__()
            )
            )
        return result

    @field(
        description="""Updates the status entry for a job.""")
    def update_internal_reconciliation_job(
        self,
        report_cursor: Annotated[
            str,
            argument(
                description="""Cursor to the report to update."""
            )
        ],
        status: Annotated[
            ReconciliationStatus,
            argument(
                description="""The status to update the job with."""
            )
        ],
        error_message: Annotated[
            typing.Optional[str],  # `Optional` marks it as 'optional'...
            argument(
                description="""The error to post to the job, if any."""
            )
        ] = None,  # Default value actually MAKES it optional
    ) -> UpdateInternalReconciliationJobStrawberryResponse:
        return update_job(
            report_cursor,
            OrcaStatus(status.value),
            error_message,
            Mutations.adapters_storage.logger_provider.get_logger(
                uuid.uuid4().__str__()
            ),
            Mutations.adapters_storage.storage_internal_reconciliation,
        )

    @field(
        description="""Updates the status entry for a job.""")
    def import_current_archive_list_for_reconciliation_job(
        self,
        report_source: Annotated[
            str,
            argument(
                description="""The region covered by the report."""
            )
        ],
        report_cursor: Annotated[
            str,
            argument(
                description="""Cursor to the report to update."""
            )
        ],
        columns_in_csv: Annotated[
            typing.List[str],
            argument(
                description="""Columns in the csv files."""
            )
        ],
        csv_file_locations: Annotated[
            typing.List[AWSS3FileLocation],
            argument(
                description="""Locations of the csv files in the report."""
            )
        ],
        report_bucket_region: Annotated[
            str,
            argument(
                description="""Required by current Postgres driver."""
            )
        ],
    ) -> ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse:
        return get_current_archive_list(
            report_source,
            report_cursor,
            columns_in_csv,
            csv_file_locations,
            report_bucket_region,
            Mutations.adapters_storage.storage_internal_reconciliation,
            Mutations.adapters_storage.logger_provider.get_logger(
                uuid.uuid4().__str__()
            )
        )

    @field(
        description="""Generates reports for a given job.""")
    def perform_orca_reconcile_for_reconciliation_job(
        self,
        report_source: Annotated[
            str,
            argument(
                description="""The region covered by the report."""
            )
        ],
        report_cursor: Annotated[
            str,
            argument(
                description="""Cursor to the report to update."""
            )
        ],
    ) -> ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse:
        return perform_orca_reconcile(
            report_source,
            report_cursor,
            Mutations.adapters_storage.storage_internal_reconciliation,
            Mutations.adapters_storage.logger_provider.get_logger(
                uuid.uuid4().__str__()
            )
        )
