# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType, \
    ErrorStrawberryType
from src.entities.common import Edge
from src.entities.echo import Echo, BoringWordException


@strawberry.type
class BoringWordExceptionStrawberryType(ErrorStrawberryType):
    message: str

    def __init__(self, ex: BoringWordException):
        self.message = f"{ex.word} is far too boring. Please try again."


GetEchoStrawberryResponse = strawberry.union(
    "GetEchoResponse",
    [Edge[Echo], InternalServerErrorStrawberryType, BoringWordExceptionStrawberryType]
)
