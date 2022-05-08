class InputDeviceNotFoundException(Exception):
    def __init__(self, message):
        super(InputDeviceNotFoundException, self).__init__(message)


class NoInputDeviceException(Exception):
    def __init__(self, message):
        super(NoInputDeviceException, self).__init__(message)


class InvalidInputDeviceChannelsException(Exception):
    def __init__(self, message):
        super(InvalidInputDeviceChannelsException, self).__init__(message)


class DefaultInputDeviceException(Exception):
    def __init__(self, message):
        super(DefaultInputDeviceException, self).__init__(message)


class IncorrectTypeException(Exception):
    def __init__(self, message):
        super(IncorrectTypeException, self).__init__(message)


class ZeroMQNotInitialized(Exception):
    def __init__(self, message):
        super(ZeroMQNotInitialized, self).__init__(message)


class GotNanException(Exception):
    def __init__(self, message):
        super(GotNanException, self).__init__(message)
