class Timeout(Exception):
    """
    Raised when the expected response was not received
    within the expected time.
    """
    pass

class ReadRequestNotAcknowledged(Exception):
    """
    Raised when the read request was not acknowledged.
    """
    pass

class WriteRequestNotAcknowledged(Exception):
    """
    Raised when the write request was not acknowledged.
    """
    pass

class ErrorPacket(Exception):
    """
    Raised when an error packet is received.
    """
    pass

