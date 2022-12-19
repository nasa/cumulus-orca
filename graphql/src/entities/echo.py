import dataclasses
from enum import Enum

import pydantic

# noinspection PyPackageRequirements
import strawberry


@strawberry.enum  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
class WordTypeEnum(str, Enum):
    # Whenever this class changes, update WordTypeEnumGraphqlType
    palindrome = 'palindrome'
    chaos = 'chaos'


@strawberry.type  # Not strictly clean, but alternative is duplicating classes in graphql adapter.
@dataclasses.dataclass
class Echo(pydantic.BaseModel):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    word: str
    length: int
    echo: str
    word_type: WordTypeEnum

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self, word: str, length: int, echo: str, word_type: WordTypeEnum):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(word=word, length=length, echo=echo, word_type=word_type)


class BoringWordException(Exception):
    def __init__(self, word: str):
        self.word = word
