class PyMiniPingException(Exception):
    """Base exception for pyminiping."""


class HostUnreachable(PyMiniPingException):
    """Raised when the host could not be resolved or reached."""


class RootRequired(PyMiniPingException):
    """Raised if the user does not have required root privileges."""


class PingTimeout(PyMiniPingException):
    """Raised when a ping operation times out."""


class PacketError(PyMiniPingException):
    """Raised when a received packet is malformed or unexpected."""


class DestinationUnreachable(PyMiniPingException):
    """
    Raised when an ICMP Destination Unreachable packet is received.
    """
    def __init__(self, code: int, message: str = ""):
        super().__init__(f"ICMP Destination Unreachable (code {code}): {message}")
        self.code = code
        self.message = message
