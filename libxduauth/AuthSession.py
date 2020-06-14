import http.cookiejar
import os

from requests import Session


# noinspection PyTypeChecker
class AuthSession(Session):
    def __init__(self, filename, cookies={}, headers={}):
        self.cookie_path = os.path.expanduser(
            os.path.join('~', '.xduauth', 'cookies', filename)
        )
        os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)
        if not cookies and hasattr(self, 'cookies'):
            cookies = self.cookies
        super().__init__()
        self.cookies = http.cookiejar.LWPCookieJar(self.cookie_path)

        for cookie in cookies:
            self.cookies.set_cookie(cookie)
        self.headers.update(headers)

        if not os.path.exists(self.cookie_path):
            self.cookies.save(ignore_discard=True)
        self.cookies.load(ignore_discard=True)

    def request(self, *args, **kwargs):
        ret = super().request(*args, **kwargs)
        self.cookies.save(ignore_discard=True)
        return ret
