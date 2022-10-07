from typing import Generic

# noinspection PyPackageRequirements
import strawberry

from src.entities.common import Edge, GenericType


@strawberry.type
class EdgeStrawberryType(Edge, Generic[GenericType]):
    pass
