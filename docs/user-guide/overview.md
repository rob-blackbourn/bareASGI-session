# Overview

When a client (e.g. a browser tab) makes HTTP requests to a server, the server
does not know if the requests came from the same client. This makes it difficult
to maintain state information (e.g. the users identity).

A solution which is transparent to the client involves the server sending a
cookie to the client. Once the cookie is sent the client will automatically add
the cookie to any subsequent request it makes to the server (assuming cookies
are enabled). By checking the cookie the server can know which client has sent
the request.
