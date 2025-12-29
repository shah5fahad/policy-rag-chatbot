import re
from contextvars import ContextVar

from fastapi import Request
from jwt import decode
from loguru import logger

_current_user: ContextVar[str] = ContextVar("current_user", default="system")


_USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_]{1,64}$")


async def user_context_dependency(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = None
    if token:
        try:
            payload = decode(token, options={"verify_signature": False})
            user = (
                payload.get("email")
                or payload.get("sub")
                or payload.get("user")
                or payload.get("user_id")
                or payload.get("username")
            )
        except Exception as e:
            logger.exception(e)
    set_current_user(user)
    try:
        yield
    finally:
        _current_user.set("system")


def set_current_user(user: str | None) -> None:
    if user is None:
        value = "system"
    else:
        candidate = user.strip()
        if candidate and _USER_ID_PATTERN.fullmatch(candidate):
            value = candidate
        else:
            logger.warning(
                f"Invalid user identifier from token: '{user}'. Falling back to 'system'."
            )
            value = "system"
    _current_user.set(value)


def get_current_user() -> str:
    return _current_user.get()
