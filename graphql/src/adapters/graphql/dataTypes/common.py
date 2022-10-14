# noinspection PyPackageRequirements
import strawberry


@strawberry.type
class InternalServerErrorStrawberryType(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
