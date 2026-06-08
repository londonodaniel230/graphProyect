# Custom exception raised when input validation fails.
# Stores a list of error messages to be returned to the client.
class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__("Validation error")
        self.errors = errors
