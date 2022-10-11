# noinspection PyPackageRequirements
from enum import Enum

import strawberry

from src.entities.echo import Echo


# todo: While it technically breaks CleanArchitecture,
#  I wonder if we wouldn't be fine placing these decorators on the base class
#  given that they don't change behavior.


@strawberry.enum
class WordTypeEnumStrawberryType(str, Enum):
    # Whenever this class changes, update WordTypeEnum
    palindrome = 'palindrome'
    chaos = 'chaos'


@strawberry.type
class EchoStrawberryType(Echo):
    word_type: WordTypeEnumStrawberryType  # override type to help FastAPI out.
    pass
