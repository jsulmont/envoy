import logging
from http import HTTPStatus

from fastapi import APIRouter, Response
from fastapi_async_sqlalchemy import db

from envoy.server.manager.health import HealthManager

logger = logging.getLogger(__name__)


router = APIRouter()

HEALTH_URI = "/status/health"

HEALTH_DOE_URI = "/status/doe"
HEALTH_DYNAMIC_PRICE_URI = "/status/dynamicprices"


@router.head(HEALTH_URI)
@router.get(HEALTH_URI, status_code=HTTPStatus.OK)
async def get_health() -> Response:
    """Responds with a HTTP 200 if the server diagnostics report everything is OK. HTTP 500 otherwise.

    Response will be a plaintext encoding of the passing/failing health checks

    Returns:
        fastapi.Response object.
    """

    check = await HealthManager.run_health_check(db.session)
    headers = {"Content-Type": "text/plain"}
    content = str(check)

    if not check.database_connectivity:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    elif not check.database_has_data:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        status_code = HTTPStatus.OK

    return Response(content=content, status_code=status_code, headers=headers)


@router.head(HEALTH_DOE_URI)
@router.get(HEALTH_DOE_URI, status_code=HTTPStatus.OK)
async def get_doe_health() -> Response:
    """Responds with a HTTP 200 if the server dynamic operating envelope diagnostics report everything is OK.
    HTTP 500 otherwise.

    Response will be a plaintext encoding of the passing/failing health checks

    Returns:
        fastapi.Response object.
    """

    check = await HealthManager.run_dynamic_operating_envelope_check(db.session)
    headers = {"Content-Type": "text/plain"}
    content = str(check)

    if not check.has_does:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    elif not check.has_future_does:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        status_code = HTTPStatus.OK

    return Response(content=content, status_code=status_code, headers=headers)


@router.head(HEALTH_DYNAMIC_PRICE_URI)
@router.get(HEALTH_DYNAMIC_PRICE_URI, status_code=HTTPStatus.OK)
async def get_dynamic_price_health() -> Response:
    """Responds with a HTTP 200 if the server dynamic prices diagnostics report everything is OK. HTTP 500 otherwise.

    Response will be a plaintext encoding of the passing/failing health checks

    Returns:
        fastapi.Response object.
    """

    check = await HealthManager.run_dynamic_price_check(db.session)
    headers = {"Content-Type": "text/plain"}
    content = str(check)

    if not check.has_dynamic_prices:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    elif not check.has_future_prices:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        status_code = HTTPStatus.OK

    return Response(content=content, status_code=status_code, headers=headers)
