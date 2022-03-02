import matplotlib.pyplot as plt


class AudioController:
    """
    This class contains realtime audio controller such as matplotlib.
    Args:
        self._audio_stream (object): The instance of audio stream from AudioStream Class,
        which will be used to plot or calculate streaming data.
    """

    def __init__(self, audio_stream):
        self._audio_stream = audio_stream
