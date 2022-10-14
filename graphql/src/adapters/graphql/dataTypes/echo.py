# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType
from src.entities.common import Edge
from src.entities.echo import Echo

GetEchoStrawberryResponse = strawberry.union(
    "GetEchoResponse",
    [Edge[Echo], InternalServerErrorStrawberryType]
)
