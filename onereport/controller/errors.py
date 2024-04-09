from typing import Any, Tuple
from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException
from onereport.exceptions import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    MethodNotAllowedError,
    NotFoundError,
    InternalServerError,
)


errors = Blueprint("errors", __name__)


@errors.app_errorhandler(400)
def bad_request_handler(error: HTTPException | Any) -> Tuple[str, int]:
    return (
        render_template("errors/error.html", error=BadRequestError("bad request")),
        400,
    )


@errors.app_errorhandler(401)
def unauthorized_handler(error: HTTPException | Any) -> Tuple[str, int]:
    return (
        render_template("errors/error.html", error=UnauthorizedError("unauthorized")),
        401,
    )


@errors.app_errorhandler(403)
def forbidded_handler(error: HTTPException | Any) -> Tuple[str, int]:
    return render_template("errors/error.html", error=ForbiddenError("forbidden")), 403


@errors.app_errorhandler(404)
def not_found_handler(error: HTTPException | Any) -> Tuple[str, int]:
    return render_template("errors/error.html", error=NotFoundError("not found")), 404


@errors.app_errorhandler(405)
def method_not_allowed_handler(error: HTTPException | Any) -> Tuple[str, int]:
    return (
        render_template(
            "errors/error.html", error=MethodNotAllowedError("method not allowed")
        ),
        405,
    )


@errors.app_errorhandler(500)
def internal_server_error(error: HTTPException | Any) -> Tuple[str, int]:
    return (
        render_template(
            "errors/error.html", error=InternalServerError("internal server error")
        ),
        500,
    )
