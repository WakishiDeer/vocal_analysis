import queue

from audio import Audio
import sounddevice as sd


class AudioStream(Audio):
    """
    This class controls audio coming from audio device (microphone), using `Python-sounddevice.`
    Note that your available audio device could be list by just write `$ python -m sounddevice`
    And an instance of this class will be used in `AudioController` class in `audio_controller.py`
    """

    def __init__(self):
        """
        Initialize sound device to decide which one to select for audio stream.
        """
        sd.default.device = 0
        buffer = queue.Queue

    def query_available_sound_input(self):
        pass

    def audio_callback(self, incoming_data, frames, time, status):
        """
        This callback will be called from each audio block.
        """
        pass
