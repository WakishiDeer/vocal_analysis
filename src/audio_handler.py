import queue

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import sounddevice as sd
from logger import Logger


class AudioHandler:
    """
    This class contains realtime audio controller such as matplotlib.
    Args:
        self._audio_stream (object): The instance of audio stream from AudioStream Class,
        which will be used to plot or calculate streaming data.
    """

    def __init__(self, audio_stream):
        self._audio_stream = audio_stream
        # plot setting
        self.window = 2000.0
        self.interval = 30.0
        self.samplerate = sd.default.samplerate
        self.channels = [1]  # input channels to plot
        self.lines = None
        self.plot_data = None

        # Logger.setting
        self.logger = Logger(name=__name__)

    @property
    def audio_stream(self):
        return self._audio_stream

    def update_plot(self, frame):
        """
        This is called for each plot update.
        Args:
            frame:
        Returns:
        """
        while True:
            try:
                data = self.audio_stream.buffer.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            self.plot_data = np.roll(self.plot_data, -shift, axis=0)
            self.plot_data[-shift:, :] = data
        for column, line in enumerate(self.lines):
            line.set_ydata(self.plot_data[:, column])
        return self.lines

    def start_input(self, is_buffer=False):
        """
        This method just input and does not plot anything.
        Returns:
        """
        if is_buffer:
            self.audio_stream.stream = self.audio_stream.get_input_stream_raw()
            self.logger.logger.info("Streaming with buffer mode.")
        else:
            self.audio_stream.stream = self.audio_stream.get_input_stream_numpy()
            self.logger.logger.info("Streaming with numpy mode.")
        # start streaming
        with self.audio_stream.stream:
            self.logger.logger.info("Steaming...")
            self.logger.logger.info("Starting voice activity detection.")
            input("If you want to exit, please put any.")  # wait for keyboard
            import time
            time.sleep(100)

    def start_plot_amplitude(self):
        # plot setting
        length = int(self.window * self.samplerate / (1000 * self.audio_stream.DOWN_SAMPLE))
        self.plot_data = np.zeros((length, len(self.channels)))
        fig, ax = plt.subplots()
        self.lines = ax.plot(self.plot_data)
        if len(self.channels) > 1:
            ax.legend(['channel {}'.format(c) for c in self.channels],
                      loc='lower left', ncol=len(self.channels))
        ax.axis((0, len(self.plot_data), -1, 1))
        ax.set_yticks([0])
        ax.yaxis.grid(True)
        ax.tick_params(bottom='off', top='off', labelbottom='off',
                       right='off', left='off', labelleft='off')
        fig.tight_layout(pad=0)

        # stream setting
        self.audio_stream.stream = self.audio_stream.get_input_stream_numpy()
        ani = FuncAnimation(fig, self.update_plot, interval=self.interval, blit=True)
        with self.audio_stream.stream:
            plt.show()

    def start_plot_f0(self):
        """
        Todo: Implement
        Returns:
        """
        pass
