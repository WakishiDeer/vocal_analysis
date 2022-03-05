import queue

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class AudioPlotter:
    """
    This class contains realtime audio controller such as matplotlib.
    Args:
        self._audio_stream (object): The instance of audio stream from AudioStream Class,
        which will be used to plot or calculate streaming data.
    """

    def __init__(self, audio_stream):
        self._audio_stream = audio_stream
        self.lines = None
        self.plot_data = None

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

    def start_plot(self):
        length = int(self.audio_stream.window * self.audio_stream.samplerate / (1000 * self.audio_stream.down_sample))
        self.plot_data = np.zeros((length, len(self.audio_stream.channels)))
        fig, ax = plt.subplots()
        self.lines = ax.plot(self.plot_data)
        if len(self.audio_stream.channels) > 1:
            ax.legend(['channel {}'.format(c) for c in self.audio_stream.channels],
                      loc='lower left', ncol=len(self.audio_stream.channels))
        ax.axis((0, len(self.plot_data), -1, 1))
        ax.set_yticks([0])
        ax.yaxis.grid(True)
        ax.tick_params(bottom='off', top='off', labelbottom='off',
                       right='off', left='off', labelleft='off')
        fig.tight_layout(pad=0)

        self.audio_stream.stream = self.audio_stream.get_input_stream()
        ani = FuncAnimation(fig, self.update_plot, interval=self.audio_stream.interval, blit=True)
        with self.audio_stream.stream:
            plt.show()
