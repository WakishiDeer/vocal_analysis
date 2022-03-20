from audio_stream import AudioStream
from audio_handler import AudioHandler
from audio_manipulator import AudioManipulator
from profile import Profile
from logger import Logger
import pyannote.features.shennong

class Main:
    """
    This is main class for controlling commandline arguments, audio input, calc, plot, and others.
    Attributes:
    """

    def __init__(self):
        # pprint.pprint(results_list)
        # initialization for help of commandline arguments
        _args = self._argparse_init()
        import pprint
        pprint.pprint(_args)
        self.profile = Profile.set_args(args=_args)  # you can access args via `self.profile`)
        # instances for each audio class
        self._audio_stream = None
        self._audio_handler = None
        self.audio_manipulator = AudioManipulator()

        # Logger setting
        self.logger = Logger(name=__name__)

    def _argparse_init(self):
        import argparse
        # general description
        parser = argparse.ArgumentParser(
            description="The program for audio analysis, which includes file based and audio stream (realtime) one.")
        # description to display available audio input
        parser.add_argument("-a", "--available_device", help="display all of available audio device with index",
                            action="store_true", default=False)
        # description for each argument
        # following `-f` and `-s` arguments should be mutually exclusive (i.e., xor)
        xor_group = parser.add_mutually_exclusive_group(required=True)
        xor_group.add_argument("-f", "--filename", help="whether using wave file or not")
        xor_group.add_argument("-s", "--stream", help="whether using audio device as input source or not",
                               action="store_true", default=False)
        xor_group.add_argument("-i", "--input", help="start as input mode. it won't be plotted.", action="store_true",
                               default=False)
        parser.add_argument("-d", "--down_input_sample_rate", help="set input sample rate as 16000",
                            action="store_true", default=False)
        # parsing
        return parser.parse_args()

    def start_mode(self):
        # firstly, set input device
        self.audio_manipulator.set_input_device()
        # execute according process
        if Profile.args.available_device:
            pass
        elif Profile.args.filename is not None:
            # todo implement
            pass
        elif Profile.args.stream:
            self.logger.logger.info("Start streaming and plotting.")
            self.audio_handler.start_plot_amplitude()
        elif Profile.args.input:
            self.logger.logger.info("Start streaming input (without plotting).")
            self.audio_stream = AudioStream(audio_manipulator=self.audio_manipulator)
            self.audio_handler = AudioHandler(audio_stream=self.audio_stream)
            self.audio_handler.start_input()
        else:
            self.logger.logger.error("Invalid mode selection.")

    @property
    def audio_manipulator(self):
        return self._audio_manipulator

    @property
    def audio_stream(self):
        return self._audio_stream

    @property
    def audio_handler(self):
        return self._audio_handler

    @audio_manipulator.setter
    def audio_manipulator(self, data):
        self._audio_manipulator = data

    @audio_stream.setter
    def audio_stream(self, data):
        self._audio_stream = data

    @audio_handler.setter
    def audio_handler(self, data):
        self._audio_handler = data


if __name__ == '__main__':
    main = Main()
    main.start_mode()
