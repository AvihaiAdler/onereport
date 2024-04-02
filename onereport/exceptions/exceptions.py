from typing import Self


class BaseError(Exception):
    def __init__(self: Self, code: int, msg: str, /) -> None:
        self.code = code
        self.msg = msg

    def __repr__(self: Self) -> str:
        return f"CustomException({self.code} {self.msg})"

    def __str__(self: Self) -> str:
        return self.msg


class BadRequestError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(400, msg)

    def __repr__(self: Self) -> str:
        return f"BadRequest({self.code} {self.msg})"


class UnauthorizedError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(401, msg)

    def __repr__(self: Self) -> str:
        return f"Unauthorized({self.code} {self.msg})"


class ForbiddenError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(401, msg)

    def __repr__(self: Self) -> str:
        return f"Forbidden({self.code} {self.msg})"


class NotFoundError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(404, msg)

    def __repr__(self: Self) -> str:
        return f"NotFound({self.code} {self.msg})"


class InternalServerError(BaseError):
    def __init__(self: Self, msg: str, /) -> None:
        super().__init__(500, msg)

    def __repr__(self: Self) -> str:
        return f"InternalError({self.code} {self.msg})"
