# bareASGI-session

Session support for bareASGI (read the [docs](https://rob-blackbourn.github.io/bareASGI-session/)).

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
