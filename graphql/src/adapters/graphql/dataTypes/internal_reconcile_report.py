# noinspection PyPackageRequirements
import typing

import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.entities.common import Page
from src.entities.internal_reconcile_report import Mismatch, Phantom, \
    InternalReconcileReportCursorOutput

CreateInternalReconciliationJobStrawberryResponse = strawberry.union(
    "CreateInternalReconciliationJobStrawberryResponse",
    [InternalReconcileReportCursorOutput, InternalServerErrorGraphqlType]
)

UpdateInternalReconciliationJobStrawberryResponse = typing.Optional[InternalServerErrorGraphqlType]

ImportCurrentArchiveListInternalReconciliationJobStrawberryResponse = typing.Optional[InternalServerErrorGraphqlType]

GetPhantomPageStrawberryResponse = strawberry.union(
    "GetPhantomPageStrawberryResponse",
    [Page[Phantom], InternalServerErrorGraphqlType]
)

GetMismatchPageStrawberryResponse = strawberry.union(
    "GetMismatchPageStrawberryResponse",
    [Page[Mismatch], InternalServerErrorGraphqlType]
)
