import matplotlib.pyplot as plt


class AudioController:
    """
    This class contains real-time audio controller such as matplotlib.
    """
    def __init__(self, audio_stream):
        self._audio_stream = audio_stream
