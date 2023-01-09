import uuid

from src.use_cases.adapter_interfaces.word_generation import WordGenerationInterface


class UUIDWordGeneration(WordGenerationInterface):
    def get_random_word(self) -> str:
        word = uuid.uuid4().__str__()
        return word[:len(word)//2]
