from Token import Token

class RuntimeErrorException(RuntimeError):
    """RuntimeError is raised when an error occurs during runtime."""
    token: Token
    message: str

    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message
