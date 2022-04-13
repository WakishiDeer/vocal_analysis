import numpy as np
import auditok

import queue

from util.profile import Profile
from util.exception import *
from util import sd
from audio import Audio


class AudioStream(Audio):
    """
    This class controls audio_util coming from audio_util device (microphone), using `Python-sounddevice.`
    Note that your available audio_util device could be list by just write `$ python -m sounddevice`
    And an instance of this class will be used in `AudioController` class in `audio_handler.py`
    """

    def __init__(self, audio_manipulator=None):
        """
        Initialize sound device to decide which one to select for audio_util stream.
        """
        super().__init__(audio_manipulator=audio_manipulator)

        try:
            if not Profile.is_input_device_set:
                raise DefaultInputDeviceException
        except DefaultInputDeviceException:
            self.logger.exception("Setting for input device hasn't done yet.")
        else:
            # setting for input device
            self.DOWN_SAMPLE = 20
            self.CHUNK_DURATION_MS = 25 * 40 * 5
            self.BLOCK_SIZE = int(  # number of frames per callback
                self.audio_manipulator.INPUT_SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
            self.buffer = queue.Queue()
            self.region_concat = None  # `auditok.AudioRegion` can use operator `+` to concatenate
            self.region_concat_energy = None
            self.is_init = True  # this is for `self.region_concat` to initialize
            self.stream = None

            import atexit
            atexit.register(self.save_region)

    def audio_callback_numpy(self, indata: np.ndarray, frames: int, time, status):
        """
        This callback will be called from each audio_util block.
        Args:
            indata (np.ndarray): This is audio_util data whose shape will be (`self.block_size`, `sd.default.channels[0]`).
            frames:
            time:
            status:
        """
        self.buffer.put(indata[::self.DOWN_SAMPLE])
        vad_generator = self.audio_manipulator.vad_generator(audio_data=indata,
                                                             max_dur_sec=self.CHUNK_DURATION_MS / 1000)
        s = str()
        # for each voiced region
        for i, region in enumerate(vad_generator):
            # calculate energy
            energy = self.audio_manipulator.calc_energy(voiced_audio_data=region.samples, sample_width=2)
            if self.is_init:
                self.region_concat = region
                self.region_concat_energy = np.array([energy])
                self.is_init = False
            else:
                s += "#{} region: {}sec detected.\n".format(i, region.duration)
                # store voiced regions and energy
                self.region_concat = region + self.region_concat
                self.region_concat_energy = np.append(self.region_concat_energy, energy)
                print(self.region_concat_energy)
        print(s, "\n")

    def audio_callback_raw(self, indata, frames: int, time, status):
        self.audio_manipulator.voice_activity_detection(audio_buf=indata)

    def get_input_stream_numpy(self):
        return sd.InputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_numpy,
            blocksize=self.BLOCK_SIZE
        )

    def get_input_stream_raw(self):
        return sd.RawInputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_raw,
            blocksize=self.BLOCK_SIZE
        )

    def save_region(self):
        """
        When exiting, save the voiced audio regions, which is concatenated.
        Returns:
        """
        self.audio_manipulator.save_wav_auditok(audio_region=self.region_concat)
