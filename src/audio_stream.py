import pprint
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
        self.block_size = int(sd.default.samplerate * 1)  # number of frames per callback
        self.stream = None

    def audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """
        This callback will be called from each audio block.
        Args:
            indata (np.ndarray): This is audio data whose shape will be (`self.block_size`, `sd.default.channels[0]`).
            frames:
            time:
            status:
        """
        if status:
            print("status: ", status, file=sys.stderr)
        # display number of buffer
        self.buffer.put(indata[::self.down_sample])
        # with self.buffer.mutex:
        #     print(len(self.buffer.queue))
        self.calc_f0(indata)

    def get_input_stream(self):
        return sd.InputStream(
            device=sd.default.device[0],
            callback=self.audio_callback,
            blocksize=self.block_size
        )
