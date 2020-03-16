# bareASGI-session

Session support for bareASGI (read the [docs](https://rob-blackbourn.github.io/bareASGI-session/)).

## Usage

You can add seesion middleware with the `add_session_middleware` helper function.

```python
import socket

from bareasgi import Application
from bareasgi_session import (
  add_session_middleware,
  MemorySessionStorage,
  SessionCookieFactory
)

app = Application()

fqdn = socket.getfqdn()
host, _sep, domain_name = fqdn.partition(',')
add_session_middleware(
    app,
    MemorySessionStorage(),
    SessionCookieFactory(domain=(domain_name or host).encode())
)
```

The session gets stored in the `info` parameter in the request handler through the `SESSION_COOKIE_KEY`:

```python
from datetime import datetime
from bareutils import text_writer
from bareasgi_session import SESSION_COOKIE_KEY

async def session_handler(scope, info, matches, content):
    session = info[SESSION_COOKIE_KEY]
    now = session.get('now')
    message = f'The time was {now}' if now else 'First time'
    session['now'] = datetime.now()
    headers: List[Header] = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(message)).encode('ascii'))
    ]
    return 200, headers, text_writer(message)
```
