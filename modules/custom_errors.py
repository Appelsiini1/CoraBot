class RandomOrgAPIError(Exception):
    """Exception raised for errors given by the Random.org API.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class RequestLimitReached(Exception):
    """Random.org API request limit reached for the day.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)