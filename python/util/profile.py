class Profile:
    """
    Store values.
    """
    args = None
    is_input_device_set = False

    @classmethod
    def set_args(cls, args):
        Profile.args = args
