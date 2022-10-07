# noinspection PyPackageRequirements
import strawberry

from src.entities.common import Edge
from src.entities.echo import Echo


@strawberry.type
class EchoStrawberryType(Echo):
    pass
