from util.logger import Logger
from util.exception import GotNanException

import numpy as np
import auditok
import librosa
import pyworld as pw


class AudioCalculator:
    """
    This class calculates audio data.
    The variety of speach analysis are following:
    {pause, volume, pitch, speed}
    Todo:
        add feature -> neural model based vad with speech segmentation, splitting it into sentences and words.
        To do above, we can calculate features based on each sentence and word.
    Notes:
        This class has audio dependencies such as `auditok` and `librosa`.
    """

    def __init__(self):
        self.logger = Logger(name=__name__)

    def vad_generator(self, audio_data: np.ndarray, min_dur_sec: float = 0.2, max_dur_sec: float = 5,
                      max_silence_sec: float = 0.5, energy_threshold: float = 50.0, sample_rate=16000):
        """
        Vad based on energy.
        Args:
            sample_rate:
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
        audio_region = auditok.AudioRegion(data=audio_data.tobytes(), sampling_rate=sample_rate, sample_width=2,
                                           channels=1)
        # res = audio_region.split(
        res = auditok.split(
            input=audio_region,
            min_dur=min_dur_sec,
            max_dur=max_dur_sec,
            max_silence=max_silence_sec,
            energy_threshold=energy_threshold
        )
        return res

    def calc_short_time_fourier_transform(self, voiced_audio_data: np.ndarray = None, n_fft=512,
                                          hop_length: int = 512 // 4):
        """
        Calculate short time fourier transform from time domain `np.ndarray.`
        Args:
            hop_length:
            voiced_audio_data:
            n_fft:
        Returns:
            res (np.ndarray): Complex-valued matrix of short-term fourier transform coefficients.
        """
        res = librosa.magphase(librosa.stft(y=voiced_audio_data, n_fft=n_fft, hop_length=hop_length))[0]
        return True, res

    def calc_magphase(self, voiced_audio_data_freq: np.ndarray = None):
        """
        Separate a complex-valued spectrogram D into Magnitude (S) and phase (P).
        Args:
            voiced_audio_data_freq:
        Returns:
            magnitude (np.ndarray): note that data type is `real`
            phase (np.ndarray): note that data type is `complex`
        """
        magnitude, phase = librosa.magphase(D=voiced_audio_data_freq)
        return magnitude, phase

    def calc_energy_rms(self, magnitude: np.ndarray = None, voiced_audio_data: np.ndarray = None,
                        frame_length: int = 512,
                        hop_length: int = 512 // 4,
                        is_freq: bool = False) -> np.ndarray:
        """
        Calc root-mean-square of energy of each region.
        Args:
            voiced_audio_data: Time domain audio series.
            hop_length: Number of audio samples between adjacent STFT columns.
            is_freq (bool): If audio data is freq. domain or not.
            frame_length (int): The length to calculate.
            magnitude (np.ndarray): The region to calculate energy.
        Returns:
            res (np.ndarray): calculated audio signals (= region) for each duration.
        """
        if is_freq:
            res = librosa.feature.rms(S=magnitude, frame_length=frame_length, hop_length=hop_length)
        else:
            res = librosa.feature.rms(y=voiced_audio_data, frame_length=frame_length, hop_length=hop_length)
        return res

    def calc_average_energy_rms(self, root_energy: np.ndarray = None) -> np.float64:
        """
        Calc average for root-mean-square of energy.
        Args:
            root_energy:
        Returns:
        """
        res = np.mean(root_energy, dtype=np.float64)
        return res

    def calc_f0_pyin(self, voiced_audio_data: np.ndarray = None, sample_rate: int = 16000,
                     frame_length: int = 512,
                     hop_length: int = 512 // 4,
                     min_freq: int = librosa.note_to_hz("C2"), max_freq: int = librosa.note_to_hz("C7")) -> [np.ndarray,
                                                                                                             np.ndarray,
                                                                                                             np.ndarray,
                                                                                                             np.ndarray]:
        """
        References:
            https://librosa.org/doc/main/generated/librosa.pyin.html
            Mauch, Matthias, and Simon Dixon.
            “pYIN: A fundamental frequency estimator using probabilistic threshold distributions.”
             2014 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2014.
        Args:
            hop_length:
            frame_length:
            max_freq:
            min_freq:
            voiced_audio_data:
            sample_rate:
        Returns:
            f0: time series of fundamental frequencies in Hertz.
            voiced_flag: time series containing boolean flags indicating whether a frame is voiced or not.
            voiced_probs: time series containing the probability that a frame is voiced.
            times:
        Notes:
            `f0` contains `np.nan` if `librosa.pyin()` detects unvoiced region.
        """
        f0, voiced_flag, voiced_probs = librosa.pyin(y=voiced_audio_data, fmin=min_freq, fmax=max_freq, sr=sample_rate,
                                                     frame_length=frame_length, hop_length=hop_length)
        times = librosa.times_like(f0, hop_length=hop_length, sr=sample_rate)
        return f0, voiced_flag, voiced_probs, times

    def calc_f0_dio(self, voiced_audio_data: np.ndarray = None, sample_rate: int = 16000):
        """
        Calculate f0 contour based on DIO algorithm.
        In this algorithm, there are three steps.
        1. low-pass filtering with different cutoff freq.
        2. calculate f0 candidates with each filtered signal.
        3. select the highest reliability of that.
        References:
            https://scholar.archive.org/work/us4hwprcqbealjydiwyeakkky4/access/wayback/http://www.isca-speech.org:80/archive/Interspeech_2017/pdfs/0068.PDF
        """
        pass

    def calc_f0_harvest(self, voiced_audio_data: np.ndarray = None, sample_rate: int = 16000,
                        min_freq: int = librosa.note_to_hz("C2"), max_freq: int = librosa.note_to_hz("C7"),
                        hop_length_ms: float = 5.0):
        """
        Calculate f0 contour based on Harvest algorithm with stonemask which is f0 refinement method.
        References:
            https://web.archive.org/web/20180206035
        """
        _f0, temporal_positions = pw.harvest(x=voiced_audio_data, fs=sample_rate, f0_floor=min_freq, f0_ceil=max_freq,
                                             frame_period=hop_length_ms)
        f0 = pw.stonemask(x=voiced_audio_data, temporal_positions=temporal_positions, f0=_f0, fs=sample_rate)
        return f0

    def calc_average_f0(self, f0: np.ndarray = np.array([])) -> np.float64:
        """
        Calculate average of f0 for given array of f0 values.
        Notes:
            In this function, `np.nan` will be ignored when calculating mean.
        """
        try:
            # convert 0.0 into NaN
            f0[f0 == 0.0] = np.nan
            # avoid NaN when calculating
            f0_avg = np.nanmean(f0, dtype=np.float64)
            if np.isnan(f0_avg):
                raise GotNanException("Error when calculating average of f0")
        except GotNanException:
            self.logger.logger.warn("Got value of `nan` when calculating average of f0.")
        return f0_avg

    def calc_normalization(self, audio_data: np.ndarray) -> np.ndarray:
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
