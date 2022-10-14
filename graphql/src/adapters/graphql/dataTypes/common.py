# noinspection PyPackageRequirements
import strawberry
from abc import abstractmethod


class ErrorStrawberryType:
    """
    A basic error type to encourage inheritance and a consistent `message` property.
    """
    @property
    @abstractmethod
    def message(self) -> str:
        ...


@strawberry.type
class InternalServerErrorStrawberryType(ErrorStrawberryType):
    message: str = "An unexpected error has occurred. " \
                   "Please Contact the ORCA development team for more information."
    exception_message: str
    stack_trace: str

    def __init__(self, exception_message: str, stack_trace: str):
        self.exception_message = exception_message
        self.stack_trace = stack_trace
