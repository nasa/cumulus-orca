import logging
from typing import List, Optional

from orca_shared.reconciliation import OrcaStatus

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.adapters.graphql.dataTypes.internal_reconcile_report import (
    CreateInternalReconciliationJobStrawberryResponse,
    GetMismatchPageStrawberryResponse,
    GetPhantomPageStrawberryResponse,
    ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse,
    PerformOrcaReconcileStrawberryResponse,
)
from src.entities.common import PageParameters
from src.entities.files import FileLocation
from src.entities.internal_reconcile_report import InternalReconcileReportCursor
from src.use_cases.adapter_interfaces.storage import (
    InternalReconcileGenerationStorageInterface,
    StorageInternalReconcileReportInterface,
)
from src.use_cases.helpers.edge_cursor import EdgeCursor
from src.use_cases.internal_reconcile_generation import InternalReconcileGeneration
from src.use_cases.internal_reconcile_report import InternalReconcileReport


def create_job(
    report_source: str,
    creation_timestamp: float,
    storage_irr: InternalReconcileGenerationStorageInterface,
    logger: logging.Logger,
) -> CreateInternalReconciliationJobStrawberryResponse:
    try:
        result = InternalReconcileGeneration(storage_irr) \
            .create_job(report_source, creation_timestamp, logger)
        return result
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)


def update_job(
    report_cursor: str,
    status: OrcaStatus,
    error_message: Optional[str],
    storage_irr: InternalReconcileGenerationStorageInterface,
    logger: logging.Logger,
) -> Optional[InternalServerErrorGraphqlType]:
    try:
        cursor = EdgeCursor.decode_cursor(report_cursor, InternalReconcileReportCursor)
        InternalReconcileGeneration(storage_irr) \
            .update_job(cursor, status, error_message)
        return
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)


def get_current_archive_list(
    report_source: str,
    report_cursor: str,
    columns_in_csv: List[str],
    csv_file_locations: List[FileLocation],
    report_bucket_region: str,
    storage_irr: InternalReconcileGenerationStorageInterface,
    logger: logging.Logger,
) -> ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse:
    try:
        cursor = EdgeCursor.decode_cursor(report_cursor, InternalReconcileReportCursor)
        InternalReconcileGeneration(storage_irr) \
            .get_current_archive_list(
            report_source,
            cursor,
            columns_in_csv,
            csv_file_locations,
            report_bucket_region,
            logger,
        )
        return
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)


def perform_orca_reconcile(
    report_source: str,
    report_cursor: str,
    storage_irr: InternalReconcileGenerationStorageInterface,
    logger: logging.Logger,
) -> PerformOrcaReconcileStrawberryResponse:
    try:
        InternalReconcileGeneration(storage_irr) \
            .perform_orca_reconcile(
            report_source,
            EdgeCursor.decode_cursor(report_cursor, InternalReconcileReportCursor),
            logger,
        )
        return
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)


def get_phantom_page(
    job_id: int,
    page_parameters: PageParameters,
    storage_irr: StorageInternalReconcileReportInterface,
    logger: logging.Logger,
) -> GetPhantomPageStrawberryResponse:
    try:
        return InternalReconcileReport(storage_irr) \
            .get_phantom_page(job_id, page_parameters, logger)
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)


def get_mismatch_page(
    job_id: int,
    page_parameters: PageParameters,
    storage_irr: StorageInternalReconcileReportInterface,
    logger: logging.Logger,
) -> GetMismatchPageStrawberryResponse:
    try:
        return InternalReconcileReport(storage_irr) \
            .get_mismatch_page(job_id, page_parameters, logger)
    except Exception as ex:
        logger.error(ex)
        return InternalServerErrorGraphqlType(ex)
