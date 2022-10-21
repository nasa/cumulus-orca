from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType
from src.adapters.graphql.dataTypes.sample import BoringWordExceptionStrawberryType, \
    GetEchoStrawberryResponse
from src.adapters.graphql.initialized_adapters.adapters import word_generation
from src.entities.echo import BoringWordException
from src.use_cases.sample import Test


def get_echo(word: str) -> GetEchoStrawberryResponse:
    # noinspection PyTypeChecker
    echo = None
    error = None
    try:
        echo = Test(word_generation).get_echo(word)
    except BoringWordException as ex:
        error = BoringWordExceptionStrawberryType(ex)
    except Exception as ex:
        error = InternalServerErrorStrawberryType(ex)

    errors = []
    if error is not None:
        errors.append(error)
    return GetEchoStrawberryResponse(response=echo, error=error)
