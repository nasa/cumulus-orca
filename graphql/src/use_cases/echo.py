import random
import uuid

import src.entities.echo
from src import entities
from src.entities.common import Edge
from src.use_cases.adapter_interfaces.word_generation import WordGenerationInterface
from src.use_cases.edge_cursor import EdgeCursor
from src.entities.echo import BoringWordException


class Echo:
    def __init__(self, word_generation: WordGenerationInterface):
        self.word_generator = word_generation

    @staticmethod
    def _create_cursor(echo: entities.echo.Echo) -> str:
        """
        Creates a filter for the cursor based on the record information
        and the original filter used to obtain the information.

        Args:
            echo: The element to create a cursor for.

        Returns:
            A cursor that will always point to the given element.
        """
        return EdgeCursor.encode_cursor(**{"word": echo.word})

    def get_echo(self, word: str) -> Edge[entities.echo.Echo]:
        if word is None or word is "":
            word = self.word_generator.get_random_word()

        if random.randint(0, 10) == 5:
            raise Exception("Whoops, random error.")

        if word == len(word) * word[0]:
            raise BoringWordException(word)

        echo = (word[::-1])
        result = entities.echo.Echo(word=word, length=len(word), echo=echo,
                                    word_type=src.entities.echo.WordTypeEnum.palindrome
                                    if word == echo else
                                    src.entities.echo.WordTypeEnum.chaos)
        return Edge(node=result, cursor=self._create_cursor(result))
