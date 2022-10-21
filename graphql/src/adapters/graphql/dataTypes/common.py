import traceback

from dataclasses import dataclass
from typing import Generic

# noinspection PyPackageRequirements
import strawberry

from src.entities.common import GenericType


# alternate error logic approaches:
# https://productionreadygraphql.com/2020-08-01-guide-to-graphql-errors
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
