"""Session"""

from uuid import uuid4 as uuid

from bareasgi import Application, HttpRequest, HttpResponse, HttpRequestCallback
from bareutils.cookies import decode_set_cookie
from bareutils import header

from .factory import SessionCookieFactory
from .storage import SessionStorage

SESSION_COOKIE_NAME = b'bareASGI-session'
SESSION_COOKIE_KEY = '__bareasgi_session__'


def add_session_middleware(
        app: Application,
        storage: SessionStorage,
        cookie_factory: SessionCookieFactory
) -> None:
    """Add the session middleware

    Args:
        app (Application): The ASGI application
        storage (SessionStorage): The session storage engine
        cookie_factory (SessionCookieFactory): The session cookie factory
    """

    async def _session_middleware(
            request: HttpRequest,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        # Fetch or create the session cookie and add it to info
        cookies = header.cookie(request.scope['headers'])
        cookie = cookies.get(cookie_factory.name)
        session_key: str = cookie[0].decode('ascii') if cookie else str(uuid())
        request.info[SESSION_COOKIE_KEY] = await storage.load(session_key)

        # Call the request handler.
        response = await handler(request)

        # Save the cookie data
        await storage.save(session_key, request.info[SESSION_COOKIE_KEY])

        # Put the set-cookie in the headers
        headers = response.headers or []
        set_cookie = cookie_factory.create_cookie(session_key)
        set_cookie_header = (b'set-cookie', set_cookie)
        for index, (key, value) in enumerate(headers):
            if key == b'set-cookie':
                candidate = decode_set_cookie(value)
                if candidate['name'] == cookie_factory.name:
                    headers[index] = set_cookie_header
                    break
        else:
            headers.append(set_cookie_header)

        return HttpResponse(
            response.status,
            headers,
            response.body,
            response.pushes
        )

    app.middlewares.append(_session_middleware)
