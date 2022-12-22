from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, List

# noinspection PyPackageRequirements
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


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclass
class Page(Generic[GenericType]):
    """
    A page contains multiple records plus string cursor values for the first and last elements.
    """
    items: List[GenericType]
    start_cursor: str
    end_cursor: str


@strawberry.enum  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
class DirectionEnum(str, Enum):
    # Whenever this class changes, update WordTypeEnumGraphqlType
    next = 'next'
    previous = 'previous'


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclass
class PageParameters:
    """
    A page contains multiple records plus string cursor values for the first and last elements.
    """
    cursor: str = None
    direction: DirectionEnum = next
    limit: int = None  # todo: Set default in resolver or some other level
