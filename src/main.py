import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt


def main():
    data, time, rate = read_audio()
    fft_data, freq_list = calc_fft(data, rate)
    # plt.plot(time, data)
    plt.plot(freq_list, fft_data)
    # plt.xlim(0, 1000/rate)
    plt.xlim(0, 8000)  # range is from 0Hz to 8000Hz
    plt.show()


def read_audio():
    """
    Returns:
        data (numpy_array): The array of audio data whose type is 1-D or 2-D one, depending on audio channel.
        time (float): The time was based on `rate`.
        rate (int): Sample rate of WAV file.
    """
    # read audio file
    args = sys.argv
    wav_file_name = args[1]
    rate, data = scipy.io.wavfile.read(wav_file_name)
    # vertically normalize amplitude from -1 to 1
    data = data / 2 ** (16 - 1)
    # horizontal setting
    time = np.arange(0, data.shape[0] / rate, 1 / rate)
    return data, time, rate


def calc_fft(data, rate):
    # vertical axis
    fft_data = np.abs(np.fft.fft(data))
    # horizontal axis
    freq_list = np.fft.fftfreq(data.shape[0], d=1.0 / rate)
    return fft_data, freq_list


if __name__ == '__main__':
    main()
