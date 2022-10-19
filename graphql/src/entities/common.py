from dataclasses import dataclass
from typing import Generic, TypeVar

import strawberry

GenericType = TypeVar("GenericType")


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclass
class Edge(Generic[GenericType]):
    """
    An edge contains additional information of the relationship. In this case
    the calculated cursor value for the node record.
    """
    node: GenericType
    cursor: str
