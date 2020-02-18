import uvicorn
from bareasgi import Application, bytes_writer

app = Application()


@app.on_http_request({'GET'}, '/')
async def http_request_handler(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], bytes_writer(b'Hello, World!')

uvicorn.run(app, port=9009)
