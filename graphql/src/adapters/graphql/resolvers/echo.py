from src import use_cases
from src.adapters.graphql import initialized_adapters
from src.adapters.graphql.dataTypes.common import EdgeStrawberryType
from src.adapters.graphql.dataTypes.echo import EchoStrawberryType
from src.use_cases.echo import Echo


def get_echo(word: str) -> EdgeStrawberryType[EchoStrawberryType]:
    # Acts as a translation layer to make Strawberry accept non-strawberry data classes.
    # noinspection PyTypeChecker
    return use_cases.echo.Echo(initialized_adapters.word_generation).get_echo(word)
