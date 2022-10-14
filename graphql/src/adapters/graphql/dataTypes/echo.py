from enum import Enum

# noinspection PyPackageRequirements
import strawberry

from src.adapters.graphql.dataTypes.common import EdgeStrawberryType, \
    InternalServerErrorStrawberryType
from src.entities.echo import Echo


@strawberry.enum
class WordTypeEnumStrawberryType(Enum):
    # Whenever this class changes, update WordTypeEnum
    palindrome = 'palindrome'
    chaos = 'chaos'


@strawberry.type
class EchoStrawberryType(Echo):
    word_type: WordTypeEnumStrawberryType  # override type to help FastAPI out.
    pass


GetEchoStrawberryResponse = strawberry.union(
    "GetEchoResponse",
    [EdgeStrawberryType, InternalServerErrorStrawberryType]
)
