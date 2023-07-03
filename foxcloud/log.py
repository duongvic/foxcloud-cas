import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def setup_logging(name):
    log = logging.getLogger(name)
    if len(log.handlers) == 0:
        h = NullHandler()
        log.addHandler(h)
    return log