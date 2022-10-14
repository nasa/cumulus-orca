# noinspection PyPackageRequirements
import strawberry


@strawberry.type
class InternalServerErrorStrawberryType:
    message: str

    def __init__(self, message: str):
        self.message = message
