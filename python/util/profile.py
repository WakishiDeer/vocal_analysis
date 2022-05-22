from typing import List


class Profile:
    """
    Store values.
    """
    args = None
    is_input_device_set = False
    is_init = True  # this is for `self.region_concat` to initialize
    is_writable = False  # for saving streaming audio
    f0_estimation_methods: str = "Harvest"  # the way to estimate f0

    @classmethod
    def set_args(cls, args):
        Profile.args = args
