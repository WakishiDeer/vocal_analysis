class InputDeviceNotFoundException(Exception):
    def __init__(self, message):
        super(InputDeviceNotFoundException, self).__init__(message)


class NoInputDeviceException(Exception):
    def __init__(self, message):
        super(NoInputDeviceException, self).__init__(message)


class InvalidInputDeviceChannelsException(Exception):
    def __init__(self, message):
        super(InvalidInputDeviceChannelsException, self).__init__(message)