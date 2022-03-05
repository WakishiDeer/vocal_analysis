import queue
import sys

import numpy as np

from audio import Audio
from audio import sd


class AudioStream(Audio):
    """
    This class controls audio coming from audio device (microphone), using `Python-sounddevice.`
    Note that your available audio device could be list by just write `$ python -m sounddevice`
    And an instance of this class will be used in `AudioController` class in `audio_plotter.py`
    """

    def __init__(self):
        """
        Initialize sound device to decide which one to select for audio stream.
        """
        super().__init__()
        # setting for input device
        self.set_input_device()

        self.duration = 5.0
        self.window = 200.0
        self.interval = 30.0
        self.block_size = 0
        self.samplerate = 44100.0
        self.down_sample = 10
        self.channels = [1]
        # self.mapping
        self.buffer = queue.Queue()
        self.stream = None

    def audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """
        This callback will be called from each audio block.
        """
        if status:
            print(status, file=sys.stderr)
        self.buffer.put(indata[::self.down_sample])

    def get_input_stream(self):
        return sd.InputStream(
            device=sd.default.device[0],
            callback=self.audio_callback
        )
