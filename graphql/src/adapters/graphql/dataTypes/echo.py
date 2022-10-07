# noinspection PyPackageRequirements
import strawberry

from src.entities.common import Edge
from src.entities.echo import Echo


@strawberry.experimental.pydantic.type(model=Echo)
class EchoStrawberryType:  # todo: Find a better way to tie this to entities/echo.py
    word: strawberry.auto  # todo: Find a better way to tie this to entities/echo.py
    length: strawberry.auto  # todo: Find a better way to tie this to entities/echo.py
    echo: strawberry.auto  # todo: Find a better way to tie this to entities/echo.py

# todo: In this case, could use
# @strawberry.experimental.pydantic.type(model=Echo, all_fields=True)
# class EchoStrawberryType:
#     pass
# todo: so add one that uses an enum.


@strawberry.experimental.pydantic.type(model=Edge)
class EchoEdgeStrawberryType:
    node: EchoStrawberryType
    cursor: strawberry.auto
