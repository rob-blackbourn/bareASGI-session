# bareASGI-session

Session support for bareASGI (read the [docs](https://rob-blackbourn.github.io/bareASGI-session/)).

## Overview

When a client (e.g. a browser tab) makes HTTP requests to a server, the server
does not know if the requests came from the same client. This makes it difficult
to maintain state information (e.g. the users identity).

A solution which is transparent to the client involves the server sending a
cookie to the client. Once the cookie is sent the client will automatically add
the cookie to any subsequent request it makes to the server (assuming cookies
are enabled). By checking the cookie the server can know which client has sent
the request.

## Usage

You can add session middleware with the `add_session_middleware` helper function.

```python
from bareasgi import Application
from bareasgi_session import (
  add_session_middleware,
  MemorySessionStorage
)

app = Application()

add_session_middleware(app, MemorySessionStorage())
```

The session can be retrieved with the `session_data` helper function. This returns
an (initially empty) dictionary.

```python
from datetime import datetime
from bareutils import text_writer
from bareasgi_session import session_data

async def session_handler(request: HttpRequest) -> HttpResponse:
    session = session_data(request)
    now = session.get('now')
    message = f'The time was {now}' if now else 'First time'
    session['now'] = datetime.now()
    headers: List[Header] = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(message)).encode('ascii'))
    ]
    return HttpResponse(200, headers, text_writer(message))
```
