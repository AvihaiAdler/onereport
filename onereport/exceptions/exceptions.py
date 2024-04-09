from typing import Self


class BaseError(Exception):
    def __init__(self: Self, code: int, description: str, msg: str, /) -> None:
        self.code = code
        self.description = description
        self.msg = msg

    def __repr__(self: Self) -> str:
        return f"CustomException({self.code} {self.description}\n{self.msg})"

    def __str__(self: Self) -> str:
        return f"{self.code} - {self.description}\n{self.msg}"


class BadRequestError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(400, "Bad Request", msg)


class UnauthorizedError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(401, "Unauthorized", msg)


class ForbiddenError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(401, "Forbidded", msg)


class NotFoundError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(404, "Not Found", msg)


class MethodNotAllowedError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(405, "Method Not Allowed", msg)


class InternalServerError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(500, "Internal Server Error", msg)
