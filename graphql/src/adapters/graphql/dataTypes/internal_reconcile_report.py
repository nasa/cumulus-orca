# noinspection PyPackageRequirements
import typing

import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.entities.common import Page
from src.entities.internal_reconcile_report import (
    InternalReconcileReportCreationRecord,
    Mismatch,
    Phantom,
)

CreateInternalReconciliationJobStrawberryResponse = strawberry.union(
    "CreateInternalReconciliationJobStrawberryResponse",
    [InternalReconcileReportCreationRecord, InternalServerErrorGraphqlType]
)

UpdateInternalReconciliationJobStrawberryResponse = typing.Optional[InternalServerErrorGraphqlType]

ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse = \
    typing.Optional[InternalServerErrorGraphqlType]

PerformOrcaReconcileStrawberryResponse = \
    typing.Optional[InternalServerErrorGraphqlType]

GetPhantomPageStrawberryResponse = strawberry.union(
    "GetPhantomPageStrawberryResponse",
    [Page[Phantom], InternalServerErrorGraphqlType]
)

GetMismatchPageStrawberryResponse = strawberry.union(
    "GetMismatchPageStrawberryResponse",
    [Page[Mismatch], InternalServerErrorGraphqlType]
)
