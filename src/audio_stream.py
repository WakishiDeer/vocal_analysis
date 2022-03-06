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
        self.down_sample = 20
        self.buffer = queue.Queue()
        self.stream = None

    def audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """
        This callback will be called from each audio block.
        """
        if status:
            print("status: ", status, file=sys.stderr)
        # self.buffer.put(indata[::self.down_sample])
        self.buffer.put(indata[:])
        # with self.buffer.mutex:
        #     print(self.buffer.queue)

    def get_input_stream(self):
        return sd.InputStream(
            device=sd.default.device[0],
            callback=self.audio_callback
        )
