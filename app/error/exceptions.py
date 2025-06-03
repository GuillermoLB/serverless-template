from .codes import Errors, Warnings


class BaseAppException(Exception):
    """Base exception for our application"""
    def __init__(self, error: Errors | Warnings, code: int = 500):
        self.error = error
        self.code = code

    def __str__(self):
        return self.error


class ResourceNotFoundException(BaseAppException):
    """Raised when a requested resource is not found"""
    def __init__(self, error: str):
        super().__init__(error, code=404)
class ValidationException(BaseAppException):
    """Raised when input validation fails"""
    def __init__(self, error: str, code: int = 400):
        super().__init__(error, code=code)

class UnauthorizedException(BaseAppException):
    """Raised when user is not authorized"""
    def __init__(self, error: str):
        super().__init__(error, code=401)
