from audio_stream import AudioStream
from audio_plotter import AudioPlotter
from profile import Profile
from logger import Logger


class Main:
    """
    This is main class for controlling commandline arguments, audio input, calc, plot, and others.
    Attributes:
    """

    def __init__(self):
        # initialization for help of commandline arguments
        _args = self._argparse_init()
        import pprint
        pprint.pprint(_args)
        self.profile = Profile.set_args(args=_args)  # you can access args via `self.profile`)
        # instances for each audio class
        self._audio_stream = AudioStream()
        self._audio_plotter = AudioPlotter(self._audio_stream)

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
        # parsing
        return parser.parse_args()

    def start_mode(self):
        if Profile.args.available_device:
            pass
        elif Profile.args.filename is not None:
            pass
        elif Profile.args.stream:
            self.logger.logger.info("Start streaming and plotting.")
            self.audio_plotter.start_plot()
        else:
            self.logger.logger.error("Invalid mode.")

    @property
    def audio_stream(self):
        return self._audio_stream

    @property
    def audio_plotter(self):
        return self._audio_plotter


if __name__ == '__main__':
    main = Main()
    main.start_mode()
