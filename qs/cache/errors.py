class CacheError(Exception):
    """
    Some unexpected behavior that can occur with cache
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
