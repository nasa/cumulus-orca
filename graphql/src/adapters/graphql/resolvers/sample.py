import logging

from src.adapters.graphql.dataTypes.common import InternalServerErrorGraphqlType
from src.adapters.graphql.dataTypes.sample import (
    BoringWordExceptionGraphqlType,
    GetEchoStrawberryResponse,
)
from src.entities.echo import BoringWordException
from src.use_cases.adapter_interfaces.word_generation import WordGenerationInterface
from src.use_cases.sample import Test


def get_echo(word: str, word_generation: WordGenerationInterface, logger: logging.Logger) \
        -> GetEchoStrawberryResponse:
    try:
        return Test(word_generation).get_echo(word, logger)
    except BoringWordException as ex:
        logger.exception(ex)  # todo: expand to production code.
        return BoringWordExceptionGraphqlType(ex)
    except Exception as ex:
        logger.exception(ex)
        return InternalServerErrorGraphqlType(ex)
