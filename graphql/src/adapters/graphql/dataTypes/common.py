from typing import Generic

# noinspection PyPackageRequirements
import strawberry

from src.entities.common import Edge, GenericType


@strawberry.type
class InternalServerErrorStrawberryType(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


@strawberry.type
class EdgeStrawberryType(Edge, Generic[GenericType]):
    pass
