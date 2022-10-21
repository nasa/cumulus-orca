import traceback

# noinspection PyPackageRequirements
from dataclasses import dataclass
from typing import Generic

import strawberry

from src.entities.common import GenericType


@strawberry.interface
class ErrorStrawberryTypeInterface:
    message: str


@strawberry.type
class InternalServerErrorStrawberryType(ErrorStrawberryTypeInterface):
    exception_message: str
    stack_trace: str

    def __init__(self, ex: Exception):
        self.message = "An unexpected error has occurred. " \
                       "Please review the logs and contact support if needed."
        self.exception_message = str(ex)
        self.stack_trace = traceback.format_exc()


@strawberry.type
@dataclass
class ResponseStrawberryType(Generic[GenericType]):
    """
    A generic structure to standardize returning either a response or an error.
    """
    response: GenericType
    error: ErrorStrawberryTypeInterface
