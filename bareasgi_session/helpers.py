"""Session"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from bareasgi import Application, HttpRequest

from .middleware import SessionMiddleware
from .storage import SessionStorage

SESSION_INFO_KEY = '__bareasgi_session__'


def add_session_middleware(
        app: Application,
        storage: SessionStorage,
        *,
        info_key: str = SESSION_INFO_KEY,
        cookie_name: bytes = b'bareASGI-session',
        expires: Optional[datetime] = None,
        max_age: Optional[Union[int, timedelta]] = None,
        path: Optional[bytes] = None,
        domain: Optional[bytes] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[bytes] = None
) -> Application:

    session_middleware = SessionMiddleware(
        info_key,
        storage,
        cookie_name,
        expires,
        max_age,
        path,
        domain,
        secure,
        http_only,
        same_site
    )

    app.info[info_key] = None

    app.middlewares.append(session_middleware)

    return app


def session_data(
        request: HttpRequest,
        *,
        info_key: str = SESSION_INFO_KEY
) -> Any:
    return request.info[info_key]
