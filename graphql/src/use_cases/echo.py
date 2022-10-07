from src import entities
from src.entities.common import Edge
from src.entities.echo import Echo as EchoEntity  # todo: Use a better naming scheme so this isn't an issue.
from src.use_cases.edge_cursor import EdgeCursor


class Echo:
    def __init__(self):
        pass

    @staticmethod
    def _create_cursor(echo: entities.echo.Echo) -> str:
        """
        """
        # Create the filter for the cursor based on the record information
        # and the original filter used to obtain the information.
        return EdgeCursor.encode_cursor(**{"word": echo.word})

    def get_echo(self, word: str) -> Edge:
        # todo: This constructor has no type hints, or even name hints. Find an alternative.
        result = EchoEntity(word=word, length=len(word), echo=(word[::-1]))
        # todo: This constructor has no type hints, or even name hints. Find an alternative.
        return Edge(node=result, cursor=self._create_cursor(result))
