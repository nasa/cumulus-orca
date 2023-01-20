import logging

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.adapters.graphql.dataTypes.internal_reconcile_report import (
    GetMismatchPageStrawberryResponse, GetPhantomPageStrawberryResponse,
)
from src.entities.common import PageParameters
from src.use_cases.adapter_interfaces.storage import (
    StorageInternalReconcileReportInterface,
)
from src.use_cases.internal_reconcile_report import InternalReconcileReport


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
        return InternalServerErrorGraphqlType(ex)
