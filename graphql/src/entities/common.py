from dataclasses import dataclass
from typing import Generic, TypeVar

GenericType = TypeVar("GenericType")


@dataclass
class Edge(Generic[GenericType]):
    """
    An edge contains additional information of the relationship. In this case
    the calculated cursor value for the node record.
    """
    node: GenericType
    cursor: str
