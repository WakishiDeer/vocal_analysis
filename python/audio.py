from typing import Dict, Any
import numpy as np


class Audio:
    """
    Store audio features, which will be sent
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
        self._total_voiced_time_ms: float = 0.0
        self.current_audio_data = None
        self._f0 = None
        self._average_rms: np.float64 = np.float64()
        self._average_rms_db: np.float64 = np.float64()
        self._std_rms_db: np.float64 = np.float64()  # for each region
        self._std_rms_db_total: np.float64 = np.float64()
        self._average_f0: np.float64 = np.float64()
        self._std_f0: np.float64 = np.float64()

        # dict for send
        self.message_data: Dict[str, float] = {
            "t": .0,
            "total_voiced_time_ms": self._total_voiced_time_ms,
            "average_rms": self._average_rms,
            "average_rms_db": self._average_rms_db,
            "std_rms_db": self._std_rms_db,
            "std_rms_db_total": self._std_rms_db_total,
            "average_f0": self._average_f0,
            "std_f0": self._std_f0,
        }

    @property
    def audio_data(self):
        return self._audio_data

    @property
    def total_voiced_time_ms(self):
        return self._total_voiced_time_ms

    @property
    def f0(self):
        return self._f0

    @property
    def average_rms(self):
        return self._average_rms

    @property
    def average_rms_db(self):
        return self._average_rms_db

    @property
    def std_rms_db(self):
        return self._std_rms_db

    @property
    def std_rms_db_total(self):
        return self._std_rms_db_total

    @property
    def average_f0(self):
        return self._average_f0

    @property
    def std_f0(self):
        return self._std_f0

    @audio_data.setter
    def audio_data(self, data):
        self._audio_data = data

    @total_voiced_time_ms.setter
    def total_voiced_time_ms(self, data):
        # set data into message simultaneously
        self.message_data["total_voiced_time_ms"] = data
        self._total_voiced_time_ms = data

    @f0.setter
    def f0(self, data):
        self._f0 = data

    @average_rms.setter
    def average_rms(self, data):
        # set data into message simultaneously
        self.message_data["average_rms"] = data
        self._average_rms = data

    @average_rms_db.setter
    def average_rms_db(self, data):
        # set data into message simultaneously
        self.message_data["average_rms_db"] = data
        self._average_rms_db = data

    @std_rms_db.setter
    def std_rms_db(self, data):
        # set data into message simultaneously
        self.message_data["std_rms_db"] = data
        self._std_rms_db = data

    @std_rms_db_total.setter
    def std_rms_db_total(self, data):
        # set data into message simultaneously
        self.message_data["std_rms_db_total"] = data
        self._std_rms_db_total = data

    @average_f0.setter
    def average_f0(self, data):
        # set data into message simultaneously
        self.message_data["average_f0"] = data
        self._average_f0 = data

    @std_f0.setter
    def std_f0(self, data):
        # set data into message simultaneously
        self.message_data["std_f0"] = data
        self._std_f0 = data
