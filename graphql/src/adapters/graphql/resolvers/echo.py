from src import use_cases
from src.entities.common import Edge
from src.use_cases.echo import Echo


# todo: Does this really need its own file?
def get_echo(word: str) -> Edge:  # todo: look further into just how many files `echo` functionality is pathed.
    return use_cases.echo.Echo().get_echo(word)
