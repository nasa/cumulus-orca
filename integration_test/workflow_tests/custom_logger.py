import logging


class CustomLoggerAdapter(logging.LoggerAdapter):
    # example taken from
    # https://stackoverflow.com/questions/39467271/cant-get-this-custom-logging-adapter-example-to-work
    def process(self, msg, kwargs):
        my_context = kwargs.pop('my_context', self.extra['my_context'])
        return f"[{my_context}] {msg}", kwargs

    def set_logger(group_name):
        logger = logging.getLogger(__name__)
        syslog = logging.StreamHandler()
        logger.addHandler(syslog)
        logger_adapter = CustomLoggerAdapter(logger, {'my_context': group_name})
        return logger_adapter
