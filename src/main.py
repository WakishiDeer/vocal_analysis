import sys
from audio_stream import AudioStream
from audio_controller import AudioController


class Main:
    """
    This is main class for controlling audio input, calc, plot, and others.
    Attributes:
    """
    def __init__(self):
        self._args = sys.argv
        self._audio_stream = AudioStream()
        self._audio_controller = AudioController(self._audio_stream)

    @property
    def args(self):
        return self._args

    @property
    def audio_stream(self):
        return self._audio_stream

    @property
    def audio_controller(self):
        return self._audio_controller


if __name__ == '__main__':
    main = Main()
    main.audio_stream.read_audio(wav_file_name=main.args[1])
