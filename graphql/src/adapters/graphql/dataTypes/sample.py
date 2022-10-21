# noinspection PyPackageRequirements
import dataclasses
from typing import Optional, List

import strawberry

from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType, \
    ErrorStrawberryTypeInterface
from src.entities.common import Edge
from src.entities.echo import BoringWordException, Echo


@strawberry.type
class BoringWordExceptionStrawberryType(ErrorStrawberryTypeInterface):
    def __init__(self, ex: BoringWordException):
        self.message = f"{ex.word} is far too boring. Please try again."


GetEchoStrawberryErrors = strawberry.union(
    "GetEchoErrors",
    [InternalServerErrorStrawberryType, BoringWordExceptionStrawberryType]
)


@strawberry.type
@dataclasses.dataclass
class GetEchoStrawberryResponse:
    response: Optional[Edge[Echo]]
    error: Optional[GetEchoStrawberryErrors]  # todo: add recommendation to docs to ALWAYS request ErrorStrawberryTypeInterface with __typename and message properties
