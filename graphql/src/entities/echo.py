from pydantic import BaseModel


class Echo(BaseModel):
    word: str
    length: int
    echo: str

