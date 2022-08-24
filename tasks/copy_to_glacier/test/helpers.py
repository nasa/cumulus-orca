class LambdaContextMock:  # pylint: disable-msg=too-few-public-methods
    """
    create a lambda context for testing.
    """

    def __init__(self):
        self.function_name = "extract_filepaths_for_granule"
        self.function_version = 1
        self.invoked_function_arn = (
            "arn:aws:lambda:us-west-2:065089468788:"
            "function:extract_filepaths_for_granule:1"
        )
