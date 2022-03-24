import pprint
import queue
import sys

import numpy as np

from profile import Profile
from audio import Audio
from audio import sd


class AudioStream(Audio):
    """
    This class controls audio coming from audio device (microphone), using `Python-sounddevice.`
    Note that your available audio device could be list by just write `$ python -m sounddevice`
    And an instance of this class will be used in `AudioController` class in `audio_handler.py`
    """

    def __init__(self, audio_manipulator=None):
        """
        Initialize sound device to decide which one to select for audio stream.
        """
        super().__init__(audio_manipulator=audio_manipulator)

        from exception import DefaultInputDeviceException
        try:
            if not Profile.is_input_device_set:
                raise DefaultInputDeviceException
        except DefaultInputDeviceException:
            self.logger.exception("Setting for input device hasn't done yet.")
        else:
            # setting for input device
            self.DOWN_SAMPLE = 20
            self.CHUNK_DURATION_MS = 25
            self.BLOCK_SIZE = int(  # number of frames per callback
                self.audio_manipulator.INPUT_SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
            self.buffer = queue.Queue()
            self.stream = None

    def audio_callback_numpy(self, indata: np.ndarray, frames: int, time, status):
        """
        This callback will be called from each audio block.
        Args:
            indata (np.ndarray): This is audio data whose shape will be (`self.block_size`, `sd.default.channels[0]`).
            frames:
            time:
            status:
        """
        # if status:
        #     print("status: ", status, file=sys.stderr)
        # display number of buffer
        self.buffer.put(indata[::self.DOWN_SAMPLE])
        self.audio_manipulator.voice_activity_detection(
            audio_data=indata)

    def audio_callback_raw(self, indata, frames: int, time, status):
        self.audio_manipulator.voice_activity_detection(audio_buf=indata)

    def get_input_stream_numpy(self):
        return sd.InputStream(
            dtype="float32",
            device=sd.default.device[0],
            callback=self.audio_callback_numpy,
            blocksize=self.BLOCK_SIZE
        )

    def get_input_stream_raw(self):
        return sd.RawInputStream(
            dtype="float32",
            device=sd.default.device[0],
            callback=self.audio_callback_raw,
            blocksize=self.BLOCK_SIZE
        )
