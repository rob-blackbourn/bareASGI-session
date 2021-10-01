"""Session"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union
from uuid import uuid4 as uuid

from bareasgi import HttpRequest, HttpResponse, HttpRequestCallback
from bareutils.cookies import decode_set_cookie, encode_set_cookie
from bareutils import header

from .storage import SessionStorage


class SessionMiddleware:
    """Session middleware"""

    def __init__(
            self,
            context_key: str,
            storage: SessionStorage,
            cookie_name: bytes,
            expires: Optional[datetime],
            max_age: Optional[Union[int, timedelta]],
            path: Optional[bytes],
            domain: Optional[bytes],
            secure: bool,
            http_only: bool,
            same_site: Optional[bytes]
    ) -> None:
        self.context_key = context_key
        self.storage = storage
        self.cookie_name = cookie_name
        self.expires = expires
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    async def __call__(
            self,
            request: HttpRequest,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        """Call the session middleware.

        Sessions are maintained with cookies. The session gets set up by
        sending a set-cookie header in the response, with a cookie containing a
        unique key. The browser keeps this cookie and sends it on all subsequent
        requests, so the set-cookie header need only be sent once per session.

        The key is used to load session data from a store which is then added to
        the request before the handler is called. Any changes to the session
        data are saved after the handler returns and before the response is sent.

        Args:
            request (HttpRequest): The request.
            handler (HttpRequestCallback): The request handler.

        Returns:
            HttpResponse: The response.
        """

        cookie_session_key = self._get_session_key_from_cookie(request)
        if cookie_session_key is not None:
            session_key = cookie_session_key
        else:
            session_key = self._make_new_session_key()

        await self._load_session_from_store(request, session_key)

        response = await handler(request)

        await self._save_session_to_store(request, session_key)

        if cookie_session_key is None:
            response = self._add_session_key_cookie_to_response(
                session_key,
                request,
                response
            )

        return response

    def _get_session_key_from_cookie(self, request: HttpRequest) -> Optional[str]:
        cookies = header.cookie(request.scope['headers'])
        cookie = cookies.get(self.cookie_name)
        if not cookie:
            return None

        return cookie[0].decode('ascii')

    def _make_new_session_key(self) -> str:
        return str(uuid())

    async def _load_session_from_store(self, request: HttpRequest, session_key: str) -> None:
        request.context[self.context_key] = await self.storage.load(session_key)

    async def _save_session_to_store(self, request: HttpRequest, session_key: str) -> None:
        await self.storage.save(session_key, request.context[self.context_key])

    def _add_session_key_cookie_to_response(
            self,
            session_key: str,
            request: HttpRequest,
            response: HttpResponse
    ) -> HttpResponse:
        set_cookie_header = self._make_set_cookie_header(request, session_key)

        headers = self._add_set_cookie_header(
            response.headers or [],
            set_cookie_header
        )

        return HttpResponse(
            response.status,
            headers,
            response.body,
            response.pushes
        )

    def _make_set_cookie_header(
            self,
            request: HttpRequest,
            session_key: str
    ) -> Tuple[bytes, bytes]:
        if self.domain:
            domain: Optional[bytes] = self.domain
        else:
            domain = self._get_domain(request)

        set_cookie = encode_set_cookie(
            self.cookie_name,
            session_key.encode('ascii'),
            expires=self.expires,
            max_age=self.max_age,
            path=self.path,
            domain=domain,
            secure=self.secure,
            http_only=self.http_only,
            same_site=self.same_site
        )
        return (b'set-cookie', set_cookie)

    def _get_domain(self, request: HttpRequest) -> Optional[bytes]:
        domain = header.find(b'host', request.scope['headers'])
        assert domain, 'missing host header'
        if domain == b'localhost' or domain.startswith(b'localhost:'):
            # For localhost the domain must be omitted.
            domain = None

        return domain

    def _add_set_cookie_header(
            self,
            headers: List[Tuple[bytes, bytes]],
            set_cookie_header: Tuple[bytes, bytes]
    ) -> List[Tuple[bytes, bytes]]:
        for index, (key, value) in enumerate(headers):
            if key == b'set-cookie':
                candidate = decode_set_cookie(value)
                if candidate['name'] == self.cookie_name:
                    headers[index] = set_cookie_header
                    break
        else:
            headers.append(set_cookie_header)

        return headers
