import traceback

# noinspection PyPackageRequirements
import strawberry


@strawberry.type
class InternalServerErrorStrawberryType:
    message: str = "An unexpected error has occurred. " \
                   "Please Contact the ORCA development team for more information."
    exception_message: str
    stack_trace: str

    def __init__(self, ex: Exception):
        self.exception_message = str(ex)
        self.stack_trace = traceback.format_exc()
