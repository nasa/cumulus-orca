import logging


class CustomLoggerAdapter(logging.LoggerAdapter):
    # example taken from
    # https://stackoverflow.com/questions/39467271/cant-get-this-custom-logging-adapter-example-to-work
    def process(self, msg, kwargs):
        my_context = kwargs.pop('my_context', self.extra['my_context'])
        return f"[{my_context}] {msg}", kwargs

    @staticmethod
    def set_logger(group_name):
        logger = logging.getLogger(__name__)
        #logger.propagate = False
        logger_adapter = CustomLoggerAdapter(logger, {"my_context": group_name})
        if not logger.handlers:
            syslog = logging.StreamHandler()
            logger.addHandler(syslog)
        return logger_adapter
