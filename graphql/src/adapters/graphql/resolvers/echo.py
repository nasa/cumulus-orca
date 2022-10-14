import traceback

from src import use_cases
from src.adapters.graphql import initialized_adapters
from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType
from src.adapters.graphql.dataTypes.echo import GetEchoStrawberryResponse, \
    BoringWordExceptionStrawberryType
from src.entities.echo import BoringWordException
from src.use_cases.echo import Echo


def get_echo(word: str) -> GetEchoStrawberryResponse:
    # Acts as a translation layer to make Strawberry accept non-strawberry data classes.
    # noinspection PyTypeChecker
    try:
        return use_cases.echo.Echo(initialized_adapters.word_generation).get_echo(word)
    except BoringWordException as ex:
        return BoringWordExceptionStrawberryType(ex)
    except Exception as ex:
        return InternalServerErrorStrawberryType(ex)
