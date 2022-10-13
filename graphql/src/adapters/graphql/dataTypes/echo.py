from enum import Enum

# noinspection PyPackageRequirements
import strawberry

from src.entities.echo import Echo


# todo: While it technically breaks CleanArchitecture,
#  I wonder if we wouldn't be fine placing these decorators on the base class
#  given that they don't change coding behavior.


@strawberry.enum
class WordTypeEnumStrawberryType(Enum):
    # Whenever this class changes, update WordTypeEnum
    palindrome = 'palindrome'
    chaos = 'chaos'


@strawberry.type
class EchoStrawberryType(Echo):
    word_type: WordTypeEnumStrawberryType  # override type to help FastAPI out.
    pass
