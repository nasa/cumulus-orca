from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, List
import typing

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
    start_cursor: typing.Optional[str]
    end_cursor: typing.Optional[str]


@strawberry.enum  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
class DirectionEnum(str, Enum):
    # Whenever this class changes, update WordTypeEnumGraphqlType
    next = 'next'
    previous = 'previous'


@strawberry.input  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclass
class PageParameters:
    """
    A page contains multiple records plus string cursor values for the first and last elements.
    """
    cursor: typing.Optional[str] = None
    direction: DirectionEnum = DirectionEnum.next
    limit: int = 100  # todo: Docs suggest ceiling, but don't know what that should be.
