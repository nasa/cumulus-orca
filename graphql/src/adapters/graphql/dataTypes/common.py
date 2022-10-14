import traceback
# noinspection PyPackageRequirements
import strawberry
from abc import abstractmethod


class ErrorStrawberryType:
    """
    A basic error type to encourage inheritance and a consistent `message` property.
    """
    # todo: Better abstraction? Might not be doable. In that case, maybe just remove.
    def message(self) -> str:
        ...


@strawberry.type
class InternalServerErrorStrawberryType(ErrorStrawberryType):
    message: str = "An unexpected error has occurred. " \
                   "Please Contact the ORCA development team for more information."
    exception_message: str
    stack_trace: str

    def __init__(self, ex: Exception):
        self.exception_message = str(ex)
        self.stack_trace = traceback.format_exc()
