import re
import pprint
from typing import Union
import numpy as np
import auditok

from util.profile import Profile
from util.logger import Logger
from util.exception import *
from util import sd


class AudioManipulator:
    """
    This class has manipulation for audio input/output and audio conversion.
    Device information is written here.
    """

    def __init__(self):
        self.logger = Logger(name=__name__)

        # for audio_util device setting
        import re
        self.pattern = re.compile("\\S+")
        self.INPUT_SAMPLE_RATE: int = 16000  # input samplerate of the device (can be down sampled)

    def get_devices(self):
        # session for listing audio_util device
        devices = sd.query_devices()
        input_device = sd.query_devices(kind="input")  # returns available dict of input device
        return devices, input_device

    def is_device_exist(self, devices):
        is_exist = False
        if len(devices) > 0:
            is_exist = True
        return is_exist

    def find_device_index(self, device_candidate: str = "", devices: sd.DeviceList = None) -> int:
        """
        Find and return device index from device name.
        """
        for index, device in enumerate(devices):
            # matched or not
            if device['name'] == device_candidate:
                return index

    def input_device_interactively(self):
        # session for interactive input
        while True:
            # wait for user input
            device_candidate = input("Enter the device name or index you want to use: \n")
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

    def set_default(self, use_default: bool = False, device_index: int = 0,
                    devices: sd.DeviceList = None):
        """
        Set default of sound device.
        Notes:
            Output parameters won't be changed in this method.
        Args:
            use_default:
            device_index:
            devices:
        Returns:
        """
        # default setting for sounddevice
        sd.default.device = (device_index, sd.default.device[1])

        # set reduced sample rate or default one
        if Profile.args.down_input_sample_rate:
            sd.default.samplerate = 16000
        else:
            sd.default.samplerate = devices[device_index]['default_samplerate']

        # set input channel: (input_channels, output_channels)
        sd.default.channels = (1, devices[device_index]['max_output_channels'])
        # default setting for fields
        self.INPUT_SAMPLE_RATE = sd.default.samplerate

    def set_input_device(self, use_default: bool = False) -> bool:
        """
        Select input device interactively.
        Args:
            use_default (bool): To use default input device without selecting.
        Returns:
            success (bool): Successfully set device or not
        """
        device_candidate: str = "0"
        device_index: int = 0
        is_success: bool
        devices, input_device = self.get_devices()

        # manually set
        try:
            # exit if not input device exist, otherwise proceed
            is_exist = self.is_device_exist(devices=devices)
            if not is_exist:  # raise error when there is no available device
                raise NoInputDeviceException("Error on selecting device.")

            # use default mode or not
            if use_default:
                pprint.pprint(input_device)  # show only selected input device
                device_index = self.find_device_index(device_candidate=input_device["name"], devices=devices)
                self.set_default(use_default=True, device_index=device_index, devices=devices)
                # successfully set
                Profile.is_input_device_set = True
                is_success = True
                return is_success

            pprint.pprint(devices)  # show all devices (includes both input and output ones)
            # user will input `input device`
            device_candidate = self.input_device_interactively()
            # check if input name or index is matched or not
            is_matched = self.is_device_matched(device_candidate=device_candidate, devices=devices)
            if not is_matched:  # set default input device (output one won't be changed)
                raise InputDeviceNotFoundException("Error on selecting device.")
            if device_candidate.isdecimal():  # when numerical value
                self.set_default(use_default=False, device_index=int(device_candidate), devices=devices)
            else:  # when string
                device_index = self.find_device_index(device_candidate=device_candidate, devices=devices)
                self.set_default(use_default=False, device_index=device_index, devices=devices)

        except NoInputDeviceException:
            self.logger.logger.exception("On device selecting, it seems there is no available audio_util device.")
            import sys
            sys.exit(1)  # exit as failure

        except InputDeviceNotFoundException:
            self.logger.logger.exception("On device selecting, {} does not matched.".format(device_candidate))
            is_success = False
            return is_success

        else:  # success
            Profile.is_input_device_set = True
            self.logger.logger.info("Successfully set default device.")
            is_success = True
            return is_success

    def int_to_float64(self, audio_data: np.ndarray = None):
        pattern = r"(float)\d{2,3}"
        res: Union[re.Match, None] = re.match(pattern, str(audio_data.dtype))
        try:
            if res is not None:  # when float type is found
                raise IncorrectTypeException("Error when converting into float")
        except IncorrectTypeException:
            self.logger.logger.exception("{} can't accept float.".format(__name__))
            import sys
            sys.exit(1)  # exit as failure
        res = (audio_data / 2 ** 15).astype(np.float64)
        return res

    def float_to_int16(self, audio_data: np.ndarray = None):
        try:
            if audio_data.dtype == "int16":
                raise IncorrectTypeException("Error when converting into int16")
        except IncorrectTypeException:
            self.logger.logger.exception("{} can't accept int16.".format(__name__))
            import sys
            sys.exit(1)  # exit as failure
        res = (audio_data * 2 ** 15).astype(np.int16)
        return res

    def save_wav_auditok(self, audio_region: auditok.AudioRegion, file_name: str = None):
        # if file name is empty, set time format
        if not file_name:
            import datetime
            file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        import os
        # get current executing path
        absolute_path = os.path.abspath("..")
        destination_path = os.path.join(absolute_path, "etc")
        file_path = os.path.join(destination_path, file_name + ".wav")
        # if there is no path, make directories
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        audio_region.save(file_path)
