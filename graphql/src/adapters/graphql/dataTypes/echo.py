# noinspection PyPackageRequirements
import strawberry

from src.entities.echo import Echo


@strawberry.type
class EchoStrawberryType(Echo):
    pass
