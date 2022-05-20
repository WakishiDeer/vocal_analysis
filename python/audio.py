import numpy as np


class Audio:
    """
    Attributes:
        self.audio_manipulator: Instance of AudioManipulator which includes methods to control audio devices and audio.
        self.audio_calculator: Instance of AudioCalculator which includes methods for calculation such as rms energy.
    """

    def __init__(self, audio_manipulator, audio_calculator):
        # instance for audio_util calc and manipulate
        self.audio_manipulator = audio_manipulator
        self.audio_calculator = audio_calculator

        # fields
        self._audio_data: np.ndarray = np.array([])  # overall audio data
        self.current_audio_data = None
        self._f0 = None
        self._average_energy_rms: np.float64 = np.float64()
        self._average_f0: np.float64 = np.float64()
        self._average_spl_db: np.float64 = np.float64()
        self._std_spl_db: np.float64 = np.float64()

    @property
    def audio_data(self):
        return self._audio_data

    @property
    def f0(self):
        return self._f0

    @property
    def average_energy_rms(self):
        return self._average_energy_rms

    @property
    def average_f0(self):
        return self._average_f0

    @audio_data.setter
    def audio_data(self, data):
        self._audio_data = data

    @f0.setter
    def f0(self, data):
        self._f0 = data

    @average_energy_rms.setter
    def average_energy_rms(self, data):
        self._average_energy_rms = data

    @average_f0.setter
    def average_f0(self, data):
        self._average_f0 = data
