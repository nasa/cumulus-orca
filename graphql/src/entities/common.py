from typing import Generic, TypeVar

from pydantic import BaseModel

GenericType = TypeVar("GenericType")


class Edge(BaseModel, Generic[GenericType]):
    """
    An edge contains additional information of the relationship. In this case
    the calculated cursor value for the node record.
    """
    node: GenericType
    cursor: str
