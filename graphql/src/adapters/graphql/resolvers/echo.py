from src import use_cases
from src.adapters.graphql.dataTypes.common import EdgeStrawberryType
from src.use_cases.echo import Echo


def get_echo(word: str) -> EdgeStrawberryType:
    # Acts as a translation layer to make Strawberry accept non-strawberry data classes.
    # noinspection PyTypeChecker
    return use_cases.echo.Echo().get_echo(word)
