# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType, \
    ErrorStrawberryTypeInterface
from src.entities.common import Edge
from src.entities.echo import BoringWordException, Echo


@strawberry.type
class BoringWordExceptionStrawberryType(ErrorStrawberryTypeInterface):
    def __init__(self, ex: BoringWordException):
        self.message = f"{ex.word} is far too boring. Please try again."


GetEchoStrawberryResponse = strawberry.union(
    "GetEchoStrawberryResponse",
    [Edge[Echo], InternalServerErrorStrawberryType, BoringWordExceptionStrawberryType]
)
