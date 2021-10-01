"""Session"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from bareasgi import Application, HttpRequest

from .middleware import SessionMiddleware
from .storage import SessionStorage, MemorySessionStorage

SESSION_CONTEXT_KEY = '__bareasgi_session__'


def add_session_middleware(
        app: Application,
        storage: Optional[SessionStorage] = None,
        *,
        context_key: str = SESSION_CONTEXT_KEY,
        cookie_name: bytes = b'bareASGI-session',
        expires: Optional[datetime] = None,
        max_age: Optional[Union[int, timedelta]] = None,
        path: Optional[bytes] = None,
        domain: Optional[bytes] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[bytes] = None
) -> Application:
    """Add session storage middleware.

    If no storage provider is supplied the default is to store the sessions in
    memory.

    The default settings are **not secure**. In production the following settings
    are recommended.

    Setting `http_only=True` forbids JavaScript from accessing the cookie in
    the browser. With `same_site="Strict"` or `same_site="Lax"`, the browser
    prevents the cookie being sent on cross-site requests. If the server is
    delivering over https, setting `secure=True` will prevent the cookie from
    being sent from non-https requests.

    Args:
        app (Application): The ASGI application.
        storage (Optional[SessionStorage], optional): The storage provider.
            Defaults to None.
        context_key (str, optional): The key in the applications context where session
            data can be found. Defaults to SESSION_CONTEXT_KEY.
        cookie_name (bytes, optional): The cookie name. Defaults to b'bareASGI-session'.
        expires (Optional[datetime], optional): The cookie expiry time. Defaults
            to None.
        max_age (Optional[Union[int, timedelta]], optional): The maximum age of
            the cookie. Defaults to None.
        path (Optional[bytes], optional): The cookie path. Defaults to None.
        domain (Optional[bytes], optional): The cookie domain. If unspecified
            the host header of the request will be used. Defaults to None.
        secure (bool, optional): The cookie is only sent if the request is
            using https Defaults to False.
        http_only (bool, optional): If true the cookie is not available with
            javascript in the client. Defaults to False.
        same_site (Optional[bytes], optional): Controls whether the cookie is
            sent cross origin. Defaults to None.

    Returns:
        Application: The ASGI application.
    """

    session_middleware = SessionMiddleware(
        context_key,
        storage or MemorySessionStorage(),
        cookie_name,
        expires,
        max_age,
        path,
        domain,
        secure,
        http_only,
        same_site
    )

    app.middlewares.append(session_middleware)

    return app


def session_data(
        request: HttpRequest,
        *,
        context_key: str = SESSION_CONTEXT_KEY
) -> Any:
    return request.context[context_key]
