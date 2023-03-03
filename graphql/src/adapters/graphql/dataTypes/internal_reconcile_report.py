# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.entities.common import Page
from src.entities.internal_reconcile_report import Mismatch, Phantom, InternalReconcileReportCursor

CreateJobStrawberryResponse = strawberry.union(
    "InternalReconciliationCreateJobStrawberryResponse",
    [InternalReconcileReportCursor, InternalServerErrorGraphqlType]
)

GetPhantomPageStrawberryResponse = strawberry.union(
    "GetPhantomPageStrawberryResponse",
    [Page[Phantom], InternalServerErrorGraphqlType]
)

GetMismatchPageStrawberryResponse = strawberry.union(
    "GetMismatchPageStrawberryResponse",
    [Page[Mismatch], InternalServerErrorGraphqlType]
)
