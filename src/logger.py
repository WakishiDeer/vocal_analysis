import logging


class Logger:
    """
    This class defines the format of logger.
    """

    def __init__(self, name: str):
        # logger setting
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        # adding formatter
        formatter = logging.Formatter(
            '%(levelname)-8s: %(asctime)s | %(filename)-12s - %(funcName)-12s : %(lineno)-4s -- %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        stream_handler.setFormatter(formatter)
        # adding handler
        self.logger.addHandler(stream_handler)
