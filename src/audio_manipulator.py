import numpy as np
import sounddevice as sd
import pyworld as pw
import re

from profile import Profile
from logger import Logger


class AudioManipulator:
    """
    This class calc audio features and initialize related devices.
    Device information and parameter to calc audio are written here.
    """

    def __init__(self):
        self.logger = Logger(name=__name__)

        # for audio device setting
        self.pattern = re.compile("\\S+")
        self.INPUT_SAMPLE_RATE = None
        self.VAD_DURATION = 10  # ms

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

    def set_default(self, device_index: int, devices: sd.DeviceList):
        """
        Set default of sound device.
        Notes:
            Output parameters won't be changed in this method.
        Args:
            device_index:
            devices:
        Returns:
        """
        # default setting for sounddevice
        sd.default.device = (device_index, sd.default.device[1])
        # set reduced sample rate or default
        if Profile.args.down_input_sample_rate:
            sd.default.samplerate = 16000
        else:
            sd.default.samplerate = devices[device_index]['default_samplerate']
        # set input channel
        sd.default.channels = (1, devices[device_index]['max_output_channels'])
        # default setting for fields
        self.INPUT_SAMPLE_RATE = sd.default.samplerate

    def set_input_device(self):
        """
        Select input device interactively.
        Returns:
        """
        # display devices on terminal
        global device_candidate
        devices, input_device = self.get_devices()
        import pprint
        pprint.pprint(devices)  # show all devices (includes both input and output ones)
        pprint.pprint(input_device)  # show only selected input device

        from exception import NoInputDeviceException
        from exception import InputDeviceNotFoundException
        try:
            # exit if not input device exist, otherwise proceed
            is_exist = self.is_device_exist(devices=devices)
            if not is_exist:  # raise error when there is no available device
                raise NoInputDeviceException("Error on selecting device.")

            # user will input `input device`
            device_candidate = self.input_device_interactively()
            # check if input name or index is matched or not
            is_matched = self.is_device_matched(device_candidate=device_candidate, devices=devices)
            if is_matched:  # set default input device (output one won't be changed)
                device_index = 0
                if device_candidate.isdecimal():  # when numerical value
                    device_index = int(device_candidate)
                    self.set_default(device_index=device_index, devices=devices)
                else:  # when string
                    # todo implement
                    pass
                Profile.is_input_device_set = True
                self.logger.logger.info("Successfully set default device.")
            else:
                raise InputDeviceNotFoundException("Error on selecting device.")

        except NoInputDeviceException:
            self.logger.logger.exception("On device selecting, it seems there is no available audio device.")
            import sys
            sys.exit(1)  # exit as failure

        except InputDeviceNotFoundException:
            self.logger.logger.exception("On device selecting, {} does not matched.".format(device_candidate))

    def voice_activity_detection(self, audio_data: np.ndarray = None, audio_buf=None):
        """
        Do VAD with `shennong`, library for voice feature extraction.
        Notes:
            To default, the length of `audio_data` should be xx msec.
        Args:
            audio_data (np.ndarray): the target audio data, which length is usually
        Returns:
        """
        pass

    def calc_normalization(self, audio_data: np.ndarray):
        """
        Normalization for audio array.
        Returns:
            res (np.ndarray): Normalized data from -1 to 1
        """
        data_min = audio_data.min(keepdims=True)
        data_max = audio_data.max(keepdims=True)
        res = ((audio_data - data_min) / (data_max - data_min) - 0.5) * 2
        return res

    def calc_fft(self):
        # vertical axis
        self.fft_data = np.abs(np.fft.fft(self.audio_data))
        # horizontal axis
        self.freq_list = np.fft.fftfreq(self.audio_data.shape[0], d=1.0 / self.rate)

    def calc_f0(self, data: np.ndarray):
        """
        This method calculates f0 from numpy array of audio.
        """
        data = data.astype(np.float)
        data = np.squeeze(data)
        _f0, t = pw.dio(data, sd.default.samplerate)
        self._f0 = pw.stonemask(data, _f0, t, sd.default.samplerate)
        print(self.f0)
