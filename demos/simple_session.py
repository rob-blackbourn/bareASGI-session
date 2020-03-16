"""A simple example"""

import asyncio
from datetime import datetime
import socket
from typing import List

from bareasgi import Application, text_writer, bytes_writer
from baretypes import Scope, Info, RouteMatches, Content, HttpResponse, Header
from hypercorn.asyncio import serve
from hypercorn.config import Config

from bareasgi_session import (
    add_session_middleware,
    SESSION_COOKIE_KEY,
    MemorySessionStorage,
    SessionCookieFactory
)


async def index_handler(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """Redirect to the session handler"""
    return 303, [(b'location', b'/session')]


async def session_handler(
        _scope: Scope,
        info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    session = info[SESSION_COOKIE_KEY]
    now = session.get('now')
    message = f'The time was {now}' if now else 'First time'
    session['now'] = datetime.now()
    headers: List[Header] = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(message)).encode('ascii'))
    ]
    return 200, headers, text_writer(message)


app = Application()

fqdn = socket.getfqdn()
host, _sep, domain_name = fqdn.partition(',')
add_session_middleware(
    app,
    MemorySessionStorage(),
    SessionCookieFactory(domain=(domain_name or host).encode())
)
app.http_router.add({'GET'}, '/', index_handler)
app.http_router.add({'GET'}, '/session', session_handler)

config = Config()
config.bind = [f"{fqdn}:9009"]
asyncio.run(serve(app, config))
