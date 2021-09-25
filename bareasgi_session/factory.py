"""A session cookie factory

Attributes:
    SESSION_COOKIE_NAME (bytes): 'bareASGI-session' - The session cookie name.
    SESSION_COOKIE_EXPIRES (Optional[datetime]): None - The session cookie expiry.
    SESSION_COOKIE_MAX_AGE (Optional[Union[int, timedelta]]): None - The maximum age of the session cookie.
    SESSION_COOKIE_PATH (Optional[bytes]): None - The session cookie path
    SESSION_COOKIE_DOMAIN (Optional[bytes]): None - the session cookie domain
    SESSION_COOKIE_SECURE (bool): False - Indicates whether the session cookie is available to JavaScript.
    SESSION_COOKIE_HTTP_ONLY (bool): False - Indicates whether the session cookie is available to the browser.
    SESSION_COOKIE_SAME_SITE (Optional[bytes]): None - CORS directive.
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from bareutils.cookies import encode_set_cookie

SESSION_COOKIE_NAME: bytes = b'bareASGI-session'


class SessionCookieFactory:
    """Session cookie factory"""

    def __init__(
            self,
            name: bytes = SESSION_COOKIE_NAME,
            expires: Optional[datetime] = None,
            max_age: Optional[Union[int, timedelta]] = None,
            path: Optional[bytes] = None,
            domain: Optional[bytes] = None,
            secure: bool = False,
            http_only: bool = False,
            same_site: Optional[bytes] = None
    ) -> None:
        """A session cookie factory.

        Args:
            name ([type], optional): The session cookie name. Defaults to
                SESSION_COOKIE_NAME.
            expires (Optional[datetime], optional): The session cookie expiry.
                Defaults to None.
            max_age (Optional[Union[int, timedelta]], optional): The maximum age
                of the session cookie. Defaults to None.
            path (Optional[bytes], optional): The session cookie path. Defaults
                to None.
            domain (Optional[bytes], optional): The session cookie domain.
                Defaults to None.
            secure (bool, optional): Indicates whether the cookie should be sent
                over https only. Defaults to False.
            http_only (bool, optional): Indicates whether the session cookie is
                available to JavaScript in the browser. Defaults to
                False.
            same_site (Optional[bytes], optional): CORS directive. Defaults to
                None.
        """
        self.name = name
        self.expires = expires
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    def create_cookie(self, key: str, host: bytes) -> bytes:
        """Creates the 'set-cookie' header value

        Args:
            key (str): The session key

        Returns:
            bytes: The set-cookie header value.
        """
        return encode_set_cookie(
            self.name,
            key.encode('ascii'),
            expires=self.expires,
            max_age=self.max_age,
            path=self.path,
            domain=self.domain or host,
            secure=self.secure,
            http_only=self.http_only,
            same_site=self.same_site
        )
