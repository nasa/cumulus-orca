import dataclasses

import pydantic


@dataclasses.dataclass
class Echo(pydantic.BaseModel):
    # IMPORTANT: Whenever properties are added/removed/modified/renamed, update constructor.
    word: str
    length: int
    echo: str

    # Overriding constructor to give us type/name hints for Pydantic class.
    def __init__(self, word: str, length: int, echo: str):
        # This call to __init__ will NOT automatically update when performing renames.
        super().__init__(word=word, length=length, echo=echo)
