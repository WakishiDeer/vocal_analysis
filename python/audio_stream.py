import numpy as np

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

    def __init__(self, audio_manipulator=None, audio_calculator=None):
        """
        Initialize sound device to decide which one to select for audio_util stream.
        """
        super().__init__(audio_manipulator=audio_manipulator, audio_calculator=audio_calculator)

        try:
            if not Profile.is_input_device_set:
                raise DefaultInputDeviceException
        except DefaultInputDeviceException:
            self.logger.exception("Setting for input device hasn't done yet.")
        else:
            # setting for input device
            self.DOWN_SAMPLE = 20
            self.CHUNK_DURATION_MS = 25 * 40 * 5
            self.FRAME_LENGTH = int(  # number of overall frames per callback
                self.audio_manipulator.INPUT_SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
            self.WINDOW_LENGTH = 512  # length for each sliding process
            self.HOP_LENGTH = self.WINDOW_LENGTH // 4  # usually, one-fourth of WINDOW_LENGTH
            self.buffer = queue.Queue()  # this is for plot
            self.region_concat = None  # `auditok.AudioRegion` can use operator `+` to concatenate
            self.region_concat_energy = None
            self.stream = None

            # when exiting, save the voiced region for sample
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
        # store all data including both silence and voice
        self.audio_data = np.append(self.audio_data, indata)
        # calculate
        self.handle_calculation(indata=indata)

    def audio_callback_raw(self, indata, frames: int, time, status):
        pass

    def handle_calculation(self, indata: np.ndarray = None):
        """
        This class specifies calculation for each callback (i.e., for each block)
        Args:
            indata (np.ndarray): This is audio_util data whose shape will be (`self.block_size`, `sd.default.channels[0]`).
        Returns:
        """
        # for each voiced region
        vad_generator = self.audio_calculator.vad_generator(audio_data=indata,
                                                            max_dur_sec=self.CHUNK_DURATION_MS / 1000)
        region_info = str()
        root_energy = None
        for i, region in enumerate(vad_generator):
            # get values represented as np.ndarray
            voiced_audio_data = self.audio_manipulator.int_to_float32(audio_data=region.samples)
            # calc stft
            is_freq, voiced_audio_data_freq = self.audio_calculator.calc_short_time_fourier_transform(
                voiced_audio_data=voiced_audio_data,
                n_fft=self.WINDOW_LENGTH)
            # separate complex-valued data into magnitude and phase
            magnitude, phase = self.audio_calculator.calc_magphase(voiced_audio_data_freq=voiced_audio_data_freq)
            # calculate energy
            root_energy = self.audio_calculator.calc_energy_rms(magnitude=magnitude,
                                                                frame_length=512,
                                                                is_freq=is_freq)
            region_info += "#{} region: {}sec detected.\n".format(i, region.duration)
            # switch on the first time or not
            if Profile.is_init:
                self.region_concat = region
                self.region_concat_energy = np.array([root_energy])
                Profile.is_writable = True
                Profile.is_init = False
            else:
                # store voiced regions and energy
                self.region_concat = region + self.region_concat
                self.region_concat_energy = np.append(self.region_concat_energy, root_energy)
        if region_info is not "":
            self.logger.logger.info(region_info)
            print("avg rms of energy: ",
                  self.audio_calculator.calc_average_energy_rms(root_energy=root_energy),
                  "\n")

    def store_values(self):
        """
        Store values which is calculated and raw ones.
        Returns:
        """
        pass

    def get_input_stream_numpy(self):
        """
        Default samplerate and farame_width of input device are written here.
        Returns:
            sd.InputStream: Instance of the audio input stream classes.
        """
        return sd.InputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_numpy,
            blocksize=self.FRAME_LENGTH
        )

    def get_input_stream_raw(self):
        return sd.RawInputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_raw,
            blocksize=self.FRAME_LENGTH
        )

    def save_region(self):
        """
        When exiting, save the voiced audio regions, which is concatenated.
        Returns:
        """
        if Profile.is_writable:
            self.audio_manipulator.save_wav_auditok(audio_region=self.region_concat)
