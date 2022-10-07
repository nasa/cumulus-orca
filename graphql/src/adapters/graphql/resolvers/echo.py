from src import use_cases
from src.adapters.graphql.dataTypes.echo import EchoEdgeStrawberryType
from src.use_cases.echo import Echo


# todo: Does this really need its own file?
def get_echo(word: str) -> EchoEdgeStrawberryType:  # todo: look further into just how many files `echo` functionality is pathed.
    return EchoEdgeStrawberryType.from_pydantic(use_cases.echo.Echo().get_echo(word))
