import re
import queue
from typing import Dict, Any, Union

import numpy as np
import auditok

from audio import Audio
from util import sd
from util.exception import *
from util.profile import Profile
from util.logger import Logger


class AudioStream(Audio):
    """
    This class controls audio_util coming from audio_util device (microphone), using `Python-sounddevice.`
    Note that your available audio_util device could be list by just write `$ python -m sounddevice`
    And an instance of this class will be used in `AudioController` class in `audio_handler.py`
    """

    def __init__(self, audio_manipulator=None, audio_calculator=None, zeromq_sender=None) -> None:
        """
        Initialize sound device to decide which one to select for audio_util stream.
        """
        # Logger setting
        self.logger = Logger(name=__name__)
        super().__init__(audio_manipulator=audio_manipulator, audio_calculator=audio_calculator)
        self.zeromq_sender = zeromq_sender
        # initialize connection with Unity
        self.zeromq_sender.initialize_connection()

        try:
            if not Profile.is_input_device_set:
                raise DefaultInputDeviceException
        except DefaultInputDeviceException:
            self.logger.exception("Setting for input device hasn't done yet.")
        else:
            # setting for input device
            self.DOWN_SAMPLE: int = 20
            self.CHUNK_DURATION_MS: int = 25 * 40 * 5
            self.FRAME_LENGTH: int = int(  # number of overall frames per callback
                self.audio_manipulator.INPUT_SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
            self.WINDOW_LENGTH: int = 512  # length for each sliding process
            self.HOP_LENGTH: int = self.WINDOW_LENGTH // 4  # usually, one-fourth of WINDOW_LENGTH
            self.SAMPLE_WIDTH = 2
            self.buffer: queue.Queue = queue.Queue()  # this is for plot

            # audio data
            self.region_concat: auditok.AudioRegion = auditok.AudioRegion(
                data=np.array([]).tobytes(),
                sampling_rate=self.audio_manipulator.INPUT_SAMPLE_RATE,
                sample_width=self.SAMPLE_WIDTH,
                channels=1)  # `auditok.AudioRegion` can use operator `+` to concatenate
            self.region_concat_energy: np.ndarray = np.array([])
            self.region_concat_f0: np.ndarray = np.array([])
            # dictionary for sending audio features
            self.message_dict: Dict[str, Any] = {}
            self.stream = None

            # when exiting, save the voiced region for sample
            import atexit
            atexit.register(self.save_region)

    def audio_callback_numpy(self, indata: np.ndarray, frames: int, time, status) -> None:
        """
        This callback will be called from each audio_util block.
        After calculation, the dict of values will send to Unity Process.
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
        # store dict for message
        self.store_message_values(average_energy_rms=self.average_energy_rms, average_f0=self.average_f0)

        try:
            # send message after checking initialization
            if self.zeromq_sender.is_initialized:
                message = self.zeromq_sender.snake_to_camel(data_dict=self.message_dict)
                self.zeromq_sender.set_message(
                    data_dict=message)  # we need it because sending method is async one
                # get ready and send simultaneously due to async one
                self.zeromq_sender.is_sendable = True
            else:
                raise ZeroMQNotInitialized("Error before sending message")
        except ZeroMQNotInitialized:
            self.logger.logger.warn("ZeroMQ is not initialized, so message won't be sent.")

    def audio_callback_raw(self, indata, frames: int, time, status):
        pass

    def handle_calculation(self, indata: np.ndarray = None):
        """
        This class specifies calculation for each callback (i.e., for each block)
        Args:
            indata (np.ndarray): This is audio_util data whose shape will be (`self.block_size`, `sd.default.channels[0]`).
        Returns:
        """
        # extracts voiced region
        vad_generator = self.audio_calculator.vad_generator(audio_data=indata,
                                                            max_dur_sec=self.CHUNK_DURATION_MS / 1000)

        root_energy: np.ndarray = np.array([])
        f0 = np.array([])
        region_info: str = str()

        # calculation for each voiced region
        for i, region in enumerate(vad_generator):
            # to save the region
            if Profile.is_init:
                Profile.is_writable = True
                Profile.is_init = False

            # get values represented as np.ndarray
            voiced_audio_data: np.ndarray = self.audio_manipulator.int_to_float64(
                audio_data=region.samples.astype("int16"))
            # calc stft
            is_freq, voiced_audio_data_freq = self.audio_calculator.calc_short_time_fourier_transform(
                voiced_audio_data=voiced_audio_data,
                n_fft=self.WINDOW_LENGTH)
            # separate complex-valued data into magnitude and phase
            magnitude, _ = self.audio_calculator.calc_magphase(voiced_audio_data_freq=voiced_audio_data_freq)
            # calculate energy
            root_energy = self.audio_calculator.calc_energy_rms(magnitude=magnitude,
                                                                frame_length=512,
                                                                is_freq=is_freq)
            # calculate f0
            for f0_method in Profile.f0_estimation_methods:
                if f0_method == "pYIN":
                    f0, voiced_flag, _, times = self.audio_calculator.calc_f0_pyin(voiced_audio_data=voiced_audio_data)
                elif f0_method == "DIO":
                    pass
                elif f0_method == "Harvest":
                    f0 = self.audio_calculator.calc_f0_harvest(voiced_audio_data=voiced_audio_data,
                                                               sample_rate=self.audio_manipulator.INPUT_SAMPLE_RATE)
            # store and concat values
            self.concat_values(region=region, root_energy=root_energy, f0=f0)

            # concat region info
            region_info += "\n#{} region: {}sec detected.".format(i, region.duration)

        # if the voiced region was not found
        if region_info != "":
            self.logger.logger.info(region_info)
            # calc features with overall data
            self.average_energy_rms = self.audio_calculator.calc_average_energy_rms(root_energy=root_energy)
            # when getting NaN, `np.float64(0.0)` will be returned
            f0_avg_candidate = self.audio_calculator.calc_average_f0(f0=f0)
            # check if f0 average is valid (NaN) or not
            if f0_avg_candidate != np.float64(0.0):
                self.average_f0 = f0_avg_candidate
            else:  # otherwise, retain previous value
                pass

    def concat_values(self, region, root_energy, f0):
        """
        Store values which is calculated and raw ones into fields.
        Returns:
        """
        # concat voiced regions
        self.region_concat = region + self.region_concat
        # concat energy
        self.region_concat_energy = np.append(self.region_concat_energy, root_energy)
        # concat f0
        self.region_concat_f0 = np.append(self.region_concat_f0, f0)

    def store_message_values(self, **kwargs):
        """
        Store values which is calculated and row ones into dictionary for message.
        In addition to that, the type of data will be converted into another one properly for the serialization.
        Note:
            Currently, the parameters should be stored are following:
        """
        pattern = r".*?(numpy\.float)\d{2,3}.*"
        for key in kwargs:
            # get matched data
            res: Union[re.Match, None] = re.match(pattern, str(type(kwargs[key])))
            # check if the data is valid for serialization
            if res.group(1) == "numpy.float":  # if data type is not for serialization
                # convert type for numpy into build-in one
                serializable_value = kwargs[key].item()
                # store
                self.message_dict[key] = serializable_value
            else:
                # just store each value
                self.message_dict[key] = kwargs[key]

    def get_input_stream_numpy(self) -> sd.InputStream:
        """
        Default samplerate and frame_width of input device are written here.
        Returns:
            sd.InputStream: Instance of the audio input stream classes.
        """
        return sd.InputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_numpy,
            blocksize=self.FRAME_LENGTH
        )

    def get_input_stream_raw(self) -> sd.RawInputStream:
        return sd.RawInputStream(
            dtype="int16",
            device=sd.default.device[0],
            callback=self.audio_callback_raw,
            blocksize=self.FRAME_LENGTH
        )

    def save_region(self) -> None:
        """
        When exiting, save the voiced audio regions, which is concatenated.
        Returns:
        """
        if Profile.is_writable:
            self.audio_manipulator.save_wav_auditok(audio_region=self.region_concat)
