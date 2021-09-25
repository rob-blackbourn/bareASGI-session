"""Session"""

from uuid import uuid4 as uuid

from bareasgi import Application, HttpRequest, HttpResponse, HttpRequestCallback
from bareutils.cookies import decode_set_cookie
from bareutils import header

from .factory import SessionCookieFactory
from .storage import SessionStorage

SESSION_COOKIE_NAME = b'bareASGI-session'
SESSION_COOKIE_KEY = '__bareasgi_session__'


class SessionMiddleware:
    """Session middleware"""

    def __init__(
            self,
            storage: SessionStorage,
            cookie_factory: SessionCookieFactory
    ) -> None:
        self.storage = storage
        self.cookie_factory = cookie_factory

    async def _hydrate_session(self, request: HttpRequest) -> str:
        cookies = header.cookie(request.scope['headers'])
        cookie = cookies.get(self.cookie_factory.name)
        session_key: str = cookie[0].decode('ascii') if cookie else str(uuid())
        request.info[SESSION_COOKIE_KEY] = await self.storage.load(session_key)
        return session_key

    async def _dehydrate_session(
            self,
            session_key: str,
            request: HttpRequest,
            response: HttpResponse
    ) -> HttpResponse:
        # Save the cookie data
        await self.storage.save(session_key, request.info[SESSION_COOKIE_KEY])

        # Put the set-cookie in the headers
        headers = response.headers or []
        host = header.find(b'host', request.scope['headers'])
        assert host, 'missing host header'
        set_cookie = self.cookie_factory.create_cookie(session_key, host)
        set_cookie_header = (b'set-cookie', set_cookie)
        for index, (key, value) in enumerate(headers):
            if key == b'set-cookie':
                candidate = decode_set_cookie(value)
                if candidate['name'] == self.cookie_factory.name:
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

    async def __call__(
            self,
            request: HttpRequest,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        session_key = await self._hydrate_session(request)
        response = await handler(request)
        return await self._dehydrate_session(session_key, request, response)


def add_session_middleware(
        app: Application,
        storage: SessionStorage,
        cookie_factory: SessionCookieFactory
) -> Application:
    """Add the session middleware

    Args:
        app (Application): The ASGI application
        storage (SessionStorage): The session storage engine
        cookie_factory (SessionCookieFactory): The session cookie factory

    Returns:
        Application: The application.
    """

    session_middleware = SessionMiddleware(storage, cookie_factory)

    app.middlewares.append(session_middleware)

    return app
