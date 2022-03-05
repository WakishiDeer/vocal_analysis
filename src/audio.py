import numpy as np
from scipy.io import wavfile
import sounddevice as sd
from profile import Profile
from logger import Logger


class Audio:
    """
    This is super class of any audio subclass. It contains audio data, sample rate, and more.
    Attributes:

    Todo:
        Consider using MATLAB audio library, because there is little python library
        to handle realtime audio processing.
    """

    def __init__(self):
        self._audio_data = None
        self._time = None
        self._fft_data = None
        self._freq_list = None

        # for audio device setting
        import re
        self.pattern = re.compile("\\S+")

        # Logger setting
        self.logger = Logger(name=__name__)

    @property
    def audio_data(self):
        return self._audio_data

    @property
    def time(self):
        return self._time

    @property
    def fft_data(self):
        return self._fft_data

    @property
    def freq_list(self):
        return self._freq_list

    @audio_data.setter
    def data(self, data):
        self._audio_data = data

    @time.setter
    def time(self, time):
        self._time = time

    @fft_data.setter
    def fft_data(self, fft_data):
        self._fft_data = fft_data

    @freq_list.setter
    def freq_list(self, freq_list):
        self._freq_list = freq_list

    def get_devices(self):
        # session for listing audio device
        devices = sd.query_devices()
        input_device = sd.query_devices(kind="input")  # returns available dict of input device
        return devices, input_device

    def is_device_exist(self, devices):
        is_exist = False
        if len(devices) > 0:
            is_exist = True
        return is_exist

    def input_device_interactively(self):
        # session for interactive input
        while True:
            # wait for user input
            device_candidate = input("Enter the device name or index you want to use: ")
            if self.pattern.match(device_candidate) is None:
                # if not found, repeat input
                self.logger.logger.info("On device selecting, {} is invalid name or index.".format(device_candidate))
                continue
            else:
                break  # found successfully
        return device_candidate

    def is_device_matched(self, device_candidate, devices):
        is_found = False
        if device_candidate.isdecimal():  # when index
            if len(devices) > int(device_candidate):
                is_found = True
            return is_found
        else:  # when string
            for device in devices:
                if device["name"] == device_candidate:
                    is_found = True
                    break
            return is_found

    def set_input_device(self):
        """
        Select input device interactively.
        Returns:
        """
        # display devices on terminal
        devices, input_device = self.get_devices()
        import pprint
        pprint.pprint(devices)  # show all devices (includes both input and output ones)
        pprint.pprint(input_device)  # show only selected input device

        try:
            # exit if not input device exist, otherwise proceed
            is_exist = self.is_device_exist(devices=devices)
            if not is_exist:  # raise error when there is no available device
                from exception import NoInputDeviceException
                raise NoInputDeviceException("Error for input device.")

            # user will input `input device`
            device_candidate = self.input_device_interactively()
            # check if input name or index is matched or not
            is_matched = self.is_device_matched(device_candidate=device_candidate, devices=devices)
            if not is_matched:
                from exception import InputDeviceNotFoundException

        except NoInputDeviceException:
            self.logger.logger.exception("On device selecting, it seems there is no available audio device.")
            import sys
            sys.exit(1)  # exit as failure

        except InputDeviceNotFoundException:
            self.logger.logger.exception("On device selecting, {} does not matched.".format(device_candidate))

        # set default input device (output one won't be changed)
        if is_matched:
            if device_candidate.isdecimal():  # when numerical value
                sd.default.device = (int(device_candidate), sd.default.device[1])  # found device successfully
            elif device_candidate.isdecimal():  # when string
                # todo implement
                pass
            self.logger.logger.info("Successfully set default device.")
        else:
            self.logger.logger.warning("On device selecting, {} does not matched.".format(device_candidate))

    def read_audio(self, wav_file_name):
        """
        Reads the WAV file as numpy_array and other features.
        Args:
            wav_file_name (string): The name of wave file.
        Returns:
            data (numpy_array): The array of audio data whose type is 1-D or 2-D one, depending on audio channel.
            time (float): The time was based on `rate`.
            rate (int): Sample rate of WAV file.
        """
        # read audio file
        rate, data = wavfile.read(wav_file_name)
        self.sample_rate = rate
        # vertically normalize amplitude from -1 to 1
        self.audio_data = data / 2 ** (16 - 1)
        # horizontal setting
        self.time = np.arange(0, data.shape[0] / rate, 1 / rate)

    def calc_fft(self):
        # vertical axis
        self.fft_data = np.abs(np.fft.fft(self.audio_data))
        # horizontal axis
        self.freq_list = np.fft.fftfreq(self.audio_data.shape[0], d=1.0 / self.rate)
