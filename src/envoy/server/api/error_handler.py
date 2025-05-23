import logging
from http import HTTPStatus
from typing import Optional, Union

from envoy_schema.server.schema.sep2.error import ErrorResponse
from envoy_schema.server.schema.sep2.types import ReasonCodeType
from fastapi import HTTPException, Request, Response
from lxml.etree import XMLSyntaxError  # type: ignore # nosec: This will need to be addressed with pydantic-xml
from pydantic_core import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from envoy.server.api.response import XmlResponse

logger = logging.getLogger(__name__)


def http_status_code_to_reason_code(status_code: Union[HTTPStatus, int]) -> ReasonCodeType:
    if status_code == HTTPStatus.TOO_MANY_REQUESTS:
        return ReasonCodeType.resource_limit_reached
    elif status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return ReasonCodeType.internal_error
    else:
        return ReasonCodeType.invalid_request_format


def generate_error_response(
    status_code: Union[HTTPStatus, int], message: Optional[str] = None, max_retry_duration: Optional[int] = None
) -> Response:
    """Generates an XML response loaded with a sep2 Error object"""
    reason_code = http_status_code_to_reason_code(status_code)

    return XmlResponse(
        status_code=status_code,
        content=ErrorResponse(reasonCode=reason_code, message=message, maxRetryDuration=max_retry_duration),
    )


def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException, Exception]) -> Response:
    """Handles specific HTTP exceptions"""
    if isinstance(exc, HTTPException) or isinstance(exc, StarletteHTTPException):
        status_code = exc.status_code
        detail = exc.detail
    else:
        status_code = 0
        detail = "Unknown"

    logger.exception(f"{request.path_params} generated status code {status_code} and exception {exc}")

    return generate_error_response(status_code, message=detail)


def validation_exception_handler(request: Request, exc: Union[ValidationError, Exception]) -> Response:
    """Handles fastapi validation exceptions that haven't been handled. These usually occur during
    parsing of an incoming model to a Pydantic model and almost always indicate a bad request by the user.

    It can technically arise if we stuff up the creation of a response model but test coverage should be catching
    those cases so I think it's an acceptable 'risk' to just return the validation errors."""

    if not hasattr(exc, "json"):
        return general_exception_handler(request, exc)

    logger.exception(f"{request.path_params} generated validation exception {exc}")
    return generate_error_response(HTTPStatus.BAD_REQUEST, message=exc.json())


def xml_exception_handler(request: Request, exc: Union[XMLSyntaxError, Exception]) -> Response:
    """Handles fastapi XML validation exceptions that haven't been handled. These usually occur during
    parsing of an incoming model to a Pydantic XML model and almost always indicate a bad request by the user.

    It can technically arise if we stuff up the creation of a response model but test coverage should be catching
    those cases so I think it's an acceptable 'risk' to just return the validation errors."""

    if not hasattr(exc, "msg"):
        return general_exception_handler(request, exc)

    logger.exception(f"{request.path_params} generated validation exception {exc}")
    return generate_error_response(HTTPStatus.BAD_REQUEST, message=exc.msg)


def general_exception_handler(request: Request, exc: Exception) -> Response:
    """Handles general purpose exceptions that haven't been handled
    through another means"""

    logger.exception(f"{request.path_params} generated exception {exc}")

    # don't leak any internal information about a 500
    return generate_error_response(HTTPStatus.INTERNAL_SERVER_ERROR, message=None)


class LoggedHttpException(HTTPException):
    """This is for all intents and purposes a HTTPException - it will just also utilise the specified
    logger to log the exception too.

    It's a simple way of making the various HTTP Exception handlers more consistent with their logging practices"""

    def __init__(
        self, logger_instance: logging.Logger, exc: Optional[Exception], status_code: HTTPStatus, detail: str
    ) -> None:
        super().__init__(status_code, detail)

        log_message = f"LoggedHttpException ({int(status_code)}) {status_code}: {detail}"
        if exc is None:
            logger_instance.info(log_message)
        else:
            logger_instance.error(log_message, exc_info=exc)
