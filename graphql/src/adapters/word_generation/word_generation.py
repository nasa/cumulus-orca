import uuid

from src.use_cases.adapter_interfaces.word_generation import WordGenerationInterface


class UUIDWordGeneration(WordGenerationInterface):
    def get_random_word(self) -> str:
        return uuid.uuid4().__str__()
