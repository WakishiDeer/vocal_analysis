import sys
from audio_stream import AudioStream
from audio_controller import AudioController


class Main:
    """
    This is main class for controlling audio input, calc, plot, and others.
    Attributes:
    """

    def __init__(self):
        self._audio_stream = AudioStream()
        self._audio_controller = AudioController(self._audio_stream)
        # initialization for help of commandline arguments
        self._args = self._argparse_init()

    def _argparse_init(self):
        import argparse
        # general description
        parser = argparse.ArgumentParser(
            description="The program for audio analysis, which includes file based and audio stream (realtime) one.")
        # description for each argument
        # following `-f` and `-s` arguments should be mutually exclusive (i.e., xor)
        xor_group = parser.add_mutually_exclusive_group(reqired=True)
        xor_group.add_argument("-f", "--filename", help="whether using wave file or not", action="store_true", default=False)
        parser.add_argument("filename_string", help="the name of wave file")
        xor_group.add_argument("-s", "--stream", help="whether using audio device as input source or not",
                               action="store_true")
        # parsing
        return parser.parse_args()

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
    main.audio_stream.read_audio(wav_file_name=main.args.filename_string)
