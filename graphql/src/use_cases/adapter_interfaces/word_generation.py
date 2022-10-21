class WordGenerationInterface:
    """
    Sample interface for abstracting an adapter for use in use_cases

    Generic randomizer class with method that needs to be implemented by an adapter.
    """

    def get_random_word(self) -> str: ...
