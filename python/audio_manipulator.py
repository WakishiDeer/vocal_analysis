import numpy as np
import pyworld as pw
import auditok
import shennong
from shennong.processor.mfcc import MfccProcessor
from shennong.postprocessor.cmvn import CmvnPostProcessor
from shennong.postprocessor.vad import VadPostProcessor

import re

from util.profile import Profile
from util.logger import Logger
from util.exception import *
from util import sd


class AudioManipulator:
    """
    This class calc audio_util features and initialize related devices.
    Device information and parameter to calc audio_util are written here.
    """

    def __init__(self):
        self.logger = Logger(name=__name__)

        # for audio_util device setting
        self.pattern = re.compile("\\S+")
        self.INPUT_SAMPLE_RATE = None

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
        # set reduced sample rate or default one
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
            self.logger.logger.exception("On device selecting, it seems there is no available audio_util device.")
            import sys
            sys.exit(1)  # exit as failure

        except InputDeviceNotFoundException:
            self.logger.logger.exception("On device selecting, {} does not matched.".format(device_candidate))

    def vad_generator(self, audio_data: np.ndarray, min_dur_sec: float = 0.2, max_dur_sec: float = 5,
                      max_silence_sec: float = 0.5, energy_threshold: float = 50):
        """
        Vad based on energy.
        Args:
            energy_threshold:
            max_dur_sec:
            min_dur_sec:
            max_silence_sec:
            audio_data:
        Returns:
            res (auditok.core.AudioRegion): split audio signals (= region) for each duration.
        Notes:
            This VAD is based on `auditok` library, whose detection method calculates audio_util energy.
            To avoid wrong detection, please run this method in silent place.
        Todo:
            Conduct an experiment to find what values of args are good for my research.
        """
        audio_region = auditok.AudioRegion(data=audio_data.tobytes(), sampling_rate=16000, sample_width=2, channels=1)
        # res = audio_region.split(
        res = auditok.split(
            input=audio_region,
            min_dur=min_dur_sec,
            max_dur=max_dur_sec,
            max_silence=max_silence_sec,
            energy_threshold=energy_threshold
        )
        return res

    def voice_activity_detection(self, audio_data: np.ndarray = None):
        """
        Do VAD with `shennong`, library for voice feature extraction.
        Notes:
            To default, the length of `audio_data` should be xx msec.
        Args:
            audio_buf:
            audio_data (np.ndarray): the target audio_util data.
        Returns:
        """
        # calc mfcc
        mfcc = self.calc_mfcc(audio_data=audio_data)
        # calc cmvn
        normalized_mfcc = self.calc_cmvn(mfcc=mfcc)
        processor = VadPostProcessor(energy_mean_scale=0.5, energy_threshold=2.0)
        vad = processor.process(features=normalized_mfcc)
        nframes = normalized_mfcc.shape[0]
        nvoiced = sum(vad.data[vad.data == 1])
        self.logger.logger.info('{} voiced frames out of {}'.format(nvoiced, nframes))

    def calc_energy(self, voiced_audio_data: np.ndarray = None, sample_width: int = 0):
        """
        Calc energy of each region using `auditok.signal.compute_average_channel`
        Args:
            sample_width:
            voiced_audio_data (auditok.core.AudioRegion): The region to calculate energy.
        Returns:
            res (auditok.core.AudioRegion): calcurated audio signals (= region) for each duration.
        """
        res = auditok.signal.calculate_energy_single_channel(data=voiced_audio_data.tobytes(),
                                                             sample_width=sample_width)
        # print(res)
        return res

    def calc_mfcc(self, audio_data: bytes = None, window_type: str = "hanning"):
        """
        Calc mfcc, audio_util feature, and return it.
        Notes:
            For `audio_data`, whose range of value should be from -1 to 1 if dtype of np.ndarray is np.float32
            or np.float64.
            For more detail, please refer to https://docs.cognitive-ml.fr/shennong/python/audio.html
        Args:
            audio_data (np.ndarray): the target audio_util data, whose length is usually `25 * n`msec.
            window_type: which window you want to use {"hamming", "hanning", "povey", "rectangular", "blackman"}
        Returns:
            res (shennong.features.Features): calculated MFCC data.
        """
        processor = MfccProcessor(sample_rate=self.INPUT_SAMPLE_RATE, frame_length=0.025)
        processor.window_type = window_type
        processor.low_freq = 20
        processor.high_freq = 7800
        audio = shennong.Audio(data=audio_data, sample_rate=self.INPUT_SAMPLE_RATE)
        res = processor.process(signal=audio)  # calc mfcc
        return res

    def calc_cmvn(self, mfcc: shennong.features.Features = None):
        """
        Calc CMVN, Cepstral Mean Variance Normalization, which makes MFCC zero mean and unit variance.
        Args:
            mfcc (shennong.features.Features): calculated MFCC
        Returns:
            res (shennong.features.Features): calculated CMVN
        """
        processor = CmvnPostProcessor(dim=mfcc.ndims)
        processor.accumulate(mfcc)
        res = processor.process(mfcc)
        return res

    def calc_normalization(self, audio_data: np.ndarray):
        """
        Normalization for audio_util array.
        Notes:
            DO NOT use with streaming data, because range is calculated for each block of audio_util.
        Returns:
            res (np.ndarray): Normalized data from -1 to 1
        """
        data_min = audio_data.min(keepdims=True)
        data_max = audio_data.max(keepdims=True)
        res = ((audio_data - data_min) / (data_max - data_min) - 0.5) * 2
        return res

    def calc_f0(self, data: np.ndarray):
        """
        This method calculates f0 from numpy array of audio_util.
        """
        data = data.astype(np.float)
        data = np.squeeze(data)
        _f0, t = pw.dio(data, sd.default.samplerate)
        self._f0 = pw.stonemask(data, _f0, t, sd.default.samplerate)
        print(self.f0)

    def save_wav_auditok(self, audio_region: auditok.AudioRegion, file_name: str = None):
        # if file name is empty, set time format
        if not file_name:
            import datetime
            file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        audio_region.save(file_name)
