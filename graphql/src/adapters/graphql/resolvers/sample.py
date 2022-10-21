from src.adapters.graphql.dataTypes.common import InternalServerErrorStrawberryType
from src.adapters.graphql.dataTypes.sample import BoringWordExceptionStrawberryType, \
    GetEchoStrawberryResponse
from src.adapters.graphql.initialized_adapters.adapters import word_generation
from src.entities.echo import BoringWordException
from src.use_cases.sample import Test


def get_echo(word: str) -> GetEchoStrawberryResponse:
    try:
        return Test(word_generation).get_echo(word)
    except BoringWordException as ex:
        return BoringWordExceptionStrawberryType(ex)
    except Exception as ex:
        return InternalServerErrorStrawberryType(ex)
