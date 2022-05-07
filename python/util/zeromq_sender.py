import json
from typing import Any
from typing import Dict

import zmq
from zmq.asyncio import Context
from tornado.ioloop import IOLoop

from .logger import Logger


class ZeroMQSender:
    """
    This class defines the way to response data to C# Program running on Unity.
    In short, this class works as sever.
    Todo: implement message process with AsyncIO
    Note:
        ref: https://github.com/zeromq/pyzmq/blob/main/examples/asyncio/coroutines.py
    """

    def __init__(self) -> None:
        self.logger = Logger(name=__name__)

        self.context = None
        self.socket = None
        self.loop = None
        self.message_dict: Dict[str, Any] = {}
        self.is_initialized = False
        self.is_sendable = False

    def initialize_connection(self, port_number: str = "5555") -> None:
        """
        Initialize connection.
        Notes:
            Separate with initialization due to avoiding bugs.
        """
        # for zeromq
        self.context = Context.instance()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:" + port_number)
        # for tornado setting
        self.loop = IOLoop.current()
        self.is_initialized = True

    async def send_message(self) -> None:
        """
        Process on sending message.
        """
        self.logger.logger.info("Try to Send...")
        while True:
            if self.is_sendable:
                # `self.message_dict` will be updated
                await self.socket.send_multipart([json.dumps(self.message_dict).encode("ascii")])
                self.is_sendable = False

    def snake_to_camel(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reformat string variable name according to the custom of the connection
        Examples:
            input: {"abc": foo, "a_bc": bar}
            output: {"Abc": foo, "aBc": bar}
        """
        import re
        # convert all keyword of the dictionary
        for snake_key in data_dict:
            # temporary store the value
            value = data_dict[snake_key]
            # remove snake_key and its value
            del data_dict[snake_key]
            camel_key = re.sub("_(.)", lambda msg: msg.group(1).upper(), snake_key)
            # re-store the data
            data_dict[camel_key] = value
        return data_dict

    def set_message(self, **kwargs: Dict[str, Any]):
        """
        Sets format of sending message.
        Format should follow the one of OpenFace.
        For instance, in the OpenFace, the raw string data is like:
        `{"t":136.710, "d":[-42.7,24.9,484.1,-0.080,-0.207,0.047,0.272,-0.029,0.0,0.272,-0.029,0.0,0.84,0.56,1.48,0.34,
        -0.11,0.22,0.37,-1.49,-0.24,-1.16,-0.17,0.72,0.30,0.65,1.15,1.16,-0.11]}`
        So, `audio_data_dict` should be like: Dict[str, Any]
        """
        # annotation for dictionary
        audio_data_dict: Dict[str, Any] = kwargs
        self.message_dict = {}
        for key in audio_data_dict:
            # add every keyword and value
            self.message_dict[key] = audio_data_dict[key]
        # ready to send message
        self.is_sendable = True

    def handle_message(self) -> None:
        """
        Handle loop of sending and receiving message.
        """
        self.loop.spawn_callback(self.send_message)
        self.loop.start()
