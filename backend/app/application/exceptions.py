class ApplicationError(Exception):
    pass


class ConflictError(ApplicationError):
    pass


class NotFoundError(ApplicationError):
    pass


class UnauthorizedError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass
