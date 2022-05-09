import time


class TimeMeasure:
    """
    Measure and process the time to tell other process with ZeroMQ communication, using `timeit`
    """

    @classmethod
    def get_process_time(cls) -> float:
        return time.process_time()
