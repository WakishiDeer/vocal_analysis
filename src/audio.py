import numpy as np
import scipy.io.wavfile


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
        self._sample_rate = None
        self._fft_data = None
        self._freq_list = None

    @property
    def audio_data(self):
        return self._audio_data

    @property
    def time(self):
        return self._time

    @property
    def sample_rate(self):
        return self._sample_rate

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

    @sample_rate.setter
    def rate(self, rate):
        self._sample_rate = rate

    @fft_data.setter
    def fft_data(self, fft_data):
        self._fft_data = fft_data

    @freq_list.setter
    def freq_list(self, freq_list):
        self._freq_list = freq_list

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
        rate, data = scipy.io.wavfile.read(wav_file_name)
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
