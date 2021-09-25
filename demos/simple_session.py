"""A simple example"""

import asyncio
from datetime import datetime
import socket
from typing import List, Tuple

from bareasgi import Application, text_writer, HttpRequest, HttpResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config

from bareasgi_session import (
    add_session_middleware,
    session_data,
    MemorySessionStorage
)


async def index_handler(_request: HttpRequest) -> HttpResponse:
    """Redirect to the session handler"""
    return HttpResponse(303, [(b'location', b'/session')])


async def session_handler(request: HttpRequest) -> HttpResponse:
    session = session_data(request)
    now = session.get('now')
    message = f'The time was {now}' if now else 'First time'
    session['now'] = datetime.now()
    headers: List[Tuple[bytes, bytes]] = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(message)).encode('ascii'))
    ]
    return HttpResponse(200, headers, text_writer(message))


app = Application()

fqdn = socket.getfqdn()
host, _sep, domain_name = fqdn.partition(',')
add_session_middleware(
    app,
    MemorySessionStorage(),
    domain=(domain_name or host).encode()
)
app.http_router.add({'GET'}, '/', index_handler)
app.http_router.add({'GET'}, '/session', session_handler)

config = Config()
config.bind = [f"0.0.0.0:9009"]
asyncio.run(serve(app, config))  # type: ignore
