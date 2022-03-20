from logger import Logger
from audio_manipulator import AudioManipulator
import sounddevice as sd

class Audio:
    """
    This is super class of any audio subclass. It contains audio data, sample rate, and more.
    Attributes:
        self.sample_rate (int): default sample rate which will be defined during audio input selection
        self.vad_frame (int): the duration of each vad processing frame (milli sec.)
    Todo:
        Consider using MATLAB audio library which is callable from Python,
        because there is little python library to handle realtime audio processing.
    """

    def __init__(self, audio_manipulator):
        # instance for audio calc and manipulate
        self.audio_manipulator = audio_manipulator

        # fields
        self._audio_data = None
        self.current_audio_data = None
        self._time = None
        self._fft_data = None
        self._freq_list = None
        self._f0 = None

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

    @property
    def f0(self):
        return self._f0

    @audio_data.setter
    def audio_data(self, data):
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
