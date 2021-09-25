"""Session"""

from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import uuid4 as uuid

from bareasgi import HttpRequest, HttpResponse, HttpRequestCallback
from bareutils.cookies import decode_set_cookie, encode_set_cookie
from bareutils import header

from .storage import SessionStorage


class SessionMiddleware:
    """Session middleware"""

    def __init__(
            self,
            info_key: str,
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
        self.info_key = info_key
        self.storage = storage
        self.cookie_name = cookie_name
        self.expires = expires
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    async def _hydrate_session(self, request: HttpRequest) -> str:
        cookies = header.cookie(request.scope['headers'])
        cookie = cookies.get(self.cookie_name)
        session_key: str = cookie[0].decode('ascii') if cookie else str(uuid())
        request.info[self.info_key] = await self.storage.load(session_key)
        return session_key

    async def _dehydrate_session(
            self,
            session_key: str,
            request: HttpRequest,
            response: HttpResponse
    ) -> HttpResponse:
        # Save the cookie data
        await self.storage.save(session_key, request.info[self.info_key])

        # Put the set-cookie in the headers
        headers = response.headers or []
        host = header.find(b'host', request.scope['headers'])
        assert host, 'missing host header'
        set_cookie = encode_set_cookie(
            self.cookie_name,
            session_key.encode('ascii'),
            expires=self.expires,
            max_age=self.max_age,
            path=self.path,
            domain=self.domain or host,
            secure=self.secure,
            http_only=self.http_only,
            same_site=self.same_site
        )
        set_cookie_header = (b'set-cookie', set_cookie)
        for index, (key, value) in enumerate(headers):
            if key == b'set-cookie':
                candidate = decode_set_cookie(value)
                if candidate['name'] == self.cookie_name:
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
