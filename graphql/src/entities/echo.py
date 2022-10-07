from dataclasses import dataclass


@dataclass
class Echo:
    word: str
    length: int
    echo: str
